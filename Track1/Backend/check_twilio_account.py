#!/usr/bin/env python3
"""
Twilio Account Status and Trial Limitations Checker
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_twilio_account_status():
    """Check Twilio account status and trial limitations"""
    
    print("🔍 Twilio Account Status Check")
    print("=" * 35)
    
    try:
        from twilio.rest import Client
        
        # Get Twilio credentials
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            print("❌ Twilio credentials not found")
            return False
        
        client = Client(account_sid, auth_token)
        
        # Get account information
        account = client.api.accounts(account_sid).fetch()
        
        print(f"📋 Account Information:")
        print(f"   Account SID: {account.sid}")
        print(f"   Friendly Name: {account.friendly_name}")
        print(f"   Status: {account.status}")
        print(f"   Type: {account.type}")
        print(f"   Created: {account.date_created}")
        print(f"   Updated: {account.date_updated}")
        
        # Check if it's a trial account
        if account.type.lower() == 'trial':
            print(f"\n⚠️  TRIAL ACCOUNT DETECTED!")
            print(f"   Your Twilio account is in trial mode with the following restrictions:")
            print(f"   📵 Can only send SMS to verified phone numbers")
            print(f"   💰 Limited balance and free credits")
            print(f"   🔒 Geographic restrictions may apply")
            
            # Get verified phone numbers
            print(f"\n📱 Checking Verified Phone Numbers:")
            try:
                verified_numbers = client.outgoing_caller_ids.list()
                if verified_numbers:
                    print(f"   Verified numbers:")
                    for number in verified_numbers:
                        print(f"     📞 {number.phone_number} - {number.friendly_name}")
                else:
                    print(f"   ❌ No verified phone numbers found!")
                    print(f"   🔧 You need to verify +237679977660 in your Twilio console")
            except Exception as e:
                print(f"   ❌ Could not fetch verified numbers: {str(e)}")
        
        # Check account balance
        try:
            balance = client.balance.fetch()
            print(f"\n💰 Account Balance:")
            print(f"   Balance: ${balance.balance} {balance.currency}")
            
            if float(balance.balance) <= 0:
                print(f"   ⚠️  Warning: Account balance is $0 or negative")
                print(f"   💳 You may need to add funds to your account")
        except Exception as e:
            print(f"\n❌ Could not fetch balance: {str(e)}")
        
        # Get phone numbers owned
        try:
            phone_numbers = client.incoming_phone_numbers.list()
            print(f"\n📞 Your Twilio Phone Numbers:")
            for number in phone_numbers:
                print(f"   📱 {number.phone_number}")
                print(f"      Friendly Name: {number.friendly_name}")
                print(f"      Capabilities: SMS={number.capabilities['sms']}, Voice={number.capabilities['voice']}")
        except Exception as e:
            print(f"\n❌ Could not fetch phone numbers: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking Twilio account: {str(e)}")
        return False

def check_phone_verification_status():
    """Check if the target phone number is verified"""
    
    print(f"\n🔍 Phone Number Verification Check")
    print("=" * 40)
    
    my_number = os.getenv('MY_NUMBER')
    if not my_number:
        print("❌ MY_NUMBER not found in environment")
        return False
    
    print(f"📱 Checking verification status for: {my_number}")
    
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)
        
        # Check if number is in verified outgoing caller IDs
        verified_numbers = client.outgoing_caller_ids.list()
        
        is_verified = False
        for number in verified_numbers:
            if number.phone_number == my_number:
                print(f"✅ {my_number} is VERIFIED")
                print(f"   Friendly Name: {number.friendly_name}")
                print(f"   Date Created: {number.date_created}")
                is_verified = True
                break
        
        if not is_verified:
            print(f"❌ {my_number} is NOT VERIFIED")
            print(f"\n🔧 How to verify your phone number:")
            print(f"   1. Go to https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
            print(f"   2. Click 'Add a new caller ID'")
            print(f"   3. Enter {my_number}")
            print(f"   4. Follow the verification process (you'll receive a call or SMS)")
            print(f"   5. Complete verification and try again")
        
        return is_verified
        
    except Exception as e:
        print(f"❌ Error checking verification: {str(e)}")
        return False

def show_solutions():
    """Show solutions for trial account limitations"""
    
    print(f"\n💡 Solutions for Trial Account Limitations:")
    print("=" * 45)
    
    print(f"1️⃣  VERIFY YOUR PHONE NUMBER:")
    print(f"   - Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
    print(f"   - Add and verify +237679977660")
    print(f"   - This allows trial accounts to send SMS to verified numbers")
    
    print(f"\n2️⃣  UPGRADE YOUR ACCOUNT:")
    print(f"   - Go to: https://console.twilio.com/us1/account/billing")
    print(f"   - Add a payment method and upgrade from trial")
    print(f"   - This removes geographic and verification restrictions")
    
    print(f"\n3️⃣  ADD ACCOUNT BALANCE:")
    print(f"   - Go to: https://console.twilio.com/us1/account/billing")
    print(f"   - Add funds to your account (minimum $1-5)")
    print(f"   - SMS typically costs $0.0075 per message")
    
    print(f"\n4️⃣  TEST WITH VERIFIED NUMBER:")
    print(f"   - If you have other verified numbers, test with those first")
    print(f"   - This confirms your SMS setup is working")
    
    print(f"\n⚡ QUICK TEST:")
    print(f"   After verification, run: python3 test_enhanced_sms_delivery.py")

if __name__ == "__main__":
    print("🧪 Twilio Account & Trial Limitations Checker")
    print("=" * 50)
    
    # Check account status
    account_ok = check_twilio_account_status()
    
    if account_ok:
        # Check phone verification
        phone_verified = check_phone_verification_status()
        
        # Show solutions
        show_solutions()
        
        if not phone_verified:
            print(f"\n⚠️  NEXT STEPS:")
            print(f"   1. Verify +237679977660 in Twilio Console")
            print(f"   2. Re-run this script to confirm verification")
            print(f"   3. Test SMS delivery again")
    
    print(f"\n🔗 Useful Twilio Console Links:")
    print(f"   - Verified Numbers: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
    print(f"   - Account Billing: https://console.twilio.com/us1/account/billing")
    print(f"   - SMS Logs: https://console.twilio.com/us1/monitor/logs/sms")
    print(f"   - Account Settings: https://console.twilio.com/us1/account/settings")
