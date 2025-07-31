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
    
    # Get DATABASE_URL from environment
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
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
