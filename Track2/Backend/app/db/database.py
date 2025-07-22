# DB session management (PostgreSQL)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import DATABASE_URL
import os

Base = declarative_base()

# PostgreSQL database configuration
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

if not DATABASE_URL.startswith("postgresql"):
    raise ValueError("Only PostgreSQL databases are supported. DATABASE_URL must start with 'postgresql://'")

# PostgreSQL with SSL configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10
    },
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_database_connection():
    """Check if database connection is working"""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False
