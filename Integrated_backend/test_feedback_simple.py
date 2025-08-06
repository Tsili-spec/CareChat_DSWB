#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.models.models import Feedback as FeedbackModel
from app.db.database import connect_to_mongo, close_mongo_connection

async def test_simple_feedback():
    """Test creating a simple feedback without analysis"""
    try:
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to database")
        
        # Create a simple feedback record
        simple_feedback = FeedbackModel(
            patient_id="6893883a6a73f9c7bc427559",
            rating=3,
            feedback_text="Simple test feedback",
            translated_text="Simple test feedback",
            language="en",
            sentiment="neutral",
            topic=None,
            urgency="not urgent"
        )
        
        # Insert the feedback
        await simple_feedback.insert()
        print(f"✅ Feedback created with ID: {simple_feedback.id}")
        
        # Try to retrieve it
        feedback_list = await FeedbackModel.find().to_list()
        print(f"✅ Total feedback count: {len(feedback_list)}")
        
        # Print the first few feedbacks
        for i, feedback in enumerate(feedback_list[:3]):
            print(f"Feedback {i+1}: ID={feedback.id}, Text='{feedback.feedback_text[:50]}...'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_simple_feedback())
