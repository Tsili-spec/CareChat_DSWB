#!/usr/bin/env python3
"""
Database Configuration Test Script
Tests if the configuration is loaded correctly and database connects properly
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print(f"📂 Project root: {project_root}")
print(f"📂 Current working directory: {os.getcwd()}")
print(f"📂 Python path: {sys.path[:2]}")

try:
    # Test environment loading
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🔧 Environment variables loaded:")
    print(f"   DATABASE_URL from env: {os.getenv('DATABASE_URL', 'NOT_FOUND')}")
    print(f"   JWT_SECRET_KEY: {'SET' if os.getenv('JWT_SECRET_KEY') else 'NOT_SET'}")
    print("=" * 50)
    
    # Test config loading
    from app.core.config import settings
    print("⚙️  Configuration loaded:")
    print(f"   DATABASE_URL: {settings.DATABASE_URL}")
    print(f"   PROJECT_NAME: {settings.PROJECT_NAME}")
    print("=" * 50)
    
    # Test model imports
    print("📋 Testing model imports:")
    from app.models.models import Patient, Feedback, Reminder, ReminderDelivery
    print("   ✅ Patient model imported")
    print("   ✅ Feedback model imported")
    print("   ✅ Reminder model imported")
    print("   ✅ ReminderDelivery model imported")
    print("=" * 50)
    
    # Test database connection
    print("🔗 Testing database connection:")
    from app.db.database import connect_to_mongo, close_mongo_connection, db
    
    async def test_db_connection():
        try:
            await connect_to_mongo()
            
            if db.client is not None and db.database is not None:
                print("   ✅ Database client created")
                print(f"   ✅ Database object: {db.database.name}")
                
                # Test basic operation
                try:
                    result = await db.database.command("ping")
                    print("   ✅ Database ping successful")
                    print(f"   📊 Ping result: {result}")
                except Exception as ping_error:
                    print(f"   ❌ Database ping failed: {ping_error}")
                
                # Test collections
                try:
                    collections = await db.database.list_collection_names()
                    print(f"   📂 Available collections: {collections}")
                except Exception as coll_error:
                    print(f"   ⚠️  Cannot list collections: {coll_error}")
                
                await close_mongo_connection()
                print("   ✅ Database connection closed")
                return True
            else:
                print("   ❌ Database client or database not initialized")
                return False
                
        except Exception as e:
            print(f"   ❌ Database connection test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Run async test
    result = asyncio.run(test_db_connection())
    print("=" * 50)
    
    if result:
        print("🎉 All configuration tests passed!")
        sys.exit(0)
    else:
        print("❌ Some configuration tests failed!")
        sys.exit(1)
        
except ImportError as import_error:
    print(f"❌ Import error: {import_error}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Configuration test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
