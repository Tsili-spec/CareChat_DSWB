from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Configuration settings loaded from environment variables"""
    
    def __init__(self):
        # App Info
        self.APP_NAME = os.getenv("APP_NAME", "CareChat API Gateway")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        
        # API Configuration
        self.API_V1_STR = os.getenv("API_V1_STR", "/api/v1")
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))
        
        # Security
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "11520"))  # 8 days
        self.REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "43200"))  # 30 days
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        
        # CORS - Parse from comma-separated string
        cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "*")
        if cors_origins == "*":
            self.BACKEND_CORS_ORIGINS = ["*"]
        else:
            self.BACKEND_CORS_ORIGINS = [origin.strip() for origin in cors_origins.split(",")]
        
        # MongoDB Configuration
        self.MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017")
        self.MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "carechat_patient_system")
        
        # PostgreSQL Configuration (for Track3)
        self.TRACK3_DATABASE_URL = os.getenv("TRACK3_DATABASE_URL", "postgresql://postgres:carechat123@localhost:5432/track3_db")
        
        # Microservice URLs
        self.TRACK1_SERVICE_URL = os.getenv("TRACK1_SERVICE_URL", "http://localhost:3001")
        self.TRACK2_SERVICE_URL = os.getenv("TRACK2_SERVICE_URL", "http://localhost:3002")
        self.TRACK3_SERVICE_URL = os.getenv("TRACK3_SERVICE_URL", "http://localhost:3003")
        
        # Legacy backend URLs (for compatibility)
        self.TRACK1_BACKEND_URL = os.getenv("TRACK1_BACKEND_URL", self.TRACK1_SERVICE_URL)
        self.TRACK2_BACKEND_URL = os.getenv("TRACK2_BACKEND_URL", self.TRACK2_SERVICE_URL)
        self.TRACK3_BACKEND_URL = os.getenv("TRACK3_BACKEND_URL", self.TRACK3_SERVICE_URL)
        
        # Redis Configuration
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # AI/LLM Configuration
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
        
        # Notification Services
        self.TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
        self.TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
        self.TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Email Configuration
        self.SMTP_HOST = os.getenv("SMTP_HOST")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USER = os.getenv("SMTP_USER")
        self.SMTP_PASS = os.getenv("SMTP_PASS")
        self.SMTP_TLS = os.getenv("SMTP_TLS", "true").lower() == "true"
        
        # Rate Limiting
        self.RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        self.RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "100"))
        
        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE")
        
        # Environment
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


# Create settings instance
settings = Settings()


# Configuration for different environments
def get_database_url() -> str:
    """Get the appropriate database URL based on environment"""
    return settings.MONGODB_URL


def get_cors_origins() -> List[str]:
    """Get CORS origins for the current environment"""
    if settings.ENVIRONMENT == "production":
        return [
            "https://carechat.com",
            "https://www.carechat.com",
            "https://admin.carechat.com"
        ]
    return settings.BACKEND_CORS_ORIGINS


def is_development() -> bool:
    """Check if running in development mode"""
    return settings.ENVIRONMENT == "development"


def is_production() -> bool:
    """Check if running in production mode"""
    return settings.ENVIRONMENT == "production"
