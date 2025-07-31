#!/usr/bin/env python3
"""
Database cleanup script
Drops all existing tables in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from datetime import datetime

def delete_all_tables():
    """Drop all tables in the database"""
    print("🗑️  Deleting all tables from database...")
    
    # Load environment variables
    load_dotenv()
    
    # Get DATABASE_URL from environment
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable is not set")
        return False
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        print(f"✅ Connected to database successfully")
        print(f"🕐 Deletion time: {datetime.now()}")
        print("=" * 80)
        
        with engine.connect() as conn:
            # Get existing tables
            metadata = MetaData()
            metadata.reflect(bind=engine)
            existing_tables = list(metadata.tables.keys())
            
            if existing_tables:
                print(f"📊 Found existing tables: {existing_tables}")
                print("⚠️  WARNING: This will DELETE ALL tables and their data!")
                
                # Drop all tables
                print("\n🗑️  Dropping all tables...")
                metadata.drop_all(bind=engine)
                conn.commit()
                
                print("✅ All tables dropped successfully")
                
                # Verify deletion
                metadata_check = MetaData()
                metadata_check.reflect(bind=engine)
                remaining_tables = list(metadata_check.tables.keys())
                
                if remaining_tables:
                    print(f"⚠️  Some tables still exist: {remaining_tables}")
                else:
                    print("✅ Database is now empty - no tables remaining")
                
            else:
                print("📭 No tables found in database")
        
        print("\n" + "=" * 80)
        print("✅ TABLE DELETION COMPLETED")
        print("=" * 80)
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def verify_empty_database():
    """Verify that the database is empty"""
    print("\n🔍 Verifying database is empty...")
    
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable is not set")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check for any tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.fetchall()
            
            if tables:
                table_names = [table[0] for table in tables]
                print(f"⚠️  Tables still exist: {table_names}")
                return False
            else:
                print("✅ Database confirmed empty - no tables found")
                return True
                
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

if __name__ == "__main__":
    # Delete all tables
    success = delete_all_tables()
    
    if success:
        # Verify deletion
        empty = verify_empty_database()
        
        if empty:
            print("\n🎉 SUCCESS: Database has been completely cleared")
            print("📝 All tables have been removed")
            print("💡 You can now run create_tables.py or recreate_database.py to rebuild the schema")
        else:
            print("\n⚠️  WARNING: Some tables may still exist")
    else:
        print("\n❌ FAILED: Could not delete all tables")
