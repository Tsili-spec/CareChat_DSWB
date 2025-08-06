const jwt = require('jsonwebtoken');
const logger = require('../utils/logger');

/**
 * Authentication middleware for API Gateway
 * Validates JWT tokens and sets user context
 */
const authMiddleware = async (req, res, next) => {
  try {
    // Extract token from header
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'No token provided or invalid format',
        expectedFormat: 'Authorization: Bearer <token>'
      });
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix

    try {
      // Verify JWT token
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'carechat-secret-key');
      
      // Set user context for downstream services
      req.user = {
        userId: decoded.userId,
        userType: decoded.userType, // 'patient', 'user', 'admin'
        trackOrigin: decoded.trackOrigin, // 'track1', 'track2', 'track3'
        permissions: decoded.permissions || [],
        email: decoded.email,
        phoneNumber: decoded.phoneNumber,
        fullName: decoded.fullName,
        isVerified: decoded.isVerified || false,
        exp: decoded.exp,
        iat: decoded.iat
      };

      // Add correlation ID for request tracking
      req.correlationId = require('uuid').v4();

      // Log authentication success
      logger.info('Authentication successful', {
        userId: req.user.userId,
        userType: req.user.userType,
        trackOrigin: req.user.trackOrigin,
        endpoint: req.originalUrl,
        method: req.method,
        correlationId: req.correlationId,
        ip: req.ip
      });

      next();
    } catch (jwtError) {
      if (jwtError.name === 'TokenExpiredError') {
        return res.status(401).json({
          error: 'Token Expired',
          message: 'Your session has expired. Please log in again.',
          expiredAt: jwtError.expiredAt
        });
      }

      if (jwtError.name === 'JsonWebTokenError') {
        return res.status(401).json({
          error: 'Invalid Token',
          message: 'The provided token is invalid or malformed.'
        });
      }

      throw jwtError; // Re-throw unexpected errors
    }

  } catch (error) {
    logger.error('Authentication error:', {
      error: error.message,
      stack: error.stack,
      endpoint: req.originalUrl,
      method: req.method,
      ip: req.ip
    });

    res.status(500).json({
      error: 'Authentication Error',
      message: 'An error occurred during authentication'
    });
  }
};

/**
 * Optional authentication middleware
 * Allows both authenticated and anonymous requests
 */
const optionalAuth = async (req, res, next) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    // No token provided, continue without user context
    req.user = null;
    req.correlationId = require('uuid').v4();
    return next();
  }

  // Token provided, validate it
  return authMiddleware(req, res, next);
};

/**
 * Role-based authorization middleware
 * Requires specific user types or permissions
 */
const authorize = (allowedRoles = [], requiredPermissions = []) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Authentication Required',
        message: 'This endpoint requires authentication'
      });
    }

    // Check user type/role
    if (allowedRoles.length > 0 && !allowedRoles.includes(req.user.userType)) {
      logger.warn('Authorization failed - insufficient role', {
        userId: req.user.userId,
        userType: req.user.userType,
        requiredRoles: allowedRoles,
        endpoint: req.originalUrl
      });

      return res.status(403).json({
        error: 'Insufficient Permissions',
        message: `This endpoint requires one of the following roles: ${allowedRoles.join(', ')}`,
        userRole: req.user.userType
      });
    }

    // Check specific permissions
    if (requiredPermissions.length > 0) {
      const userPermissions = req.user.permissions || [];
      const hasPermission = requiredPermissions.every(permission => 
        userPermissions.includes(permission)
      );

      if (!hasPermission) {
        logger.warn('Authorization failed - insufficient permissions', {
          userId: req.user.userId,
          userPermissions,
          requiredPermissions,
          endpoint: req.originalUrl
        });

        return res.status(403).json({
          error: 'Insufficient Permissions',
          message: `This endpoint requires the following permissions: ${requiredPermissions.join(', ')}`,
          userPermissions
        });
      }
    }

    next();
  };
};

/**
 * Track-specific authorization
 * Ensures users can only access their originating track's data
 */
const trackAuth = (allowedTracks = []) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Authentication Required',
        message: 'This endpoint requires authentication'
      });
    }

    if (allowedTracks.length > 0 && !allowedTracks.includes(req.user.trackOrigin)) {
      logger.warn('Track authorization failed', {
        userId: req.user.userId,
        userTrack: req.user.trackOrigin,
        allowedTracks,
        endpoint: req.originalUrl
      });

      return res.status(403).json({
        error: 'Track Access Denied',
        message: `Users from ${req.user.trackOrigin} cannot access this resource`,
        allowedTracks
      });
    }

    next();
  };
};

module.exports = {
  authMiddleware,
  optionalAuth,
  authorize,
  trackAuth
};
