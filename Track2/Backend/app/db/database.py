# DB session management (PostgreSQL)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import DATABASE_URL
import os

Base = declarative_base()

# Handle different database types and SSL configuration
database_url = DATABASE_URL or "sqlite:///./carechat.db"

if database_url.startswith("postgresql"):
    # PostgreSQL with SSL configuration
    engine = create_engine(
        database_url,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 10
        },
        pool_pre_ping=True,
        pool_recycle=300
    )
else:
    # SQLite for development
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}
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
