require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const { MongoClient } = require('mongodb');

const logger = require('./utils/logger');
const errorHandler = require('./middleware/errorHandler');
const authMiddleware = require('./middleware/auth');

// Route imports
const healthRoutes = require('./routes/health');
const feedbackRoutes = require('./routes/feedback');
const reminderRoutes = require('./routes/reminders');
const analyticsRoutes = require('./routes/analytics');
const patientRoutes = require('./routes/patients');

const app = express();
const PORT = process.env.PORT || 3001;

// MongoDB connection
let db;
const mongoUrl = process.env.MONGODB_URL || 'mongodb://localhost:27017';
const dbName = process.env.MONGODB_DATABASE || 'carechat_unified';

// Connect to MongoDB
MongoClient.connect(mongoUrl)
  .then(client => {
    db = client.db(dbName);
    app.locals.db = db;
    logger.info('Connected to MongoDB successfully');
  })
  .catch(error => {
    logger.error('MongoDB connection failed:', error);
    process.exit(1);
  });

// Trust proxy for rate limiting behind load balancer
app.set('trust proxy', 1);

// Basic middleware
app.use(helmet());
app.use(compression());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
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
  max: 500, // Limit each IP to 500 requests per windowMs
  message: {
    error: 'Too many requests',
    retryAfter: '15 minutes'
  }
});
app.use(limiter);

// Add request ID and timing
app.use((req, res, next) => {
  req.requestId = require('uuid').v4();
  req.startTime = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - req.startTime;
    logger.request(req, res, duration);
  });
  
  next();
});

// Routes
app.use('/health', healthRoutes);
app.use('/feedback', authMiddleware, feedbackRoutes);
app.use('/reminders', authMiddleware, reminderRoutes);
app.use('/analytics', authMiddleware, analyticsRoutes);
app.use('/patients', authMiddleware, patientRoutes);

// Default route
app.get('/', (req, res) => {
  res.json({
    service: 'CareChat Track1 Service',
    version: process.env.npm_package_version || '1.0.0',
    description: 'Feedback Analysis & Reminders Microservice',
    database: 'MongoDB',
    endpoints: {
      health: '/health',
      feedback: '/feedback',
      reminders: '/reminders',
      analytics: '/analytics',
      patients: '/patients'
    },
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.originalUrl} not found`,
    service: 'track1-service'
  });
});

// Error handling
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
  logger.info(`Track1 Service running on port ${PORT}`);
  logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
});

module.exports = app;
