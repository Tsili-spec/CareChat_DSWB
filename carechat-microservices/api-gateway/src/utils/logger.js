const winston = require('winston');
const path = require('path');

// Define custom log levels and colors
const logLevels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4
};

const logColors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'blue'
};

winston.addColors(logColors);

// Custom log format
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.json(),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    // Format log message with metadata
    const metaStr = Object.keys(meta).length > 0 ? JSON.stringify(meta, null, 2) : '';
    return `${timestamp} [${level.toUpperCase()}]: ${message} ${metaStr}`;
  })
);

// Console format for development
const consoleFormat = winston.format.combine(
  winston.format.colorize({ all: true }),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    const metaStr = Object.keys(meta).length > 0 ? JSON.stringify(meta, null, 2) : '';
    return `${timestamp} [${level}]: ${message} ${metaStr}`;
  })
);

// Create logger instance
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  levels: logLevels,
  format: logFormat,
  defaultMeta: {
    service: 'carechat-api-gateway',
    environment: process.env.NODE_ENV || 'development',
    version: process.env.npm_package_version || '1.0.0'
  },
  transports: [
    // Console transport for development
    new winston.transports.Console({
      format: process.env.NODE_ENV === 'production' ? logFormat : consoleFormat,
      silent: process.env.NODE_ENV === 'test'
    }),

    // File transport for errors
    new winston.transports.File({
      filename: path.join(process.cwd(), 'logs', 'error.log'),
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      tailable: true
    }),

    // File transport for all logs
    new winston.transports.File({
      filename: path.join(process.cwd(), 'logs', 'combined.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 10,
      tailable: true
    })
  ],

  // Handle uncaught exceptions and rejections
  exceptionHandlers: [
    new winston.transports.File({
      filename: path.join(process.cwd(), 'logs', 'exceptions.log')
    })
  ],

  rejectionHandlers: [
    new winston.transports.File({
      filename: path.join(process.cwd(), 'logs', 'rejections.log')
    })
  ]
});

// Enhanced logging methods with context
const contextLogger = {
  error: (message, meta = {}) => {
    logger.error(message, { ...meta, timestamp: new Date().toISOString() });
  },

  warn: (message, meta = {}) => {
    logger.warn(message, { ...meta, timestamp: new Date().toISOString() });
  },

  info: (message, meta = {}) => {
    logger.info(message, { ...meta, timestamp: new Date().toISOString() });
  },

  http: (message, meta = {}) => {
    logger.http(message, { ...meta, timestamp: new Date().toISOString() });
  },

  debug: (message, meta = {}) => {
    logger.debug(message, { ...meta, timestamp: new Date().toISOString() });
  },

  // Specific method for request logging
  request: (req, res, duration) => {
    const logData = {
      method: req.method,
      url: req.originalUrl,
      status: res.statusCode,
      duration: `${duration}ms`,
      userAgent: req.get('User-Agent'),
      ip: req.ip,
      userId: req.user?.userId,
      correlationId: req.correlationId,
      contentLength: res.get('Content-Length'),
      timestamp: new Date().toISOString()
    };

    if (res.statusCode >= 400) {
      logger.warn('HTTP Request Error', logData);
    } else {
      logger.http('HTTP Request', logData);
    }
  },

  // Method for security events
  security: (event, details = {}) => {
    logger.warn(`SECURITY: ${event}`, {
      ...details,
      timestamp: new Date().toISOString(),
      severity: 'security'
    });
  },

  // Method for performance monitoring
  performance: (operation, duration, details = {}) => {
    const logData = {
      operation,
      duration: `${duration}ms`,
      ...details,
      timestamp: new Date().toISOString(),
      type: 'performance'
    };

    if (duration > 5000) { // Warn if operation takes more than 5 seconds
      logger.warn(`Slow operation: ${operation}`, logData);
    } else {
      logger.info(`Performance: ${operation}`, logData);
    }
  }
};

// Create logs directory if it doesn't exist
const fs = require('fs');
const logsDir = path.join(process.cwd(), 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

module.exports = contextLogger;
