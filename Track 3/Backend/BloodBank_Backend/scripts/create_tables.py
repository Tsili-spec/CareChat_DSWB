#!/usr/bin/env python3
"""
Database initialization script
Creates the new 3-table blood bank schema
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.db.database import Base
from app.models import User, BloodCollection, BloodUsage, BloodStock
from dotenv import load_dotenv

def create_database_tables():
    """Create all database tables"""
    load_dotenv()
    
    # Construct DATABASE_URL from components
    POSTGRES_SERVER = os.getenv('POSTGRES_SERVER')
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DB = os.getenv('POSTGRES_DB')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(DATABASE_URL)
    
    print('🩸 Creating Blood Bank Database Tables...')
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print('✅ Database tables created successfully:')
    print('   👤 users - User accounts and permissions')
    print('   📋 blood_collections - Blood donation records')
    print('   📤 blood_usage - Blood distribution records')
    print('   📊 blood_stock - Stock tracking with audit trail')
    
    return engine

if __name__ == "__main__":
    create_database_tables()
