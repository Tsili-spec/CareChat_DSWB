#!/usr/bin/env python3
"""
Script to drop all tables in the PostgreSQL database.
This will delete ALL data - use with caution!
"""

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData
from app.core.config import settings
import sys

def drop_all_tables():
    """Drop all tables in the database"""
    print("🚨 WARNING: This will delete ALL tables and data in the database!")
    print(f"Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'Unknown'}")
    
    # Ask for confirmation
    confirm = input("Are you sure you want to continue? Type 'YES' to confirm: ")
    if confirm != 'YES':
        print("❌ Operation cancelled.")
        return False
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Connect and drop all tables
        with engine.connect() as conn:
            print("🔍 Finding all tables...")
            
            # Get all table names
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """))
            
            tables = [row[0] for row in result]
            
            if not tables:
                print("✅ No tables found to delete.")
                return True
            
            print(f"📋 Found {len(tables)} tables: {', '.join(tables)}")
            
            # Drop all tables with CASCADE to handle foreign keys
            print("🗑️  Dropping tables...")
            for table in tables:
                print(f"   Dropping table: {table}")
                conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            
            # Also drop the alembic version table if it exists
            print("🗑️  Dropping alembic version table...")
            conn.execute(text('DROP TABLE IF EXISTS "alembic_version" CASCADE'))
            
            # Commit the transaction
            conn.commit()
            
            print("✅ All tables dropped successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🗑️  DROP ALL TABLES SCRIPT")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    if not settings.DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables!")
        sys.exit(1)
    
    success = drop_all_tables()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS: All tables have been dropped!")
        print("💡 Next steps:")
        print("   1. Run: alembic upgrade head")
        print("   2. Or restart your FastAPI app to recreate tables")
        print("=" * 60)
    else:
        print("\n❌ FAILED: Could not drop all tables!")
        sys.exit(1)
