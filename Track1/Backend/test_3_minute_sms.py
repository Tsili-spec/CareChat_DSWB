#!/usr/bin/env python3
"""
SMS Reminder 3-Minute Test Script
Creates a reminder that will automatically send in 3 minutes via the scheduler
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_3_minute_reminder_test():
    """Create a reminder that will send in exactly 3 minutes"""
    
    print("⏰ CareChat 3-Minute SMS Reminder Test")
    print("=" * 50)
    
    # Get current time and calculate 3 minutes ahead
    now = datetime.utcnow()
    future_time = now + timedelta(minutes=3)
    current_day = now.strftime("%A")
    
    print(f"🕐 Current time: {now.strftime('%H:%M:%S UTC')}")
    print(f"📅 Today is: {current_day}")
    print(f"⏰ Reminder will be sent at: {future_time.strftime('%H:%M:%S UTC')} (in 3 minutes)")
    
    # Get phone number from environment
    recipient_phone = os.getenv('MY_NUMBER')
    if not recipient_phone:
        print("❌ MY_NUMBER not found in .env file")
        return False
    
    print(f"📱 SMS will be sent to: {recipient_phone}")
    
    base_url = "http://localhost:8000/api"
    
    # Check if API is running
    print("\n1️⃣ Checking API Status...")
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("❌ API not responding")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to API: {str(e)}")
        return False
    
    # Check SMS service status
    print("\n2️⃣ Checking SMS Service...")
    try:
        response = requests.get(f"{base_url}/reminder/sms-status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ SMS Configured: {status['sms_configured']}")
            print(f"📊 Scheduler Running: {status['scheduler_running']}")
            
            if not status['sms_configured']:
                print("❌ SMS not configured!")
                return False
        else:
            print("❌ Failed to get SMS status")
            return False
    except Exception as e:
        print(f"❌ Error checking SMS status: {str(e)}")
        return False
    
    # Use existing patient ID (from previous tests)
    patient_id = "089d2b4b-d03f-4bca-b827-8fae840cc3e5"  # Known patient with correct phone
    
    # Create reminder for exactly 3 minutes from now
    print(f"\n3️⃣ Creating 3-Minute Reminder...")
    
    test_reminder_data = {
        "patient_id": patient_id,
        "title": "3-Minute Test Reminder",
        "message": f"This SMS was automatically sent by the CareChat scheduler at {future_time.strftime('%H:%M')} UTC. The system is working correctly!",
        "scheduled_time": [future_time.isoformat() + "Z"],
        "days": [current_day],  # Today
        "status": "active"
    }
    
    try:
        response = requests.post(f"{base_url}/reminder/", json=test_reminder_data)
        if response.status_code == 200:
            reminder = response.json()
            reminder_id = reminder['reminder_id']
            print(f"✅ Reminder created successfully!")
            print(f"   Reminder ID: {reminder_id}")
            print(f"   Title: {reminder['title']}")
            print(f"   Scheduled for: {future_time.strftime('%H:%M:%S')} on {current_day}")
        else:
            print(f"❌ Failed to create reminder: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating reminder: {str(e)}")
        return False
    
    # Start the scheduler if not running
    print(f"\n4️⃣ Starting SMS Scheduler...")
    try:
        response = requests.post(f"{base_url}/reminder/start-scheduler")
        if response.status_code == 200:
            result = response.json()
            if result.get('success') or 'already running' in result.get('message', ''):
                print("✅ Scheduler is running")
            else:
                print(f"⚠️  Scheduler status: {result.get('message')}")
        else:
            print(f"⚠️  Scheduler response: {response.text}")
    except Exception as e:
        print(f"❌ Error with scheduler: {str(e)}")
    
    # Verify upcoming reminders
    print(f"\n5️⃣ Verifying Upcoming Reminders...")
    try:
        response = requests.get(f"{base_url}/reminder/upcoming?hours_ahead=1")
        if response.status_code == 200:
            upcoming = response.json()
            found_our_reminder = False
            
            for reminder in upcoming:
                if reminder['reminder_id'] == reminder_id:
                    found_our_reminder = True
                    print(f"✅ Found our reminder in schedule:")
                    print(f"   Patient: {reminder['patient_name']}")
                    print(f"   Phone: {reminder['patient_phone']}")
                    print(f"   Next occurrence: {reminder['next_occurrence']}")
                    break
            
            if not found_our_reminder:
                print(f"⚠️  Our reminder not found in upcoming schedule")
                
        else:
            print(f"❌ Failed to get upcoming reminders: {response.text}")
    except Exception as e:
        print(f"❌ Error checking upcoming reminders: {str(e)}")
    
    # Final instructions
    print(f"\n📱 TEST INSTRUCTIONS:")
    print("=" * 30)
    print(f"⏰ Your SMS will be sent automatically in 3 minutes at {future_time.strftime('%H:%M:%S')} UTC")
    print(f"📱 Watch your phone ({recipient_phone}) for the message")
    print(f"🔄 The scheduler checks every minute for due reminders")
    print(f"📊 You can monitor the logs with: tail -f logs/carechat_api.log")
    print(f"💡 If you don't receive the SMS, check:")
    print("   - Twilio account balance")
    print("   - Phone number verification in Twilio")
    print("   - Network connectivity")
    print("   - Message filtering/spam detection")
    
    return True

def test_immediate_sms():
    """Send an immediate SMS to verify delivery is working"""
    print(f"\n🧪 IMMEDIATE SMS TEST (for comparison)")
    print("-" * 40)
    
    recipient_phone = os.getenv('MY_NUMBER')
    base_url = "http://localhost:8000/api"
    patient_id = "089d2b4b-d03f-4bca-b827-8fae840cc3e5"
    
    # Create a simple immediate reminder
    now = datetime.utcnow()
    current_day = now.strftime("%A")
    
    immediate_reminder_data = {
        "patient_id": patient_id,
        "title": "Immediate Test",
        "message": f"Immediate SMS test sent at {now.strftime('%H:%M')}. If you receive this, SMS delivery is working.",
        "scheduled_time": [now.isoformat() + "Z"],
        "days": [current_day],
        "status": "active"
    }
    
    try:
        # Create reminder
        response = requests.post(f"{base_url}/reminder/", json=immediate_reminder_data)
        if response.status_code == 200:
            reminder = response.json()
            reminder_id = reminder['reminder_id']
            
            # Send immediately
            send_response = requests.post(f"{base_url}/reminder/{reminder_id}/send-sms")
            if send_response.status_code == 200:
                result = send_response.json()
                print(f"✅ Immediate SMS sent!")
                print(f"   Message SID: {result.get('message_sid')}")
                print(f"   Status: {result.get('status')}")
                print(f"   To: {result.get('phone_number')}")
                print(f"📱 Check your phone now for immediate delivery")
                return True
            else:
                print(f"❌ Failed to send immediate SMS: {send_response.text}")
        else:
            print(f"❌ Failed to create immediate reminder: {response.text}")
    
    except Exception as e:
        print(f"❌ Error with immediate SMS test: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("🚀 Starting 3-Minute SMS Reminder Test")
    print("💡 This will create a reminder that automatically sends in 3 minutes")
    
    choice = input("\nChoose test type:\n1. 3-minute scheduled SMS\n2. Immediate SMS (for comparison)\n3. Both\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        success = create_3_minute_reminder_test()
    elif choice == "2":
        success = test_immediate_sms()
    elif choice == "3":
        print("\n" + "="*50)
        print("RUNNING IMMEDIATE SMS TEST FIRST:")
        immediate_success = test_immediate_sms()
        
        print("\n" + "="*50)
        print("NOW SETTING UP 3-MINUTE SCHEDULED SMS:")
        scheduled_success = create_3_minute_reminder_test()
        
        success = immediate_success and scheduled_success
    else:
        print("❌ Invalid choice")
        success = False
    
    if success:
        print("\n✅ Test setup completed successfully!")
        if choice in ["1", "3"]:
            print("⏰ Wait 3 minutes for your scheduled SMS...")
    else:
        print("\n❌ Test setup failed!")
    
    print("\n🔍 To monitor the system:")
    print("   tail -f logs/carechat_api.log")
    print("   curl http://localhost:8000/api/reminder/upcoming")
