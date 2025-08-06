#!/usr/bin/env python3
"""
Test script for MongoDB connection
"""
import asyncio
import sys
from app.db.database import connect_to_mongo, close_mongo_connection
from app.core.logging_config import get_logger

logger = get_logger(__name__)

async def test_database_connection():
    """Test the database connection"""
    try:
        logger.info("🔍 Testing MongoDB connection...")
        await connect_to_mongo()
        logger.info("✅ Database connection test successful!")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_database_connection())
    sys.exit(0 if success else 1)
