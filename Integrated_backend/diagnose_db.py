#!/usr/bin/env python3
"""
Advanced MongoDB connection diagnostics
"""
import asyncio
from urllib.parse import urlparse
import motor.motor_asyncio
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

async def diagnose_connection():
    """Diagnose MongoDB connection issues"""
    logger.info("🔍 Starting MongoDB connection diagnostics...")
    
    # Parse the connection URL
    parsed_url = urlparse(settings.DATABASE_URL)
    logger.info(f"📊 Connection Details:")
    logger.info(f"   Protocol: {parsed_url.scheme}")
    logger.info(f"   Host: {parsed_url.hostname}")
    logger.info(f"   Port: {parsed_url.port}")
    logger.info(f"   Username: {parsed_url.username}")
    logger.info(f"   Database: {parsed_url.path[1:] if parsed_url.path else 'default'}")
    
    # Test basic connectivity
    logger.info("\n🔌 Testing basic connectivity...")
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.DATABASE_URL,
            serverSelectionTimeoutMS=5000  # 5 second timeout
        )
        
        # Try to get server info
        server_info = await client.server_info()
        logger.info(f"✅ Server reachable! MongoDB version: {server_info.get('version', 'unknown')}")
        
        # Try to ping
        await client.admin.command('ping')
        logger.info("✅ Authentication successful!")
        
        # List databases
        db_list = await client.list_database_names()
        logger.info(f"📁 Available databases: {db_list}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        logger.info("\n💡 Troubleshooting suggestions:")
        logger.info("   1. Verify the username and password are correct")
        logger.info("   2. Check if the server IP is accessible from your location")
        logger.info("   3. Ensure the database server allows connections from your IP")
        logger.info("   4. Verify the database name exists")
        logger.info("   5. Check if authentication database is 'admin' or another specific database")
        return False

if __name__ == "__main__":
    asyncio.run(diagnose_connection())
