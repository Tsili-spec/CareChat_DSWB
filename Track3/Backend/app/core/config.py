from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import secrets
from pathlib import Path

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Blood Bank Management System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY: str = Field(..., env="JWT_REFRESH_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # DHIS2 Integration
    DHIS2_BASE_URL: str = "https://play.dhis2.org/2.39.1.1"
    DHIS2_USERNAME: str = "admin"
    DHIS2_PASSWORD: str = "district"
    DHIS2_SYNC_INTERVAL_MINUTES: int = 30
    
    # Machine Learning
    ML_MODEL_PATH: str = "ml_models/saved_models/"
    MODEL_RETRAIN_INTERVAL_HOURS: int = 24
    FORECAST_HORIZON_DAYS: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [*]
    
    # File Storage
    UPLOAD_DIR: str = "uploads/"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Blood Bank Specific
    DEFAULT_BLOOD_SHELF_LIFE_DAYS: int = 42
    LOW_STOCK_THRESHOLD_ML: int = 5000
    CRITICAL_STOCK_THRESHOLD_ML: int = 2000
    
    # Notifications
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    ENABLE_SMS_NOTIFICATIONS: bool = False
    
    # Optional Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Optional External API Keys
    WEATHER_API_KEY: Optional[str] = None
    SMS_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields

settings = Settings()
