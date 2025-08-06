require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const { createProxyMiddleware } = require('http-proxy-middleware');
const swaggerUi = require('swagger-ui-express');
const winston = require('winston');

const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');
const healthCheck = require('./routes/health');
const authRoutes = require('./routes/auth');
const swaggerSpec = require('./config/swagger');
const logger = require('./utils/logger');

const app = express();
const PORT = process.env.PORT || 3000;

// Trust proxy for rate limiting behind load balancer
app.set('trust proxy', 1);

// Basic middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

app.use(compression());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true,
  optionsSuccessStatus: 200
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Logging
app.use(morgan('combined', {
  stream: { write: message => logger.info(message.trim()) }
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000, // Limit each IP to 1000 requests per windowMs
  message: {
    error: 'Too many requests from this IP, please try again later.',
    retryAfter: '15 minutes'
  },
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// API Documentation
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Health check and auth routes (handled by gateway)
app.use('/api/health', healthCheck);
app.use('/api/auth', authRoutes);

// Service configurations
const services = {
  track1: {
    target: process.env.TRACK1_SERVICE_URL || 'http://localhost:3001',
    changeOrigin: true,
    pathRewrite: {
      '^/api/track1': ''
    },
    timeout: 30000,
    retries: 3
  },
  track2: {
    target: process.env.TRACK2_SERVICE_URL || 'http://localhost:3002',
    changeOrigin: true,
    pathRewrite: {
      '^/api/track2': ''
    },
    timeout: 30000,
    retries: 3
  },
  track3: {
    target: process.env.TRACK3_SERVICE_URL || 'http://localhost:3003',
    changeOrigin: true,
    pathRewrite: {
      '^/api/track3': ''
    },
    timeout: 30000,
    retries: 3
  }
};

// Custom proxy options with enhanced error handling and logging
const createProxy = (serviceName, config) => {
  return createProxyMiddleware({
    ...config,
    onProxyReq: (proxyReq, req, res) => {
      logger.info(`Proxying ${req.method} ${req.originalUrl} to ${serviceName}`);
      
      // Add correlation ID for request tracking
      const correlationId = req.correlationId || require('uuid').v4();
      proxyReq.setHeader('X-Correlation-ID', correlationId);
      proxyReq.setHeader('X-Gateway-Timestamp', new Date().toISOString());
      
      // Forward user info if authenticated
      if (req.user) {
        proxyReq.setHeader('X-User-ID', req.user.userId);
        proxyReq.setHeader('X-User-Type', req.user.userType);
        proxyReq.setHeader('X-Track-Origin', req.user.trackOrigin);
      }
    },
    onProxyRes: (proxyRes, req, res) => {
      logger.info(`Response from ${serviceName}: ${proxyRes.statusCode} for ${req.originalUrl}`);
      
      // Add CORS headers if needed
      proxyRes.headers['Access-Control-Allow-Origin'] = req.headers.origin || '*';
      proxyRes.headers['Access-Control-Allow-Credentials'] = 'true';
    },
    onError: (err, req, res) => {
      logger.error(`Proxy error for ${serviceName}:`, {
        error: err.message,
        url: req.originalUrl,
        method: req.method,
        stack: err.stack
      });
      
      res.status(502).json({
        error: 'Service Unavailable',
        message: `${serviceName} service is currently unavailable`,
        timestamp: new Date().toISOString(),
        correlationId: req.correlationId
      });
    }
  });
};

// Track 1 Service Routes (Feedback & Reminders) - MongoDB
app.use('/api/track1/feedback', authMiddleware, createProxy('track1-feedback', services.track1));
app.use('/api/track1/reminders', authMiddleware, createProxy('track1-reminders', services.track1));
app.use('/api/track1/patients', authMiddleware, createProxy('track1-patients', services.track1));
app.use('/api/track1/analytics', authMiddleware, createProxy('track1-analytics', services.track1));

// Track 2 Service Routes (Chat & AI) - MongoDB  
app.use('/api/track2/chat', authMiddleware, createProxy('track2-chat', services.track2));
app.use('/api/track2/conversations', authMiddleware, createProxy('track2-conversations', services.track2));
app.use('/api/track2/ai', authMiddleware, createProxy('track2-ai', services.track2));
app.use('/api/track2/users', authMiddleware, createProxy('track2-users', services.track2));

// Track 3 Service Routes (Blood Management) - PostgreSQL
app.use('/api/track3/blood', authMiddleware, createProxy('track3-blood', services.track3));
app.use('/api/track3/collections', authMiddleware, createProxy('track3-collections', services.track3));
app.use('/api/track3/usage', authMiddleware, createProxy('track3-usage', services.track3));
app.use('/api/track3/stock', authMiddleware, createProxy('track3-stock', services.track3));

// Unified routes that aggregate data from multiple services
app.use('/api/unified', authMiddleware, require('./routes/unified'));

// Service discovery endpoint
app.get('/api/services', authMiddleware, (req, res) => {
  const serviceStatus = Object.entries(services).map(([name, config]) => ({
    name,
    url: config.target,
    status: 'unknown', // Could be enhanced with health checks
    version: '1.0.0'
  }));
  
  res.json({
    gateway: {
      version: process.env.npm_package_version || '1.0.0',
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    },
    services: serviceStatus
  });
});

// Default route
app.get('/', (req, res) => {
  res.json({
    name: 'CareChat API Gateway',
    version: process.env.npm_package_version || '1.0.0',
    description: 'Unified API Gateway for CareChat Microservices',
    documentation: '/api-docs',
    health: '/api/health',
    services: '/api/services',
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.originalUrl} not found`,
    timestamp: new Date().toISOString()
  });
});

// Error handling middleware
app.use(errorHandler);

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});

// Start server
app.listen(PORT, () => {
  logger.info(`CareChat API Gateway running on port ${PORT}`);
  logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
  logger.info(`API Documentation: http://localhost:${PORT}/api-docs`);
});

module.exports = app;
