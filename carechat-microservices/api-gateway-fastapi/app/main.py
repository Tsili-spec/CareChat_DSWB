from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from app.core.config import settings, get_cors_origins
from app.db.database import connect_to_mongo, close_mongo_connection
from app.api.v1.api import api_router


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting CareChat API Gateway...")
    await connect_to_mongo()
    
    # Initialize LLM service
    try:
        from app.services.llm_service import llm_service
        await llm_service.initialize_rag()
        logger.info("✅ LLM service initialized")
    except Exception as e:
        logger.warning(f"⚠️ LLM service initialization failed: {e}")
    
    logger.info("✅ API Gateway startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CareChat API Gateway...")
    await close_mongo_connection()
    logger.info("✅ API Gateway shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Unified API Gateway for CareChat Microservices Architecture",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add security headers middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] if settings.DEBUG else ["carechat.com", "*.carechat.com", "localhost", "127.0.0.1", "localhost:8000", "127.0.0.1:8000"]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"{response.status_code} - {process_time:.4f}s"
    )
    
    return response


# Add request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None)
        }
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "🏥 Welcome to CareChat API Gateway",
        "description": "Unified API Gateway for CareChat microservices with MongoDB integration",
        "version": settings.APP_VERSION,
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "features": [
            "🔐 JWT Authentication & Authorization",
            "👥 User Management & Profiles",
            "💬 Conversation Management",
            "📝 Feedback Collection & Analytics",
            "⏰ Smart Reminders System",
            "📊 System Analytics & Monitoring",
            "🗄️ MongoDB Integration"
        ],
        "api_info": {
            "base_url": settings.API_V1_STR,
            "documentation": "/docs",
            "redoc": "/redoc",
            "health_check": "/health"
        },
        "microservices": {
            "track1_backend": settings.TRACK1_SERVICE_URL,
            "track2_backend": settings.TRACK2_SERVICE_URL
        },
        "database": {
            "type": "MongoDB",
            "database": settings.MONGODB_DATABASE,
            "collections": [
                "users",
                "conversations", 
                "feedback_sessions",
                "smart_reminders",
                "reminder_deliveries",
                "notification_templates",
                "system_analytics",
                "system_audit_log"
            ]
        },
        "endpoints": {
            "authentication": f"{settings.API_V1_STR}/auth",
            "users": f"{settings.API_V1_STR}/users",
            "conversations": f"{settings.API_V1_STR}/conversations", 
            "feedback": f"{settings.API_V1_STR}/feedback",
            "reminders": f"{settings.API_V1_STR}/reminders",
            "analytics": f"{settings.API_V1_STR}/analytics"
        },
        "getting_started": {
            "1": "📖 View API documentation at /docs",
            "2": "🔐 Register a new user at /api/v1/auth/register",
            "3": "🔑 Login to get JWT token at /api/v1/auth/login", 
            "4": "🚀 Start using the API endpoints with your token"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # You can add more health checks here (database, redis, etc.)
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Metrics endpoint (for monitoring)
@app.get("/metrics")
async def metrics():
    # Basic metrics - you can expand this with proper monitoring
    return {
        "requests_total": "N/A",  # Would need proper tracking
        "response_time_avg": "N/A",
        "error_rate": "N/A",
        "uptime": time.time(),
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
