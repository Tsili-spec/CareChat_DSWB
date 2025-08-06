#!/usr/bin/env python3
"""
Test configuration loading in the application context
"""

import sys
import os
sys.path.insert(0, '.')

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

print("🔧 Environment Variable Loading Test")
print("=" * 50)

# Check direct environment variable
direct_env = os.getenv("DATABASE_URL")
print(f"Direct os.getenv(): {direct_env}")

# Test the application's config loading
print("\n⚙️ Application Config Loading Test")
print("=" * 50)

try:
    from app.core.config import settings
    print(f"App settings.DATABASE_URL: {settings.DATABASE_URL}")
    
    # Compare
    if direct_env == settings.DATABASE_URL:
        print("✅ Environment variable matches application config")
    else:
        print("❌ Mismatch between environment and application config!")
        print(f"   Environment: {direct_env}")
        print(f"   Application: {settings.DATABASE_URL}")
        
except Exception as e:
    print(f"❌ Error loading application config: {e}")
    
# Test the database connection in app context
print("\n🔗 Database Connection in App Context")
print("=" * 50)

try:
    import asyncio
    from app.db.database import connect_to_mongo, db
    
    async def test_app_db():
        print("Testing database connection as used by the app...")
        try:
            await connect_to_mongo()
            
            if db.client is not None and db.database is not None:
                print("✅ App database connection successful!")
                print(f"Database name: {db.database.name}")
                
                # Test a simple operation
                collections = await db.database.list_collection_names()
                print(f"Collections: {collections}")
                
                from app.db.database import close_mongo_connection
                await close_mongo_connection()
                return True
            else:
                print("❌ Database objects not initialized")
                return False
                
        except Exception as e:
            print(f"❌ App database connection failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    success = asyncio.run(test_app_db())
    
    if success:
        print("\n🎉 Application database connection working!")
    else:
        print("\n❌ Application database connection failed!")
        
except Exception as e:
    print(f"❌ Error testing app database: {e}")
    import traceback
    traceback.print_exc()
