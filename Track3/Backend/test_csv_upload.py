#!/usr/bin/env python3
"""
Test script to demonstrate CSV upload functionality
"""

import requests
import json

def test_csv_upload():
    """Test the CSV upload endpoints"""
    
    base_url = "http://localhost:8000"
    
    # Step 1: Login to get authentication token
    login_data = {
        "username": "frank",
        "password": "Frank123"
    }
    
    print("🔐 Logging in...")
    response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return False
    
    token_data = response.json()
    token = token_data.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful!")
    
    # Step 2: Upload blood collection CSV
    print("\n📤 Uploading blood collection CSV...")
    
    try:
        with open("data/blood_bank_records.csv", "rb") as f:
            files = {"file": ("blood_bank_records.csv", f, "text/csv")}
            response = requests.post(
                f"{base_url}/api/v1/blood-bank/collections/upload-csv",
                files=files,
                headers=headers
            )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Collections upload successful!")
            print(f"   📊 Total records: {result['total_records']}")
            print(f"   ✅ Successful: {result['successful_uploads']}")
            print(f"   ❌ Failed: {result['failed_uploads']}")
            if result['failures']:
                print(f"   🚨 Sample failures: {result['failures'][:3]}")
        else:
            print(f"❌ Collections upload failed: {response.status_code} - {response.text}")
            
    except FileNotFoundError:
        print("❌ blood_bank_records.csv not found in data/ directory")
        return False
    
    # Step 3: Upload blood usage CSV
    print("\n📤 Uploading blood usage CSV...")
    
    try:
        with open("data/usage_data.csv", "rb") as f:
            files = {"file": ("usage_data.csv", f, "text/csv")}
            response = requests.post(
                f"{base_url}/api/v1/blood-bank/usage/upload-csv",
                files=files,
                headers=headers
            )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Usage upload successful!")
            print(f"   📊 Total records: {result['total_records']}")
            print(f"   ✅ Successful: {result['successful_uploads']}")
            print(f"   ❌ Failed: {result['failed_uploads']}")
            if result['failures']:
                print(f"   🚨 Sample failures: {result['failures'][:3]}")
        else:
            print(f"❌ Usage upload failed: {response.status_code} - {response.text}")
            
    except FileNotFoundError:
        print("❌ usage_data.csv not found in data/ directory")
        return False
    
    print("\n🎉 CSV upload test completed!")
    return True

if __name__ == "__main__":
    test_csv_upload()
