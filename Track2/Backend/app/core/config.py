# Environment variables & settings
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "refreshsecret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# LLM Configuration - Gemini Only
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
