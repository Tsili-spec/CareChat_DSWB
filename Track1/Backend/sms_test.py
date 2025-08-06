#!/usr/bin/env python3
"""
SMS Test Script for CareChat Backend
Tests SMS functionality using Twilio API with credentials from .env file
"""

import os
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime
import sys

def load_twilio_config():
    """Load Twilio configuration from .env file"""
    load_dotenv()
    
    config = {
        'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
        'auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
        'twilio_number': os.getenv('TWILIO_NUMBER'),
        'my_number': os.getenv('MY_NUMBER')
    }
    
    # Validate configuration
    missing_configs = [key for key, value in config.items() if not value]
    if missing_configs:
        print(f"❌ Missing configuration: {', '.join(missing_configs)}")
        print("Please check your .env file for Twilio credentials.")
        return None
    
    return config

def send_test_sms(message: str = None, to_number: str = None):
    """Send a test SMS using Twilio with delivery verification"""
    
    print("📱 CareChat SMS Test")
    print("=" * 40)
    
    # Load configuration
    config = load_twilio_config()
    if not config:
        return False
    
    print(f"✅ Configuration loaded successfully")
    print(f"   Account SID: {config['account_sid'][:10]}...")
    print(f"   Twilio Number: {config['twilio_number']}")
    print(f"   Target Number: {to_number or config['my_number']}")
    
    try:
        # Initialize Twilio client
        client = Client(config['account_sid'], config['auth_token'])
        
        # Default message if none provided - keep it simple and short
        if not message:
            timestamp = datetime.now().strftime("%H:%M")
            message = f"CareChat test at {timestamp}. SMS working! Reply STOP to opt out."
        
        # Send SMS
        print(f"\n📤 Sending SMS...")
        print(f"   To: {to_number or config['my_number']}")
        print(f"   From: {config['twilio_number']}")
        print(f"   Message: {message}")
        
        message_instance = client.messages.create(
            body=message,
            from_=config['twilio_number'],
            to=to_number or config['my_number']
        )
        
        print(f"\n✅ SMS sent successfully!")
        print(f"   Message SID: {message_instance.sid}")
        print(f"   Initial Status: {message_instance.status}")
        print(f"   Direction: {message_instance.direction}")
        
        # Wait and check delivery status like the working example
        print(f"\n⏳ Waiting 10 seconds to verify delivery...")
        import time
        time.sleep(10)
        
        # Fetch updated status
        updated_message = client.messages(message_instance.sid).fetch()
        print(f"\n📊 Delivery Verification:")
        print(f"   Final Status: {updated_message.status}")
        print(f"   Date Sent: {updated_message.date_sent}")
        print(f"   Price: {updated_message.price} {updated_message.price_unit}")
        
        if updated_message.error_code:
            print(f"   ❌ Error: {updated_message.error_code} - {updated_message.error_message}")
            return False
        
        if updated_message.status == 'delivered':
            print(f"   ✅ Twilio confirms delivery - check your phone!")
            print(f"   📱 You should receive: '{message}'")
            return True
        elif updated_message.status in ['sent', 'queued']:
            print(f"   ⏳ Status: {updated_message.status} - message may still be in transit")
            print(f"   📱 Check your phone in the next few minutes")
            return True
        else:
            print(f"   ⚠️  Status: {updated_message.status} - delivery uncertain")
            return False
        
    except Exception as e:
        print(f"\n❌ Failed to send SMS!")
        print(f"   Error: {str(e)}")
        return False

def send_reminder_sms(patient_name: str = "Test Patient", reminder_text: str = None):
    """Send a patient reminder SMS (simulating the reminder system)"""
    
    if not reminder_text:
        # Keep it short and simple for better delivery
        timestamp = datetime.now().strftime("%H:%M")
        reminder_text = f"CareChat Reminder for {patient_name}: Don't forget your medication schedule today! Time: {timestamp}"
    
    print(f"\n💊 Sending Patient Reminder to {patient_name}")
    return send_test_sms(reminder_text)

def send_feedback_notification(feedback_summary: str = None):
    """Send a feedback notification SMS (simulating feedback alerts)"""
    
    if not feedback_summary:
        # Keep it short and simple for better delivery
        timestamp = datetime.now().strftime("%H:%M")
        feedback_summary = f"CareChat Alert: New patient feedback received at {timestamp}. Please check your dashboard. Sentiment: Negative, Topics: wait_time"
    
    print(f"\n📋 Sending Feedback Notification")
    return send_test_sms(feedback_summary)

def interactive_sms_test():
    """Interactive SMS testing menu"""
    
    while True:
        print(f"\n📱 CareChat SMS Test Menu")
        print("=" * 30)
        print("1. Send Basic Test SMS")
        print("2. Send Patient Reminder SMS")
        print("3. Send Feedback Notification")
        print("4. Send Custom Message")
        print("5. Exit")
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == "1":
            send_test_sms()
            
        elif choice == "2":
            patient_name = input("Enter patient name (or press Enter for 'Test Patient'): ").strip()
            if not patient_name:
                patient_name = "Test Patient"
            send_reminder_sms(patient_name)
            
        elif choice == "3":
            send_feedback_notification()
            
        elif choice == "4":
            custom_message = input("Enter your custom message: ").strip()
            custom_number = input("Enter phone number (or press Enter to use default): ").strip()
            if not custom_message:
                print("❌ Message cannot be empty!")
                continue
            send_test_sms(custom_message, custom_number if custom_number else None)
            
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice! Please select 1-5.")

if __name__ == "__main__":
    print("🚀 CareChat SMS Testing Script")
    print("=" * 50)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if running in interactive mode
    if len(sys.argv) > 1:
        if sys.argv[1] == "--basic":
            send_test_sms()
        elif sys.argv[1] == "--reminder":
            send_reminder_sms()
        elif sys.argv[1] == "--feedback":
            send_feedback_notification()
        else:
            print(f"❌ Unknown argument: {sys.argv[1]}")
            print("Available options: --basic, --reminder, --feedback")
    else:
        # Run interactive mode
        interactive_sms_test()
    
    print("\n✅ SMS testing complete!")