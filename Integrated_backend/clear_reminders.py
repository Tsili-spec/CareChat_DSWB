#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.models.models import Reminder as ReminderModel, ReminderDelivery as ReminderDeliveryModel
from app.db.database import connect_to_mongo, close_mongo_connection

async def clear_reminders():
    """Clear existing reminders and deliveries that might have ObjectId issues"""
    try:
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to database")
        
        # Clear reminders
        reminder_count = await ReminderModel.find().count()
        print(f"Found {reminder_count} existing reminders")
        
        if reminder_count > 0:
            await ReminderModel.find().delete()
            print("✅ Cleared all reminders")
        
        # Clear reminder deliveries
        delivery_count = await ReminderDeliveryModel.find().count()
        print(f"Found {delivery_count} existing reminder deliveries")
        
        if delivery_count > 0:
            await ReminderDeliveryModel.find().delete()
            print("✅ Cleared all reminder deliveries")
        
        print("✅ Database cleared and ready for testing")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(clear_reminders())
