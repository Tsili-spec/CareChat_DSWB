const logger = require('../utils/logger');

/**
 * Global error handling middleware for API Gateway
 */
const errorHandler = (err, req, res, next) => {
  // Log the error
  logger.error('Unhandled error:', {
    error: err.message,
    stack: err.stack,
    url: req.originalUrl,
    method: req.method,
    userId: req.user?.userId,
    correlationId: req.correlationId,
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });

  // Default error response
  let statusCode = 500;
  let errorResponse = {
    error: 'Internal Server Error',
    message: 'An unexpected error occurred',
    timestamp: new Date().toISOString(),
    correlationId: req.correlationId
  };

  // Handle specific error types
  if (err.name === 'ValidationError') {
    statusCode = 400;
    errorResponse = {
      error: 'Validation Error',
      message: err.message,
      details: err.details || null,
      timestamp: new Date().toISOString(),
      correlationId: req.correlationId
    };
  } else if (err.name === 'UnauthorizedError') {
    statusCode = 401;
    errorResponse = {
      error: 'Unauthorized',
      message: 'Authentication failed',
      timestamp: new Date().toISOString(),
      correlationId: req.correlationId
    };
  } else if (err.name === 'ForbiddenError') {
    statusCode = 403;
    errorResponse = {
      error: 'Forbidden',
      message: 'Access denied',
      timestamp: new Date().toISOString(),
      correlationId: req.correlationId
    };
  } else if (err.name === 'NotFoundError') {
    statusCode = 404;
    errorResponse = {
      error: 'Not Found',
      message: err.message || 'Resource not found',
      timestamp: new Date().toISOString(),
      correlationId: req.correlationId
    };
  } else if (err.code === 'ECONNREFUSED' || err.code === 'ENOTFOUND') {
    statusCode = 502;
    errorResponse = {
      error: 'Service Unavailable',
      message: 'Unable to connect to downstream service',
      timestamp: new Date().toISOString(),
      correlationId: req.correlationId
    };
  } else if (err.code === 'ETIMEDOUT') {
    statusCode = 504;
    errorResponse = {
      error: 'Gateway Timeout',
      message: 'Downstream service did not respond in time',
      timestamp: new Date().toISOString(),
      correlationId: req.correlationId
    };
  }

  // Don't expose sensitive error details in production
  if (process.env.NODE_ENV === 'production') {
    delete errorResponse.stack;
    if (statusCode === 500) {
      errorResponse.message = 'An unexpected error occurred';
    }
  } else {
    // Include stack trace in development
    errorResponse.stack = err.stack;
  }

  res.status(statusCode).json(errorResponse);
};

/**
 * Async error wrapper to catch promises that reject
 */
const asyncHandler = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

/**
 * Custom error classes
 */
class ValidationError extends Error {
  constructor(message, details = null) {
    super(message);
    this.name = 'ValidationError';
    this.details = details;
  }
}

class UnauthorizedError extends Error {
  constructor(message = 'Authentication required') {
    super(message);
    this.name = 'UnauthorizedError';
  }
}

class ForbiddenError extends Error {
  constructor(message = 'Access denied') {
    super(message);
    this.name = 'ForbiddenError';
  }
}

class NotFoundError extends Error {
  constructor(message = 'Resource not found') {
    super(message);
    this.name = 'NotFoundError';
  }
}

module.exports = {
  errorHandler,
  asyncHandler,
  ValidationError,
  UnauthorizedError,
  ForbiddenError,
  NotFoundError
};
