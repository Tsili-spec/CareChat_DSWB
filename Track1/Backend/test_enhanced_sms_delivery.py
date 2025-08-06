#!/usr/bin/env python3
"""
Enhanced SMS Test with Delivery Verification
Sends SMS and actively monitors Twilio delivery status
"""

import os
import sys
import requests
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_sms_delivery_status(message_sid):
    """Check the delivery status of a sent SMS"""
    print(f"\n🔍 Checking delivery status for Message SID: {message_sid}")
    
    try:
        # Import Twilio client
        from twilio.rest import Client
        
        # Get Twilio credentials
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            print("❌ Twilio credentials not found")
            return None
        
        client = Client(account_sid, auth_token)
        
        # Fetch message details
        message = client.messages(message_sid).fetch()
        
        print(f"📊 Message Status Details:")
        print(f"   SID: {message.sid}")
        print(f"   Status: {message.status}")
        print(f"   To: {message.to}")
        print(f"   From: {message.from_}")
        print(f"   Date Created: {message.date_created}")
        print(f"   Date Sent: {message.date_sent}")
        print(f"   Date Updated: {message.date_updated}")
        print(f"   Direction: {message.direction}")
        print(f"   Price: {message.price} {message.price_unit}")
        print(f"   Number of Segments: {message.num_segments}")
        print(f"   Number of Media: {message.num_media}")
        
        if message.error_code:
            print(f"   ❌ Error Code: {message.error_code}")
            print(f"   ❌ Error Message: {message.error_message}")
        
        # Interpret status
        status_meanings = {
            'queued': '📝 Message is queued and will be sent shortly',
            'sending': '🚀 Message is currently being sent',
            'sent': '📤 Message has been sent to carrier',
            'delivered': '✅ Message was successfully delivered',
            'undelivered': '❌ Message failed to be delivered',
            'failed': '❌ Message failed to send',
            'received': '✅ Message was received (for incoming messages)',
            'accepted': '📝 Message accepted by Twilio',
            'scheduled': '⏰ Message is scheduled for future delivery',
            'canceled': '❌ Message was canceled',
            'unknown': '❓ Status unknown'
        }
        
        status_explanation = status_meanings.get(message.status, f"❓ Unknown status: {message.status}")
        print(f"   📋 Status Meaning: {status_explanation}")
        
        return message.status, message.error_code, message.error_message
        
    except Exception as e:
        print(f"❌ Error checking delivery status: {str(e)}")
        return None, None, str(e)

def send_sms_with_delivery_tracking():
    """Send SMS and monitor its delivery status"""
    
    print("📱 Enhanced SMS Test with Delivery Tracking")
    print("=" * 55)
    
    # Get phone number from environment
    recipient_phone = os.getenv('MY_NUMBER')
    if not recipient_phone:
        print("❌ MY_NUMBER not found in .env file")
        return False
    
    print(f"📱 SMS will be sent to: {recipient_phone}")
    
    base_url = "http://localhost:8000/api"
    patient_id = "089d2b4b-d03f-4bca-b827-8fae840cc3e5"
    
    # Check API status
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
    
    # Create and send SMS
    print("\n2️⃣ Creating and Sending SMS...")
    now = datetime.utcnow()
    current_day = now.strftime("%A")
    
    reminder_data = {
        "patient_id": patient_id,
        "title": "Delivery Test",
        "message": f"CareChat delivery test sent at {now.strftime('%H:%M:%S')} UTC. Testing delivery tracking. Reply with 'RECEIVED' if you get this message.",
        "scheduled_time": [now.isoformat() + "Z"],
        "days": [current_day],
        "status": "active"
    }
    
    try:
        # Create reminder
        response = requests.post(f"{base_url}/reminder/", json=reminder_data)
        if response.status_code == 200:
            reminder = response.json()
            reminder_id = reminder['reminder_id']
            print(f"✅ Reminder created: {reminder_id}")
            
            # Send SMS immediately
            send_response = requests.post(f"{base_url}/reminder/{reminder_id}/send-sms")
            if send_response.status_code == 200:
                result = send_response.json()
                print(f"✅ SMS API call successful!")
                print(f"   Message SID: {result.get('message_sid')}")
                print(f"   Initial Status: {result.get('status')}")
                print(f"   Patient: {result.get('patient_name')}")
                print(f"   Phone: {result.get('phone_number')}")
                
                message_sid = result.get('message_sid')
                if message_sid:
                    # Wait a moment for initial processing
                    print(f"\n3️⃣ Waiting 5 seconds for initial processing...")
                    time.sleep(5)
                    
                    # Check delivery status immediately
                    status, error_code, error_message = check_sms_delivery_status(message_sid)
                    
                    # If not delivered yet, wait and check again
                    if status and status not in ['delivered', 'failed', 'undelivered']:
                        print(f"\n4️⃣ Waiting 15 seconds for carrier delivery...")
                        time.sleep(15)
                        
                        print(f"\n5️⃣ Checking final delivery status...")
                        final_status, final_error_code, final_error_message = check_sms_delivery_status(message_sid)
                        
                        if final_status == 'delivered':
                            print(f"\n🎉 SUCCESS: SMS was delivered!")
                            print(f"📱 Check your phone ({recipient_phone}) now!")
                        elif final_status in ['failed', 'undelivered']:
                            print(f"\n❌ FAILURE: SMS was not delivered")
                            print(f"   Error Code: {final_error_code}")
                            print(f"   Error Message: {final_error_message}")
                        else:
                            print(f"\n⏳ PENDING: SMS status is still '{final_status}'")
                            print(f"   This may take a few more minutes to process")
                    
                    return True
                else:
                    print("❌ No Message SID returned")
                    return False
            else:
                print(f"❌ Failed to send SMS: {send_response.text}")
                return False
        else:
            print(f"❌ Failed to create reminder: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error in SMS test: {str(e)}")
        return False

def diagnose_sms_issues():
    """Diagnose potential SMS delivery issues"""
    
    print("\n🔧 SMS Delivery Diagnostics")
    print("=" * 35)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    twilio_account = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('TWILIO_NUMBER')
    my_number = os.getenv('MY_NUMBER')
    
    print(f"   TWILIO_ACCOUNT_SID: {'✅ Set' if twilio_account else '❌ Missing'}")
    print(f"   TWILIO_AUTH_TOKEN: {'✅ Set' if twilio_token else '❌ Missing'}")
    print(f"   TWILIO_NUMBER: {twilio_number if twilio_number else '❌ Missing'}")
    print(f"   MY_NUMBER: {my_number if my_number else '❌ Missing'}")
    
    if not all([twilio_account, twilio_token, twilio_number, my_number]):
        print("\n❌ Missing required environment variables!")
        return False
    
    # Test Twilio connection
    print(f"\n🔗 Testing Twilio Connection...")
    try:
        from twilio.rest import Client
        client = Client(twilio_account, twilio_token)
        
        # Get account info
        account = client.api.accounts(twilio_account).fetch()
        print(f"✅ Connected to Twilio account: {account.friendly_name}")
        print(f"   Account Status: {account.status}")
        
        # Check phone number
        try:
            phone_number = client.incoming_phone_numbers.list(phone_number=twilio_number)
            if phone_number:
                print(f"✅ Twilio number {twilio_number} is valid")
            else:
                print(f"⚠️  Warning: {twilio_number} not found in account")
        except Exception as e:
            print(f"⚠️  Could not verify phone number: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Twilio: {str(e)}")
        return False

def check_recent_sms_logs():
    """Check recent SMS delivery logs"""
    
    print(f"\n📋 Recent SMS Logs from CareChat:")
    print("-" * 40)
    
    try:
        # Read recent log entries
        with open('logs/carechat_api.log', 'r') as f:
            lines = f.readlines()
        
        # Filter SMS-related logs from last 10 minutes
        sms_logs = []
        for line in lines[-100:]:  # Check last 100 lines
            if any(keyword in line.lower() for keyword in ['sms', 'twilio', 'message']):
                sms_logs.append(line.strip())
        
        if sms_logs:
            for log in sms_logs[-10:]:  # Show last 10 SMS-related logs
                print(f"   {log}")
        else:
            print("   No recent SMS logs found")
            
    except Exception as e:
        print(f"❌ Error reading logs: {str(e)}")

if __name__ == "__main__":
    print("🧪 CareChat Enhanced SMS Delivery Test")
    print("🎯 This script will send SMS and actively verify delivery")
    
    choice = input("\nChoose action:\n1. Send SMS with delivery tracking\n2. Run SMS diagnostics\n3. Check recent logs\n4. All of the above\nEnter choice (1/2/3/4): ").strip()
    
    if choice == "1":
        success = send_sms_with_delivery_tracking()
    elif choice == "2":
        success = diagnose_sms_issues()
    elif choice == "3":
        check_recent_sms_logs()
        success = True
    elif choice == "4":
        print("\n" + "="*50)
        print("1. RUNNING SMS DIAGNOSTICS:")
        diag_success = diagnose_sms_issues()
        
        print("\n" + "="*50)
        print("2. CHECKING RECENT LOGS:")
        check_recent_sms_logs()
        
        print("\n" + "="*50)
        print("3. SENDING SMS WITH TRACKING:")
        sms_success = send_sms_with_delivery_tracking()
        
        success = diag_success and sms_success
    else:
        print("❌ Invalid choice")
        success = False
    
    if success:
        print("\n✅ Test completed!")
    else:
        print("\n❌ Test had issues!")
    
    print(f"\n💡 Tips for better SMS delivery:")
    print("   - Ensure your phone number is verified in Twilio")
    print("   - Check your Twilio account balance")
    print("   - Verify your phone can receive SMS from other sources")
    print("   - Check if messages are going to spam/blocked folder")
    print("   - Try with a different phone number if available")
