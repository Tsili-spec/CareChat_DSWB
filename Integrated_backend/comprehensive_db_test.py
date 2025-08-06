#!/usr/bin/env python3
"""
Test with alternative MongoDB setups
"""
import asyncio
import motor.motor_asyncio
from app.core.logging_config import get_logger

logger = get_logger(__name__)

async def test_local_mongodb():
    """Test connection to local MongoDB (if available)"""
    logger.info("🔍 Testing local MongoDB connection...")
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
        await client.admin.command('ping')
        logger.info("✅ Local MongoDB is available!")
        
        # Create a test database
        db = client.carechat_local
        test_collection = db.test
        
        # Insert a test document
        result = await test_collection.insert_one({"test": "connection", "status": "working"})
        logger.info(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Read it back
        doc = await test_collection.find_one({"test": "connection"})
        logger.info(f"✅ Test document retrieved: {doc}")
        
        # Clean up
        await test_collection.delete_one({"_id": result.inserted_id})
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Local MongoDB not available: {e}")
        return False

async def test_alternative_connection_strings():
    """Test alternative connection string formats"""
    
    # Original connection string with explicit authentication database
    alt_urls = [
        "mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017/carechat?authSource=admin",
        "mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017/carechat?authSource=carechat",
        "mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017/?authSource=admin",
    ]
    
    for i, url in enumerate(alt_urls, 1):
        logger.info(f"\n🔍 Testing alternative connection string {i}...")
        logger.info(f"   URL: {url}")
        
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(url, serverSelectionTimeoutMS=5000)
            await client.admin.command('ping')
            logger.info("✅ Connection successful!")
            
            # Try to list databases
            dbs = await client.list_database_names()
            logger.info(f"📁 Available databases: {dbs}")
            
            client.close()
            return url
            
        except Exception as e:
            logger.error(f"❌ Failed: {e}")
    
    return None

async def main():
    """Main diagnostic function"""
    logger.info("🚀 Starting comprehensive MongoDB diagnostics...\n")
    
    # Test local MongoDB first
    local_success = await test_local_mongodb()
    
    if local_success:
        logger.info("\n💡 Recommendation: Use local MongoDB for development")
        logger.info("   Connection string: mongodb://localhost:27017")
    
    # Test alternative remote connection strings
    logger.info("\n" + "="*50)
    working_url = await test_alternative_connection_strings()
    
    if working_url:
        logger.info(f"\n✅ Found working connection string: {working_url}")
        logger.info("💡 Update your .env file with this connection string")
    else:
        logger.info("\n❌ No working remote connection found")
        logger.info("💡 Contact the database administrator to verify:")
        logger.info("   - Credentials are correct")
        logger.info("   - Your IP is whitelisted")
        logger.info("   - The database server is running")
        logger.info("   - Authentication database settings")

if __name__ == "__main__":
    asyncio.run(main())
