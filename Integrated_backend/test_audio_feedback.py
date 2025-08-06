#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.models.models import Feedback as FeedbackModel
from app.db.database import connect_to_mongo, close_mongo_connection

async def test_audio_feedback_creation():
    """Test creating audio feedback with transcribed data"""
    try:
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to database")
        
        # Simulate transcribed data from audio
        audio_feedback = FeedbackModel(
            patient_id="6893883a6a73f9c7bc427559",
            rating=1,
            feedback_text="The doctor was rude and my prescription was expensive",  # Original transcribed text
            translated_text="The doctor was rude and my prescription was expensive",  # English translation
            language="en",  # Detected language
            sentiment="negative",  # From analysis
            topic="staff_attitude,cost",  # From analysis 
            urgency="not urgent"  # From analysis
        )
        
        # Insert the feedback
        await audio_feedback.insert()
        print(f"✅ Audio feedback created with ID: {audio_feedback.id}")
        
        # Try to retrieve it
        feedback_list = await FeedbackModel.find().to_list()
        print(f"✅ Total feedback count: {len(feedback_list)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_audio_feedback_creation())
