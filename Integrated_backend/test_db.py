#!/usr/bin/env python3
"""
MongoDB Connection Test Script
Tests connectivity to the remote MongoDB instance
"""

import asyncio
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB connection URL
MONGODB_URL = "mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017"

def test_sync_connection():
    """Test synchronous MongoDB connection using pymongo"""
    logger.info("🔄 Testing synchronous MongoDB connection...")
    
    try:
        # Create client with timeout
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        logger.info("✅ Synchronous connection successful!")
        
        # Get server info
        server_info = client.server_info()
        logger.info(f"📊 MongoDB version: {server_info.get('version')}")
        
        # List databases
        databases = client.list_database_names()
        logger.info(f"🗃️  Available databases: {databases}")
        
        # Test basic operations on a test database
        db = client.test_carechat
        collection = db.test_collection
        
        # Insert a test document
        test_doc = {
            "test": True,
            "timestamp": datetime.now(),
            "message": "MongoDB connection test"
        }
        result = collection.insert_one(test_doc)
        logger.info(f"✅ Document inserted with ID: {result.inserted_id}")
        
        # Read the document back
        found_doc = collection.find_one({"_id": result.inserted_id})
        if found_doc:
            logger.info("✅ Document retrieval successful!")
            logger.info(f"📄 Retrieved document: {found_doc}")
        
        # Clean up - delete the test document
        collection.delete_one({"_id": result.inserted_id})
        logger.info("🧹 Test document cleaned up")
        
        # Close connection
        client.close()
        return True
        
    except ConnectionFailure as e:
        logger.error(f"❌ Connection failed: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        logger.error(f"❌ Server selection timeout: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

async def test_async_connection():
    """Test asynchronous MongoDB connection using motor"""
    logger.info("🔄 Testing asynchronous MongoDB connection...")
    
    try:
        # Create async client
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Test connection
        await client.admin.command('ping')
        logger.info("✅ Asynchronous connection successful!")
        
        # Get server info
        server_info = await client.server_info()
        logger.info(f"📊 MongoDB version (async): {server_info.get('version')}")
        
        # List databases
        databases = await client.list_database_names()
        logger.info(f"🗃️  Available databases (async): {databases}")
        
        # Test basic operations
        db = client.test_carechat_async
        collection = db.test_collection_async
        
        # Insert a test document
        test_doc = {
            "test": True,
            "timestamp": datetime.now(),
            "message": "Async MongoDB connection test",
            "type": "async_test"
        }
        result = await collection.insert_one(test_doc)
        logger.info(f"✅ Async document inserted with ID: {result.inserted_id}")
        
        # Read the document back
        found_doc = await collection.find_one({"_id": result.inserted_id})
        if found_doc:
            logger.info("✅ Async document retrieval successful!")
            logger.info(f"📄 Retrieved async document: {found_doc}")
        
        # Test find multiple
        cursor = collection.find({"type": "async_test"})
        docs = await cursor.to_list(length=10)
        logger.info(f"📋 Found {len(docs)} async test documents")
        
        # Clean up - delete the test document
        await collection.delete_one({"_id": result.inserted_id})
        logger.info("🧹 Async test document cleaned up")
        
        # Close connection
        client.close()
        return True
        
    except ConnectionFailure as e:
        logger.error(f"❌ Async connection failed: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        logger.error(f"❌ Async server selection timeout: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Async unexpected error: {e}")
        return False

def test_connection_details():
    """Test and display connection details"""
    logger.info("🔍 Testing connection details...")
    
    try:
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Try to get basic server info without admin privileges
        try:
            admin_db = client.admin
            server_status = admin_db.command("serverStatus")
            
            logger.info("📈 Server Statistics:")
            logger.info(f"   - Host: {server_status.get('host')}")
            logger.info(f"   - Version: {server_status.get('version')}")
            logger.info(f"   - Process: {server_status.get('process')}")
            logger.info(f"   - Uptime: {server_status.get('uptime')} seconds")
            logger.info(f"   - Connections: {server_status.get('connections', {})}")
            
        except Exception as admin_error:
            logger.warning(f"⚠️  Cannot access admin commands (expected): {admin_error}")
            logger.info("📈 Using alternative methods to get server info...")
            
            # Get basic info without admin privileges
            server_info = client.server_info()
            logger.info(f"   - MongoDB Version: {server_info.get('version')}")
            logger.info(f"   - Git Version: {server_info.get('gitVersion')}")
            logger.info(f"   - Build Info: {server_info.get('buildEnvironment', {}).get('target_arch', 'unknown')}")
        
        # Test database operations that don't require admin privileges
        logger.info("🗃️  Testing database access...")
        
        # Test main carechat database
        carechat_db = client.carechat
        try:
            collections = carechat_db.list_collection_names()
            logger.info(f"📂 Collections in 'carechat' database: {collections}")
        except Exception as e:
            logger.info(f"📂 Cannot list collections in 'carechat': {e}")
        
        # Test creating a test database
        test_db = client.carechat_test
        try:
            collections = test_db.list_collection_names()
            logger.info(f"🗂️  Collections in carechat_test: {collections}")
            
            # Try to create a test collection
            test_collection = test_db.test_permissions
            test_doc = {"permission_test": True, "timestamp": datetime.now()}
            result = test_collection.insert_one(test_doc)
            logger.info(f"✅ Test document created in carechat_test: {result.inserted_id}")
            
            # Clean up
            test_collection.delete_one({"_id": result.inserted_id})
            logger.info("🧹 Test document cleaned up from carechat_test")
            
        except Exception as e:
            logger.warning(f"⚠️  Limited access to test database: {e}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error getting connection details: {e}")
        return False

async def test_carechat_specific_operations():
    """Test CareChat specific database operations"""
    logger.info("🏥 Testing CareChat specific database operations...")
    
    try:
        # Use the exact URL from .env
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=10000)
        
        # Test connection
        await client.admin.command('ping')
        logger.info("✅ CareChat database connection successful!")
        
        # Test main carechat database
        carechat_db = client.carechat
        
        # Test collections that CareChat would use
        test_collections = [
            "patients",
            "feedback", 
            "appointments",
            "users",
            "sessions"
        ]
        
        for collection_name in test_collections:
            collection = carechat_db[collection_name]
            
            # Try to insert a test document
            test_doc = {
                "test": True,
                "collection": collection_name,
                "timestamp": datetime.now(),
                "test_type": "carechat_operation"
            }
            
            try:
                result = await collection.insert_one(test_doc)
                logger.info(f"✅ {collection_name}: Insert successful (ID: {result.inserted_id})")
                
                # Try to read it back
                found = await collection.find_one({"_id": result.inserted_id})
                if found:
                    logger.info(f"✅ {collection_name}: Read successful")
                
                # Try to update it
                update_result = await collection.update_one(
                    {"_id": result.inserted_id},
                    {"$set": {"updated": True, "update_time": datetime.now()}}
                )
                if update_result.modified_count > 0:
                    logger.info(f"✅ {collection_name}: Update successful")
                
                # Clean up
                await collection.delete_one({"_id": result.inserted_id})
                logger.info(f"🧹 {collection_name}: Test document cleaned up")
                
            except Exception as col_error:
                logger.warning(f"⚠️  {collection_name}: Limited operations - {col_error}")
        
        # Test database statistics
        try:
            stats = await carechat_db.command("dbStats")
            logger.info(f"📊 Database stats: {stats.get('collections', 0)} collections, {stats.get('objects', 0)} documents")
        except Exception as stats_error:
            logger.info(f"📊 Cannot get database stats: {stats_error}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ CareChat operations failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Starting MongoDB Connection Tests")
    logger.info(f"🔗 Testing URL: {MONGODB_URL}")
    logger.info("=" * 50)
    
    # Test synchronous connection
    sync_success = test_sync_connection()
    logger.info("=" * 50)
    
    # Test asynchronous connection
    async_success = await test_async_connection()
    logger.info("=" * 50)
    
    # Test CareChat specific operations
    carechat_success = await test_carechat_specific_operations()
    logger.info("=" * 50)
    
    # Test connection details
    details_success = test_connection_details()
    logger.info("=" * 50)
    
    # Summary
    logger.info("📊 Test Summary:")
    logger.info(f"   - Synchronous connection: {'✅ PASS' if sync_success else '❌ FAIL'}")
    logger.info(f"   - Asynchronous connection: {'✅ PASS' if async_success else '❌ FAIL'}")
    logger.info(f"   - CareChat operations: {'✅ PASS' if carechat_success else '❌ FAIL'}")
    logger.info(f"   - Connection details: {'✅ PASS' if details_success else '❌ FAIL'}")
    
    if sync_success and async_success and carechat_success:
        logger.info("🎉 All critical tests passed! MongoDB is ready for CareChat.")
        return 0
    else:
        logger.error("⚠️  Some critical tests failed. Please check your MongoDB configuration.")
        return 1
            "users",
            "sessions"
        ]
        
        for collection_name in test_collections:
            collection = carechat_db[collection_name]
            
            # Try to insert a test document
            test_doc = {
                "test": True,
                "collection": collection_name,
                "timestamp": datetime.now(),
                "test_type": "carechat_operation"
            }
            
            try:
                result = await collection.insert_one(test_doc)
                logger.info(f"✅ {collection_name}: Insert successful (ID: {result.inserted_id})")
                
                # Try to read it back
                found = await collection.find_one({"_id": result.inserted_id})
                if found:
                    logger.info(f"✅ {collection_name}: Read successful")
                
                # Try to update it
                update_result = await collection.update_one(
                    {"_id": result.inserted_id},
                    {"$set": {"updated": True, "update_time": datetime.now()}}
                )
                if update_result.modified_count > 0:
                    logger.info(f"✅ {collection_name}: Update successful")
                
                # Clean up
                await collection.delete_one({"_id": result.inserted_id})
                logger.info(f"🧹 {collection_name}: Test document cleaned up")
                
            except Exception as col_error:
                logger.warning(f"⚠️  {collection_name}: Limited operations - {col_error}")
        
        # Test database statistics
        try:
            stats = await carechat_db.command("dbStats")
            logger.info(f"📊 Database stats: {stats.get('collections', 0)} collections, {stats.get('objects', 0)} documents")
        except Exception as stats_error:
            logger.info(f"📊 Cannot get database stats: {stats_error}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ CareChat operations failed: {e}")
        return False

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)