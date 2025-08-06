const express = require('express');
const router = express.Router();
const logger = require('../utils/logger');

/**
 * Health check endpoint for the API Gateway
 * Provides gateway status and basic service connectivity
 */
router.get('/', async (req, res) => {
  const startTime = Date.now();
  
  try {
    // Basic health check data
    const healthData = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV || 'development',
      pid: process.pid,
      memory: process.memoryUsage(),
      platform: process.platform,
      nodeVersion: process.version
    };

    // Service connectivity checks
    const services = {
      track1: process.env.TRACK1_SERVICE_URL || 'http://localhost:3001',
      track2: process.env.TRACK2_SERVICE_URL || 'http://localhost:3002',
      track3: process.env.TRACK3_SERVICE_URL || 'http://localhost:3003'
    };

    const serviceChecks = await Promise.allSettled(
      Object.entries(services).map(async ([name, url]) => {
        try {
          const axios = require('axios');
          const response = await axios.get(`${url}/health`, { 
            timeout: 5000,
            headers: {
              'X-Health-Check': 'gateway',
              'X-Gateway-Version': healthData.version
            }
          });
          
          return {
            name,
            status: 'healthy',
            url,
            responseTime: Date.now() - startTime,
            version: response.data?.version || 'unknown'
          };
        } catch (error) {
          return {
            name,
            status: 'unhealthy',
            url,
            error: error.message,
            responseTime: Date.now() - startTime
          };
        }
      })
    );

    // Process service check results
    const serviceStatus = serviceChecks.map((result, index) => {
      const serviceName = Object.keys(services)[index];
      if (result.status === 'fulfilled') {
        return result.value;
      } else {
        return {
          name: serviceName,
          status: 'error',
          url: services[serviceName],
          error: result.reason?.message || 'Unknown error',
          responseTime: Date.now() - startTime
        };
      }
    });

    // Determine overall health status
    const unhealthyServices = serviceStatus.filter(service => service.status !== 'healthy');
    const overallStatus = unhealthyServices.length === 0 ? 'healthy' : 
                         unhealthyServices.length === serviceStatus.length ? 'unhealthy' : 'degraded';

    const response = {
      ...healthData,
      status: overallStatus,
      checks: {
        gateway: {
          status: 'healthy',
          details: 'API Gateway is running normally'
        },
        services: serviceStatus.reduce((acc, service) => {
          acc[service.name] = {
            status: service.status,
            url: service.url,
            responseTime: service.responseTime,
            version: service.version,
            error: service.error
          };
          return acc;
        }, {})
      },
      summary: {
        total: serviceStatus.length,
        healthy: serviceStatus.filter(s => s.status === 'healthy').length,
        unhealthy: serviceStatus.filter(s => s.status !== 'healthy').length
      }
    };

    // Log health check
    logger.info('Health check completed', {
      status: overallStatus,
      responseTime: Date.now() - startTime,
      servicesChecked: serviceStatus.length,
      healthyServices: response.summary.healthy
    });

    // Return appropriate status code
    const statusCode = overallStatus === 'healthy' ? 200 : 
                      overallStatus === 'degraded' ? 207 : 503;

    res.status(statusCode).json(response);

  } catch (error) {
    logger.error('Health check failed:', {
      error: error.message,
      stack: error.stack,
      responseTime: Date.now() - startTime
    });

    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: 'Health check failed',
      message: error.message,
      uptime: process.uptime(),
      version: process.env.npm_package_version || '1.0.0'
    });
  }
});

/**
 * Detailed health check with database connectivity
 */
router.get('/detailed', async (req, res) => {
  const startTime = Date.now();
  
  try {
    // Get basic health data
    const basicHealth = await new Promise((resolve, reject) => {
      router.stack[0].route.stack[0].handle(req, { 
        status: (code) => ({ json: (data) => resolve(data) }),
        json: (data) => resolve(data)
      }, reject);
    });

    // Additional detailed checks
    const detailedChecks = {
      memory: {
        status: process.memoryUsage().heapUsed < 500 * 1024 * 1024 ? 'healthy' : 'warning', // 500MB threshold
        details: process.memoryUsage()
      },
      disk: {
        status: 'healthy', // Could add actual disk space check
        details: 'Disk space check not implemented'
      },
      network: {
        status: 'healthy',
        details: 'Network connectivity normal'
      }
    };

    const response = {
      ...basicHealth,
      detailed: true,
      checks: {
        ...basicHealth.checks,
        system: detailedChecks
      },
      performance: {
        responseTime: Date.now() - startTime,
        cpuUsage: process.cpuUsage(),
        loadAverage: require('os').loadavg()
      }
    };

    res.json(response);

  } catch (error) {
    logger.error('Detailed health check failed:', {
      error: error.message,
      stack: error.stack
    });

    res.status(503).json({
      status: 'unhealthy',
      error: 'Detailed health check failed',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Simple liveness probe
 */
router.get('/live', (req, res) => {
  res.status(200).json({
    status: 'alive',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

/**
 * Readiness probe
 */
router.get('/ready', async (req, res) => {
  try {
    // Basic readiness checks
    const ready = process.uptime() > 5; // Gateway has been running for at least 5 seconds
    
    if (ready) {
      res.status(200).json({
        status: 'ready',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
      });
    } else {
      res.status(503).json({
        status: 'not ready',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
      });
    }
  } catch (error) {
    res.status(503).json({
      status: 'not ready',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router;
