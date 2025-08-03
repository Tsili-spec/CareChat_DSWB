#!/usr/bin/env python3
"""
Simple test to verify the users endpoint works
"""

import requests
import json

# Login
login_response = requests.post("http://localhost:8001/api/v1/auth/login", json={
    "username": "testadmin",
    "password": "TestPass123!"
})

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    
    # Get users
    users_response = requests.get(
        "http://localhost:8001/api/v1/auth/users?skip=0&limit=3",
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f"Status: {users_response.status_code}")
    if users_response.status_code == 200:
        users = users_response.json()
        print(f"✅ SUCCESS! Found {len(users)} users:")
        for user in users:
            print(f"  - {user['username']} ({user['role']}) - ID: {user['user_id']}")
    else:
        print(f"❌ FAILED: {users_response.text}")
else:
    print(f"Login failed: {login_response.status_code}")
