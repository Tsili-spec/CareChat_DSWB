#!/usr/bin/env python3
"""
Test script to check the users endpoint after UUID fix
"""

import requests
import json

def test_users_endpoint():
    """Test the list users endpoint"""
    
    base_url = "http://localhost:8001/api/v1"
    
    # Test login first
    login_data = {
        "username": "testadmin",
        "password": "TestPass123!"
    }
    
    try:
        print("🔑 Testing login...")
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   Login failed: {login_response.text}")
            return
            
        login_result = login_response.json()
        access_token = login_result.get('access_token')
        print(f"   Login successful! Token: {access_token[:20]}...")
        
        # Test users endpoint
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("\n👥 Testing users endpoint...")
        users_response = requests.get(f"{base_url}/auth/users?skip=0&limit=5", headers=headers)
        print(f"   Users endpoint status: {users_response.status_code}")
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            print(f"   ✅ Success! Found {len(users_data)} users")
            
            for i, user in enumerate(users_data):
                print(f"   User {i+1}:")
                print(f"     ID: {user.get('user_id')}")
                print(f"     Username: {user.get('username')}")
                print(f"     Email: {user.get('email')}")
                print(f"     Role: {user.get('role')}")
                print(f"     Active: {user.get('is_active')}")
                print()
        else:
            print(f"   ❌ Failed: {users_response.status_code}")
            print(f"   Error: {users_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_users_endpoint()
