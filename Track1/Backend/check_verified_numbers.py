#!/usr/bin/env python3
"""
Check if phone number is verified for Twilio trial account
"""

import os
from dotenv import load_dotenv
from twilio.rest import Client

def check_verified_numbers():
    """Check verified caller IDs"""
    load_dotenv()
    
    config = {
        'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
        'auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
        'my_number': os.getenv('MY_NUMBER')
    }
    
    try:
        client = Client(config['account_sid'], config['auth_token'])
        
        print("🔍 Checking Verified Caller IDs")
        print("=" * 40)
        
        # Get verified caller IDs
        verified_numbers = client.outgoing_caller_ids.list()
        
        print(f"📋 Found {len(verified_numbers)} verified numbers:")
        
        target_number = config['my_number']
        is_verified = False
        
        for number in verified_numbers:
            print(f"   ✅ {number.phone_number}")
            if number.phone_number == target_number:
                is_verified = True
        
        print(f"\n🎯 Target number: {target_number}")
        if is_verified:
            print("   ✅ This number IS verified - SMS should work!")
        else:
            print("   ❌ This number is NOT verified - this is why SMS fails!")
            print(f"\n📝 To fix this:")
            print(f"   1. Go to console.twilio.com")
            print(f"   2. Phone Numbers > Manage > Verified Caller IDs")
            print(f"   3. Add and verify: {target_number}")
        
        return is_verified
        
    except Exception as e:
        print(f"❌ Error checking verified numbers: {str(e)}")
        return False

if __name__ == "__main__":
    check_verified_numbers()
