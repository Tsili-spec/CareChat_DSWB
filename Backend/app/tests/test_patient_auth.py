import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# Test data
signup_data = {
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+237123456789",
    "email": "testuser@example.com",
    "preferred_language": "en",
    "password": "TestPassword123"
}

print("🚀 Testing CareChat Patient Authentication System")
print("=" * 50)

# Test 1: Signup
print("\n1️⃣ Testing Patient Signup...")
try:
    signup_resp = requests.post(f"{BASE_URL}/signup", json=signup_data)
    print(f"   Status Code: {signup_resp.status_code}")
    
    if signup_resp.status_code == 201:
        patient_data = signup_resp.json()
        print(f"   ✅ Signup successful!")
        print(f"   Patient ID: {patient_data.get('patient_id')}")
        print(f"   Name: {patient_data.get('first_name')} {patient_data.get('last_name')}")
    else:
        print(f"   ❌ Signup failed: {signup_resp.text}")
        
except Exception as e:
    print(f"   ❌ Signup error: {str(e)}")

# Test 2: Login
print("\n2️⃣ Testing Patient Login...")
login_data = {
    "phone_number": signup_data["phone_number"],
    "password": signup_data["password"]
}

try:
    login_resp = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"   Status Code: {login_resp.status_code}")
    
    if login_resp.status_code == 200:
        login_result = login_resp.json()
        access_token = login_result.get("access_token")
        refresh_token = login_result.get("refresh_token")
        
        print(f"   ✅ Login successful!")
        print(f"   Token Type: {login_result.get('token_type')}")
        print(f"   Expires In: {login_result.get('expires_in')} seconds")
        print(f"   Access Token: {access_token[:20]}...")
        print(f"   Patient: {login_result.get('patient', {}).get('first_name')}")
        
        # Test 3: Access protected endpoint
        print("\n3️⃣ Testing Protected Endpoint (/me)...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            me_resp = requests.get(f"{BASE_URL}/me", headers=headers)
            print(f"   Status Code: {me_resp.status_code}")
            
            if me_resp.status_code == 200:
                me_data = me_resp.json()
                print(f"   ✅ Protected endpoint access successful!")
                print(f"   Patient ID: {me_data.get('patient_id')}")
                print(f"   Phone: {me_data.get('phone_number')}")
            else:
                print(f"   ❌ Protected endpoint failed: {me_resp.text}")
                
        except Exception as e:
            print(f"   ❌ Protected endpoint error: {str(e)}")
        
        # Test 4: Refresh token
        print("\n4️⃣ Testing Token Refresh...")
        refresh_data = {"refresh_token": refresh_token}
        
        try:
            refresh_resp = requests.post(f"{BASE_URL}/refresh", json=refresh_data)
            print(f"   Status Code: {refresh_resp.status_code}")
            
            if refresh_resp.status_code == 200:
                refresh_result = refresh_resp.json()
                new_access_token = refresh_result.get("access_token")
                print(f"   ✅ Token refresh successful!")
                print(f"   New Access Token: {new_access_token[:20]}...")
                print(f"   Expires In: {refresh_result.get('expires_in')} seconds")
            else:
                print(f"   ❌ Token refresh failed: {refresh_resp.text}")
                
        except Exception as e:
            print(f"   ❌ Token refresh error: {str(e)}")
            
    else:
        print(f"   ❌ Login failed: {login_resp.text}")
        
except Exception as e:
    print(f"   ❌ Login error: {str(e)}")

# Test 5: Invalid login
print("\n5️⃣ Testing Invalid Login...")
invalid_login_data = {
    "phone_number": signup_data["phone_number"],
    "password": "WrongPassword"
}

try:
    invalid_resp = requests.post(f"{BASE_URL}/login", json=invalid_login_data)
    print(f"   Status Code: {invalid_resp.status_code}")
    
    if invalid_resp.status_code == 401:
        print(f"   ✅ Invalid login correctly rejected!")
        print(f"   Error: {invalid_resp.json().get('detail')}")
    else:
        print(f"   ❌ Invalid login should return 401, got: {invalid_resp.status_code}")
        
except Exception as e:
    print(f"   ❌ Invalid login test error: {str(e)}")

print("\n" + "=" * 50)
print("🏁 Authentication Testing Complete!")
print("\n💡 Next Steps:")
print("   - Test reminder creation with patient authentication")
print("   - Test patient-specific reminder retrieval")
print("   - Implement role-based access control for admin endpoints")
