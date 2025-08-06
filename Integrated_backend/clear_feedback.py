#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.db.database import connect_to_mongo, close_mongo_connection
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def clear_feedback_collection():
    """Clear the feedback collection to start fresh"""
    try:
        # Connect directly using motor
        client = AsyncIOMotorClient(settings.DATABASE_URL)
        db = client.carechat
        
        # Drop the feedback collection
        result = await db.feedback.drop()
        print("✅ Feedback collection dropped")
        
        # Check if collection is empty
        count = await db.feedback.count_documents({})
        print(f"✅ Feedback collection count: {count}")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(clear_feedback_collection())
