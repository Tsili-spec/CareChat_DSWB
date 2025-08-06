#!/usr/bin/env python3
"""
SMS Diagnostic Script for CareChat Backend
Diagnoses SMS delivery issues and checks Twilio account status
"""

import os
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime, timedelta
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
    
    return config

def check_twilio_account_status():
    """Check Twilio account status and balance"""
    print("🔍 Checking Twilio Account Status")
    print("=" * 40)
    
    config = load_twilio_config()
    if not config['account_sid']:
        print("❌ Missing Twilio configuration!")
        return False
    
    try:
        client = Client(config['account_sid'], config['auth_token'])
        
        # Get account information
        account = client.api.accounts(config['account_sid']).fetch()
        print(f"✅ Account Status: {account.status}")
        print(f"   Account Type: {account.type}")
        print(f"   Account SID: {account.sid}")
        
        # Get account balance (if available)
        try:
            balance = client.balance.fetch()
            print(f"   Account Balance: {balance.currency} {balance.balance}")
        except Exception as e:
            print(f"   Account Balance: Unable to fetch ({str(e)[:50]}...)")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to check account status!")
        print(f"   Error: {str(e)}")
        return False

def check_phone_number_validity():
    """Check if phone numbers are valid"""
    print("\n📱 Checking Phone Number Validity")
    print("=" * 40)
    
    config = load_twilio_config()
    
    try:
        client = Client(config['account_sid'], config['auth_token'])
        
        # Check Twilio number
        print(f"📞 Checking Twilio Number: {config['twilio_number']}")
        try:
            incoming_phone_number = client.incoming_phone_numbers.list(
                phone_number=config['twilio_number']
            )
            if incoming_phone_number:
                number_info = incoming_phone_number[0]
                print(f"   ✅ Twilio Number Valid")
                print(f"   Capabilities: SMS={number_info.capabilities['sms']}, Voice={number_info.capabilities['voice']}")
                print(f"   Status: {number_info.status if hasattr(number_info, 'status') else 'Active'}")
            else:
                print(f"   ❌ Twilio Number not found in your account!")
                return False
        except Exception as e:
            print(f"   ❌ Error checking Twilio number: {str(e)}")
        
        # Check destination number format
        print(f"\n📱 Checking Destination Number: {config['my_number']}")
        if config['my_number'].startswith('+'):
            print("   ✅ Number has international format (+)")
        else:
            print("   ⚠️  Number missing '+' prefix - this might cause issues")
        
        if len(config['my_number']) >= 10:
            print("   ✅ Number length appears valid")
        else:
            print("   ❌ Number appears too short")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to check phone numbers!")
        print(f"   Error: {str(e)}")
        return False

def check_recent_messages():
    """Check recent SMS messages and their delivery status"""
    print("\n📨 Checking Recent SMS Messages")
    print("=" * 40)
    
    config = load_twilio_config()
    
    try:
        client = Client(config['account_sid'], config['auth_token'])
        
        # Get messages from the last 24 hours
        date_sent_after = datetime.now() - timedelta(hours=24)
        
        messages = client.messages.list(
            date_sent_after=date_sent_after,
            limit=10
        )
        
        if not messages:
            print("   📭 No messages found in the last 24 hours")
            return True
        
        print(f"   📋 Found {len(messages)} recent messages:")
        
        for i, message in enumerate(messages, 1):
            print(f"\n   {i}. Message SID: {message.sid}")
            print(f"      From: {message.from_}")
            print(f"      To: {message.to}")
            print(f"      Status: {message.status}")
            print(f"      Direction: {message.direction}")
            print(f"      Date: {message.date_sent}")
            print(f"      Error Code: {message.error_code if message.error_code else 'None'}")
            print(f"      Error Message: {message.error_message if message.error_message else 'None'}")
            print(f"      Body: {message.body[:50]}...")
            
            # Check for common issues
            if message.status == 'failed':
                print(f"      ❌ FAILED: {message.error_message}")
            elif message.status == 'undelivered':
                print(f"      ⚠️  UNDELIVERED: Check recipient number")
            elif message.status == 'delivered':
                print(f"      ✅ DELIVERED successfully")
            elif message.status in ['queued', 'sent']:
                print(f"      ⏳ IN PROGRESS: Message is being processed")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to check recent messages!")
        print(f"   Error: {str(e)}")
        return False

def send_diagnostic_sms():
    """Send a diagnostic SMS with special formatting"""
    print("\n🧪 Sending Diagnostic SMS")
    print("=" * 30)
    
    config = load_twilio_config()
    
    try:
        client = Client(config['account_sid'], config['auth_token'])
        
        # Simple, clean message for testing
        diagnostic_message = f"TEST SMS from CareChat at {datetime.now().strftime('%H:%M:%S')}. If you receive this, SMS is working!"
        
        print(f"📤 Sending simplified test message...")
        print(f"   To: {config['my_number']}")
        print(f"   From: {config['twilio_number']}")
        print(f"   Message: {diagnostic_message}")
        
        message = client.messages.create(
            body=diagnostic_message,
            from_=config['twilio_number'],
            to=config['my_number']
        )
        
        print(f"\n✅ Diagnostic SMS sent!")
        print(f"   Message SID: {message.sid}")
        print(f"   Initial Status: {message.status}")
        
        # Wait a moment and check status
        print(f"\n⏳ Waiting 5 seconds to check updated status...")
        import time
        time.sleep(5)
        
        # Fetch updated message status
        updated_message = client.messages(message.sid).fetch()
        print(f"   Updated Status: {updated_message.status}")
        
        if updated_message.error_code:
            print(f"   ❌ Error Code: {updated_message.error_code}")
            print(f"   ❌ Error Message: {updated_message.error_message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send diagnostic SMS!")
        print(f"   Error: {str(e)}")
        return False

def print_troubleshooting_tips():
    """Print troubleshooting tips"""
    print("\n🛠️ Troubleshooting Tips")
    print("=" * 30)
    print("If you're not receiving SMS messages, check:")
    print("")
    print("1. 📱 Phone Number Format:")
    print("   • Ensure your number has the '+' prefix")
    print("   • Include country code (e.g., +237 for Cameroon)")
    print("   • Example: +237679977660")
    print("")
    print("2. 🏥 Twilio Account Status:")
    print("   • Check if account is active (not trial expired)")
    print("   • Verify account balance for paid accounts")
    print("   • Check if numbers are verified (for trial accounts)")
    print("")
    print("3. 📶 Network Issues:")
    print("   • Check phone signal strength")
    print("   • Try different networks if possible")
    print("   • SMS might take a few minutes to arrive")
    print("")
    print("4. 🚫 Carrier Blocking:")
    print("   • Some carriers block international SMS")
    print("   • Try with a different phone number")
    print("   • Contact your mobile provider")
    print("")
    print("5. 📞 Twilio Trial Limitations:")
    print("   • Trial accounts can only send to verified numbers")
    print("   • Add/verify your number at console.twilio.com")
    print("")

if __name__ == "__main__":
    print("🔧 CareChat SMS Diagnostic Tool")
    print("=" * 50)
    print(f"⏰ Diagnostic Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all diagnostic checks
    print("\n🚀 Running comprehensive SMS diagnostics...\n")
    
    # Check 1: Account Status
    account_ok = check_twilio_account_status()
    
    # Check 2: Phone Number Validity
    numbers_ok = check_phone_number_validity()
    
    # Check 3: Recent Messages
    messages_ok = check_recent_messages()
    
    # Check 4: Send Diagnostic SMS
    if account_ok and numbers_ok:
        diagnostic_ok = send_diagnostic_sms()
    else:
        diagnostic_ok = False
        print("\n⏭️  Skipping diagnostic SMS due to configuration issues")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"✅ Account Status: {'OK' if account_ok else 'FAILED'}")
    print(f"✅ Phone Numbers: {'OK' if numbers_ok else 'FAILED'}")
    print(f"✅ Recent Messages: {'OK' if messages_ok else 'FAILED'}")
    print(f"✅ Diagnostic SMS: {'SENT' if diagnostic_ok else 'FAILED'}")
    
    if not all([account_ok, numbers_ok, messages_ok]):
        print("\n❌ Issues detected! See details above.")
    else:
        print("\n✅ All diagnostics passed! SMS should be working.")
        print("   If you're still not receiving messages, check the tips below.")
    
    # Always show troubleshooting tips
    print_troubleshooting_tips()
    
    print("\n✅ Diagnostic complete!")
