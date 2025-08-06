#!/usr/bin/env python3
"""
MongoDB Database Connection Test
Tests the connection to the remote MongoDB database
"""
import asyncio
import sys
from datetime import datetime
from urllib.parse import urlparse
import motor.motor_asyncio
from beanie import init_beanie
import pymongo.errors

# Database URL
DATABASE_URL = "mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017"

# Import models for Beanie initialization
try:
    from app.models.models import Patient, Feedback, Reminder, ReminderDelivery
    MODELS_AVAILABLE = True
except ImportError:
    print("⚠️  Models not available, testing basic connection only")
    MODELS_AVAILABLE = False

class DatabaseTester:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.client = None
        self.database = None
        
    def parse_connection_info(self):
        """Parse and display connection information"""
        parsed = urlparse(self.database_url)
        print("📊 Connection Information:")
        print(f"   Protocol: {parsed.scheme}")
        print(f"   Host: {parsed.hostname}")
        print(f"   Port: {parsed.port}")
        print(f"   Username: {parsed.username}")
        print(f"   Password: {'*' * len(parsed.password) if parsed.password else 'None'}")
        print()
        
    async def test_basic_connection(self):
        """Test basic MongoDB connection"""
        print("🔌 Testing basic connection...")
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                self.database_url,
                serverSelectionTimeoutMS=10000  # 10 second timeout
            )
            
            # Test server selection and get server info
            server_info = await self.client.server_info()
            print(f"✅ Connected successfully!")
            print(f"   MongoDB Version: {server_info.get('version', 'unknown')}")
            print(f"   Max Wire Version: {server_info.get('maxWireVersion', 'unknown')}")
            return True
            
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(f"❌ Server selection timeout: {e}")
            return False
        except pymongo.errors.OperationFailure as e:
            print(f"❌ Authentication failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
            
    async def test_authentication(self):
        """Test authentication by pinging the server"""
        print("\n🔐 Testing authentication...")
        try:
            await self.client.admin.command('ping')
            print("✅ Authentication successful!")
            return True
        except pymongo.errors.OperationFailure as e:
            print(f"❌ Authentication failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Ping failed: {e}")
            return False
            
    async def test_database_operations(self):
        """Test basic database operations"""
        print("\n📁 Testing database operations...")
        try:
            # Get default database or create one
            db_name = urlparse(self.database_url).path.strip('/') or 'carechat'
            self.database = self.client[db_name]
            
            # List collections
            collections = await self.database.list_collection_names()
            print(f"✅ Database '{db_name}' accessible")
            print(f"   Existing collections: {collections if collections else 'None'}")
            
            # Test write operation
            test_collection = self.database.connection_test
            test_doc = {
                "test": "connection_test",
                "timestamp": datetime.utcnow(),
                "status": "testing"
            }
            
            result = await test_collection.insert_one(test_doc)
            print(f"✅ Write test successful - Document ID: {result.inserted_id}")
            
            # Test read operation
            retrieved_doc = await test_collection.find_one({"_id": result.inserted_id})
            if retrieved_doc:
                print("✅ Read test successful")
            else:
                print("❌ Read test failed")
                
            # Clean up test document
            await test_collection.delete_one({"_id": result.inserted_id})
            print("✅ Cleanup successful")
            
            return True
            
        except Exception as e:
            print(f"❌ Database operations failed: {e}")
            return False
            
    async def test_beanie_initialization(self):
        """Test Beanie ODM initialization"""
        if not MODELS_AVAILABLE:
            print("\n⚠️  Skipping Beanie test - models not available")
            return True
            
        print("\n🎯 Testing Beanie ODM initialization...")
        try:
            await init_beanie(
                database=self.database,
                document_models=[Patient, Feedback, Reminder, ReminderDelivery]
            )
            print("✅ Beanie ODM initialized successfully!")
            
            # Test model operations
            print("   Testing Patient model...")
            patient_count = await Patient.count()
            print(f"   Current Patient count: {patient_count}")
            
            print("   Testing Feedback model...")
            feedback_count = await Feedback.count()
            print(f"   Current Feedback count: {feedback_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Beanie initialization failed: {e}")
            return False
            
    async def test_alternative_databases(self):
        """Test alternative database names"""
        print("\n🔄 Testing alternative database configurations...")
        try:
            # Test common database names
            db_names = ['carechat', 'test', 'admin']
            
            for db_name in db_names:
                db = self.client[db_name]
                try:
                    # Try to access database stats
                    stats = await db.command('dbstats')
                    print(f"✅ Database '{db_name}' accessible")
                    print(f"   Collections: {stats.get('collections', 0)}")
                    print(f"   Data Size: {stats.get('dataSize', 0)} bytes")
                except Exception as e:
                    print(f"⚠️  Database '{db_name}' not accessible: {e}")
                    
            return True
            
        except Exception as e:
            print(f"❌ Alternative database test failed: {e}")
            return False
            
    async def run_comprehensive_test(self):
        """Run all database tests"""
        print("🚀 Starting comprehensive MongoDB connection test")
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        self.parse_connection_info()
        
        # Test basic connection
        if not await self.test_basic_connection():
            return False
            
        # Test authentication
        if not await self.test_authentication():
            return False
            
        # Test database operations
        if not await self.test_database_operations():
            return False
            
        # Test Beanie initialization
        await self.test_beanie_initialization()
        
        # Test alternative databases
        await self.test_alternative_databases()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        return True
        
    async def cleanup(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🧹 Database connection closed")

async def main():
    """Main test function"""
    tester = DatabaseTester(DATABASE_URL)
    
    try:
        success = await tester.run_comprehensive_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    # Run the comprehensive database test
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
