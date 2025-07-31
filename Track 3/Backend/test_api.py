#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from httpx import AsyncClient
import json

async def test_login():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        login_data = {
            "username": "testadmin",
            "password": "TestPass123!"
        }
        
        try:
            response = await client.post("/api/v1/auth/login", json=login_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Login successful!")
                print(f"Access token: {data.get('access_token', '')[:50]}...")
                print(f"User ID: {data.get('user_id')}")
                print(f"Username: {data.get('username')}")
                print(f"Role: {data.get('role')}")
                return data.get('access_token')
            else:
                print(f"Login failed: {response.text}")
                
        except Exception as e:
            print(f"Error during login: {e}")
            
    return None

if __name__ == "__main__":
    token = asyncio.run(test_login())
