from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.api import feedback, reminder, patient, dashboard
from app.db.database import connect_to_mongo, close_mongo_connection
from app.services.sms_service import sms_service
from app.services.reminder_scheduler import reminder_scheduler
import time
import os
import asyncio
from contextlib import asynccontextmanager

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Create upload directory if it doesn't exist
if not os.path.exists("upload"):
    os.makedirs("upload")

# Setup logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting CareChat API...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    logger.info("✅ Database initialization completed")
    
    # Check SMS service configuration
    if sms_service.is_configured():
        logger.info("✅ SMS service configured successfully")
        logger.info(f"   Twilio Account: {sms_service.account_sid[:10]}...")
        logger.info(f"   Twilio Number: {sms_service.twilio_number}")
    else:
        logger.warning("⚠️  SMS service not configured - check environment variables")
        logger.warning("   Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER, MY_NUMBER")
    
    # Note: Scheduler is started manually via API endpoint for better control
    logger.info("📅 Reminder scheduler ready (start via /api/reminder/start-scheduler)")
    logger.info("🎉 CareChat API startup complete!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down CareChat API...")
    
    # Stop reminder scheduler if running
    if reminder_scheduler.is_running:
        reminder_scheduler.stop_scheduler()
        logger.info("📅 Reminder scheduler stopped")
    
    # Close database connection
    await close_mongo_connection()
    
    logger.info("👋 CareChat API shutdown complete!")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan
)

# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url}")
    
    # Log request body for non-GET requests (be careful with sensitive data)
    if request.method != "GET":
        try:
            # Only log content type, not actual body for security
            content_type = request.headers.get("content-type", "unknown")
            logger.info(f"Request Content-Type: {content_type}")
        except Exception:
            logger.info("Request Body: (Unable to parse)")

    # Process the request
    response = await call_next(request)
    
    # Log response details
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Response Status: {response.status_code}")
    logger.info(f"Response Time: {process_time:.2f}ms")
    
    return response

@app.get("/",
         summary="Root endpoint",
         description="Welcome message and API information")
def root():
    """
    Welcome endpoint providing API information.
    
    **Response:** Welcome message with available services
    """
    return {
        "message": "Welcome to CareChat API! Available services: Feedback, Reminder, Patient Management.",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health",
         summary="Health check endpoint",
         description="Check API health status")
def health_check():
    """
    Health check endpoint.
    
    **Response:** Health status information
    """
    return {
        "status": "OK",
        "message": "CareChat Backend is running",
        "version": settings.VERSION,
        "timestamp": time.time()
    }

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(feedback.router, prefix="/api", tags=["Feedback"])
app.include_router(reminder.router, prefix="/api", tags=["Reminder"])
app.include_router(patient.router, prefix="/api", tags=["Patient"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
