#!/usr/bin/env python3
"""
Quick database verification script
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def check_database():
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = result.fetchall()
        
        if tables:
            print(f"📊 Tables found: {[table[0] for table in tables]}")
        else:
            print("✅ Database is empty - no tables found")

if __name__ == "__main__":
    check_database()
