from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.blood_bank import router as blood_bank_router
from app.db.database import Base, engine, check_database_health
from app.models.user import User
from app.models.blood_collection import BloodCollection
from app.models.blood_usage import BloodUsage
from app.models.blood_stock import BloodStock
from app.admin.config import configure_admin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

# Create FastAPI app with organized tags
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-Enhanced Blood Bank Stock Monitoring and Forecasting System - 3-Table Architecture",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints"
        },
        {
            "name": "Blood Bank Management", 
            "description": "Blood collection, usage, and stock management endpoints"
        },
        {
            "name": "System",
            "description": "System health and status monitoring endpoints"
        }
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper tags
app.include_router(auth_router, prefix=settings.API_V1_STR, tags=["Authentication"])
app.include_router(blood_bank_router, prefix=settings.API_V1_STR, tags=["Blood Bank Management"])

# Configure admin interface (must be done before startup events)
configure_admin(app)
logger.info("Admin interface configured successfully")

@app.get("/", tags=["System"])
def read_root():
    """Root endpoint - Welcome message"""
    return {
        "message": "Welcome to Blood Bank Management System API",
        "version": settings.VERSION,
        "architecture": "3-Table Blood Bank System (Collections, Usage, Stock)",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint - System and database status"""
    db_healthy = await check_database_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "version": settings.VERSION,
        "schema": "blood_collections, blood_usage, blood_stock, users"
    }




