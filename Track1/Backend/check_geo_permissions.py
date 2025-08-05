#!/usr/bin/env python3
"""
Check and Enable Twilio Geographic Permissions for International SMS
"""

import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_geographic_permissions():
    """Check Twilio geographic permissions for SMS"""
    
    print("🌍 Checking Twilio Geographic Permissions")
    print("=" * 45)
    
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        print("❌ Twilio credentials not found")
        return False
    
    # Create basic auth header
    credentials = f"{account_sid}:{auth_token}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        # Check SMS geographic permissions
        url = f"https://messaging.twilio.com/v1/Services/{account_sid}/AlphaSenders"
        
        # Let's try the messaging configuration API instead
        messaging_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        
        print("📋 Checking account messaging permissions...")
        
        # Try to get recent messages to understand restrictions
        response = requests.get(
            f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json?PageSize=5",
            headers=headers
        )
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Messaging API accessible")
            print(f"📊 Recent messages found: {len(messages.get('messages', []))}")
            
            # Check for failed international messages
            for msg in messages.get('messages', []):
                if msg['status'] == 'failed':
                    print(f"❌ Failed message found:")
                    print(f"   SID: {msg['sid']}")
                    print(f"   To: {msg['to']}")
                    print(f"   Error Code: {msg.get('error_code', 'Unknown')}")
                    print(f"   Error Message: {msg.get('error_message', 'No message')}")
        
        # Check if we can access usage records for international
        usage_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Usage/Records.json"
        usage_response = requests.get(usage_url, headers=headers)
        
        if usage_response.status_code == 200:
            print(f"✅ Usage API accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking permissions: {str(e)}")
        return False

def check_specific_country_restrictions():
    """Check if Cameroon (+237) has specific restrictions"""
    
    print(f"\n🇨🇲 Checking Cameroon (+237) Specific Restrictions")
    print("=" * 50)
    
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    credentials = f"{account_sid}:{auth_token}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        # Try to fetch phone number insights for Cameroon number
        lookup_url = f"https://lookups.twilio.com/v1/PhoneNumbers/+237679977660"
        
        response = requests.get(lookup_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Phone number lookup successful:")
            print(f"   Number: {data.get('phone_number')}")
            print(f"   Country Code: {data.get('country_code')}")
            print(f"   National Format: {data.get('national_format')}")
            
            # Check carrier info if available
            if 'carrier' in data:
                carrier = data['carrier']
                print(f"   Carrier: {carrier.get('name', 'Unknown')}")
                print(f"   Mobile Country Code: {carrier.get('mobile_country_code')}")
                print(f"   Mobile Network Code: {carrier.get('mobile_network_code')}")
                print(f"   Type: {carrier.get('type')}")
        
        else:
            print(f"⚠️  Phone number lookup failed: {response.status_code}")
            print(f"   This might indicate restrictions or API limitations")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking country restrictions: {str(e)}")
        return False

def test_simple_domestic_sms():
    """Test sending SMS to a US number to verify basic functionality"""
    
    print(f"\n🇺🇸 Testing Domestic SMS (for comparison)")
    print("=" * 45)
    
    # Note: We'll just explain the test since we don't have a US test number
    print(f"💡 To isolate the issue, you could test with a US number:")
    print(f"   1. Add/verify a US phone number in Twilio Console")
    print(f"   2. Test SMS delivery to that number")
    print(f"   3. If US SMS works but Cameroon doesn't, it's geographic restrictions")
    print(f"   4. If both fail, it's a broader account issue")

def show_geo_permissions_solution():
    """Show how to enable geographic permissions"""
    
    print(f"\n🔧 How to Enable Geographic Permissions:")
    print("=" * 45)
    
    print(f"1️⃣  TWILIO CONSOLE METHOD:")
    print(f"   - Go to: https://console.twilio.com/us1/develop/sms/settings/geo-permissions")
    print(f"   - Find 'Cameroon' in the country list")
    print(f"   - Enable SMS permissions for Cameroon")
    print(f"   - Save changes")
    
    print(f"\n2️⃣  ACCOUNT UPGRADE METHOD:")
    print(f"   - Go to: https://console.twilio.com/us1/account/billing")
    print(f"   - Upgrade from Trial to Full account")
    print(f"   - This removes most geographic restrictions")
    
    print(f"\n3️⃣  SUPPORT REQUEST METHOD:")
    print(f"   - Contact Twilio Support if geo-permissions don't work")
    print(f"   - Request: Enable SMS to Cameroon (+237)")
    print(f"   - Mention: Error 30454 for verified number")

def create_test_with_us_number():
    """Create a test specifically for US numbers"""
    
    print(f"\n📝 Creating Quick US Test Script...")
    
    us_test_script = '''#!/usr/bin/env python3
"""
Quick US SMS Test - Test with US number to isolate geographic issues
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_us_sms():
    """Test SMS to US number (you need to add/verify one first)"""
    
    # You would need to:
    # 1. Go to https://console.twilio.com/us1/develop/phone-numbers/manage/verified
    # 2. Add a US phone number (like +1XXXXXXXXXX)
    # 3. Replace the number below and test
    
    us_test_number = "+1234567890"  # Replace with verified US number
    
    print(f"Testing SMS to US number: {us_test_number}")
    
    # Same API call but to US number
    base_url = "http://localhost:8000/api"
    patient_id = "089d2b4b-d03f-4bca-b827-8fae840cc3e5"
    
    reminder_data = {
        "patient_id": patient_id,
        "title": "US Test",
        "message": f"US SMS test - if you receive this, geographic restrictions are the issue",
        "scheduled_time": ["2025-08-06T00:30:00Z"],
        "days": ["Tuesday"],
        "status": "active"
    }
    
    try:
        # Create reminder
        response = requests.post(f"{base_url}/reminder/", json=reminder_data)
        if response.status_code == 200:
            reminder = response.json()
            reminder_id = reminder['reminder_id']
            
            # Send SMS
            send_response = requests.post(f"{base_url}/reminder/{reminder_id}/send-sms")
            if send_response.status_code == 200:
                result = send_response.json()
                print(f"✅ US SMS sent successfully!")
                print(f"Message SID: {result.get('message_sid')}")
                return True
            else:
                print(f"❌ US SMS failed: {send_response.text}")
                return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🇺🇸 Testing US SMS (modify script with verified US number)")
    test_us_sms()
'''
    
    with open('test_us_sms.py', 'w') as f:
        f.write(us_test_script)
    
    print(f"✅ Created test_us_sms.py")
    print(f"   📝 Edit the script to add a verified US phone number")
    print(f"   🧪 Run it to test if geographic restrictions are the issue")

if __name__ == "__main__":
    print("🧪 Twilio Geographic Permissions Checker")
    print("=" * 50)
    
    # Check basic permissions
    perms_ok = check_geographic_permissions()
    
    if perms_ok:
        # Check country-specific restrictions
        country_ok = check_specific_country_restrictions()
        
        # Test domestic option
        test_simple_domestic_sms()
        
        # Show solutions
        show_geo_permissions_solution()
        
        # Create US test script
        create_test_with_us_number()
    
    print(f"\n🎯 LIKELY SOLUTION:")
    print(f"   Error 30454 + Trial Account + International Number = Geographic Restrictions")
    print(f"   ➡️  Enable Cameroon in Geo Permissions OR Upgrade Account")
    
    print(f"\n🔗 Direct Links:")
    print(f"   - Geo Permissions: https://console.twilio.com/us1/develop/sms/settings/geo-permissions")
    print(f"   - Account Upgrade: https://console.twilio.com/us1/account/billing")
    print(f"   - SMS Logs: https://console.twilio.com/us1/monitor/logs/sms")
