#!/usr/bin/env python3
"""
Simple database connection test
"""

import asyncio
import motor.motor_asyncio
import logging
from beanie import init_beanie
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_database():
    try:
        # Get the DATABASE_URL from environment
        from dotenv import load_dotenv
        load_dotenv()
        
        DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017")
        logger.info(f"Using DATABASE_URL: {DATABASE_URL}")
        
        # Create client
        client = motor.motor_asyncio.AsyncIOMotorClient(
            DATABASE_URL,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000
        )
        
        # Test basic connection
        logger.info("Testing basic connection...")
        await client.admin.command('ping')
        logger.info("✅ Basic connection successful!")
        
        # Get database
        database = client.carechat
        logger.info(f"Database name: {database.name}")
        
        # Test database operations
        collections = await database.list_collection_names()
        logger.info(f"Collections: {collections}")
        
        # Import models
        logger.info("Importing models...")
        from app.models.models import Patient, Feedback, Reminder, ReminderDelivery
        logger.info("✅ Models imported successfully!")
        
        # Initialize Beanie
        logger.info("Initializing Beanie ODM...")
        await init_beanie(
            database=database,
            document_models=[Patient, Feedback, Reminder, ReminderDelivery]
        )
        logger.info("✅ Beanie ODM initialized successfully!")
        
        # Test a simple operation
        logger.info("Testing Patient model operations...")
        patient_count = await Patient.count()
        logger.info(f"Current patient count: {patient_count}")
        
        # Close connection
        client.close()
        logger.info("✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_database())
    if result:
        print("🎉 Database test passed!")
        sys.exit(0)
    else:
        print("❌ Database test failed!")
        sys.exit(1)
