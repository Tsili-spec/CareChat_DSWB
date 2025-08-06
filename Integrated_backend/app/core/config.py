from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List
import os

load_dotenv()

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
    JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY", "your-super-secret-refresh-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]
    
    # Twilio Configuration (for SMS)
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_NUMBER: str = os.getenv("TWILIO_NUMBER", "")
    MY_NUMBER: str = os.getenv("MY_NUMBER", "")
    
    # LLM API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Application Settings
    PROJECT_NAME: str = "CareChat API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for patient reminders and feedback system with SMS notifications."

settings = Settings()
