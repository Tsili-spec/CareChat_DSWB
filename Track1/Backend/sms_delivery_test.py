#!/usr/bin/env python3
"""
Enhanced SMS Test with Delivery Status Tracking
"""

import os
import time
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime

def send_and_track_sms():
    """Send SMS and track its delivery status"""
    print("📱 Enhanced SMS Test with Delivery Tracking")
    print("=" * 50)
    
    # Load configuration
    load_dotenv()
    config = {
        'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
        'auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
        'twilio_number': os.getenv('TWILIO_NUMBER'),
        'my_number': os.getenv('MY_NUMBER')
    }
    
    try:
        client = Client(config['account_sid'], config['auth_token'])
        
        # Send a simple, clean message
        timestamp = datetime.now().strftime("%H:%M:%S")
        simple_message = f"CareChat test message sent at {timestamp}. Reply STOP to opt out."
        
        print(f"📤 Sending simple test message...")
        print(f"   To: {config['my_number']}")
        print(f"   From: {config['twilio_number']}")
        print(f"   Message: {simple_message}")
        
        # Send the message
        message = client.messages.create(
            body=simple_message,
            from_=config['twilio_number'],
            to=config['my_number']
        )
        
        print(f"\n✅ Message sent successfully!")
        print(f"   Message SID: {message.sid}")
        print(f"   Initial Status: {message.status}")
        
        # Track delivery status
        print(f"\n⏳ Tracking delivery status...")
        for i in range(6):  # Check for 30 seconds (6 times, 5 seconds each)
            time.sleep(5)
            
            # Fetch updated status
            updated_message = client.messages(message.sid).fetch()
            status = updated_message.status
            
            print(f"   Check {i+1}/6: Status = {status}")
            
            if status == 'delivered':
                print(f"   🎉 SUCCESS! Message delivered successfully!")
                break
            elif status == 'failed':
                print(f"   ❌ FAILED! Error: {updated_message.error_message}")
                print(f"   Error Code: {updated_message.error_code}")
                break
            elif status in ['undelivered']:
                print(f"   ⚠️  Message undelivered")
                break
            elif status in ['queued', 'sent']:
                print(f"   ⏳ Still in progress...")
                continue
            else:
                print(f"   ℹ️  Status: {status}")
        
        # Final status check
        final_message = client.messages(message.sid).fetch()
        print(f"\n📊 Final Status Report:")
        print(f"   Status: {final_message.status}")
        print(f"   Date Sent: {final_message.date_sent}")
        print(f"   Date Updated: {final_message.date_updated}")
        print(f"   Price: {final_message.price} {final_message.price_unit}")
        print(f"   Error Code: {final_message.error_code or 'None'}")
        print(f"   Error Message: {final_message.error_message or 'None'}")
        
        if final_message.status == 'delivered':
            print(f"\n🎉 SUCCESS! Check your phone for the message!")
        else:
            print(f"\n⚠️  Message not delivered. Status: {final_message.status}")
        
        return final_message.status == 'delivered'
        
    except Exception as e:
        print(f"❌ Error sending/tracking SMS: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"🚀 SMS Delivery Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    success = send_and_track_sms()
    
    if success:
        print(f"\n✅ SMS test completed successfully!")
    else:
        print(f"\n❌ SMS test failed - check output above for details")
