#!/usr/bin/env python3
"""
Final comprehensive test of the CareChat backend
"""

import requests
import json
import sys

def test_api_endpoints():
    """Test various API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🔗 Testing CareChat Backend API...")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health check: {health_data['status']}")
            print(f"   📊 Version: {health_data['version']}")
            print(f"   📅 Timestamp: {health_data['timestamp']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test API docs
    print("\n2. Testing API documentation...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("   ✅ API documentation accessible")
        else:
            print(f"   ❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API docs error: {e}")
    
    # Test OpenAPI schema
    print("\n3. Testing OpenAPI schema...")
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            schema = response.json()
            print(f"   ✅ OpenAPI schema loaded")
            print(f"   📋 API title: {schema.get('info', {}).get('title', 'Unknown')}")
            print(f"   🔢 API version: {schema.get('info', {}).get('version', 'Unknown')}")
            
            # Count endpoints
            paths = schema.get('paths', {})
            endpoint_count = len(paths)
            print(f"   🚀 Available endpoints: {endpoint_count}")
            
            # List some key endpoints
            key_endpoints = ['/api/patient/register', '/api/feedback/submit', '/api/reminder/create']
            available_endpoints = []
            for endpoint in key_endpoints:
                if endpoint in paths:
                    available_endpoints.append(endpoint)
            
            if available_endpoints:
                print(f"   📍 Key endpoints: {', '.join(available_endpoints)}")
        else:
            print(f"   ❌ OpenAPI schema failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ OpenAPI schema error: {e}")
    
    print("\n=" * 50)
    print("🎉 API testing completed!")
    return True

if __name__ == "__main__":
    success = test_api_endpoints()
    if success:
        print("✅ CareChat backend is running successfully!")
        print("🌐 Access the API at: http://localhost:8000")
        print("📚 View documentation at: http://localhost:8000/docs")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
