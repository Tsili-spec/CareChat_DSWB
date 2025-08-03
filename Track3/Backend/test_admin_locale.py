#!/usr/bin/env python3
"""
Test script to check if admin interface is working with English locale
"""

import requests
import os

# Set environment variables for English locale
os.environ['FASTAPI_AMIS_ADMIN_LANGUAGE'] = 'en_US'
os.environ['FASTAPI_AMIS_ADMIN_LOCALE'] = 'en_US'
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'

def test_admin_interface():
    """Test the admin interface with English headers"""
    
    # For local development
    base_url = "http://localhost:8001"

    # For Render deployment
    # base_url = "https://bloodbank.onrender.com"
    
    # Test basic health
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test admin interface with English headers
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(f"{base_url}/admin/", headers=headers)
        print(f"✅ Admin interface: {response.status_code}")
        
        # Check if response contains English text
        content = response.text.lower()
        chinese_indicators = ['首页', '筛选', '导出', '每页显示']
        english_indicators = ['home', 'filter', 'export', 'items per page', 'user management']
        
        chinese_found = any(indicator in content for indicator in chinese_indicators)
        english_found = any(indicator in content for indicator in english_indicators)
        
        print(f"   Chinese indicators found: {chinese_found}")
        print(f"   English indicators found: {english_found}")
        
        if chinese_found:
            print("⚠️  Still showing Chinese text - try clearing browser cache")
        else:
            print("✅ No Chinese text detected")
            
    except Exception as e:
        print(f"❌ Admin interface test failed: {e}")

    print("\n" + "="*60)
    print("📋 INSTRUCTIONS TO FIX CHINESE TEXT:")
    print("="*60)
    print("1. Clear your browser cache completely:")
    print("   - Chrome: Ctrl+Shift+Delete → Select 'All time' → Check all boxes → Clear")
    print("   - Firefox: Ctrl+Shift+Delete → Select 'Everything' → Check all boxes → Clear")
    print("   - Or use Incognito/Private mode")
    print()
    print("2. Force refresh the admin page:")
    print("   - Press Ctrl+F5 (or Cmd+Shift+R on Mac)")
    print()
    print("3. Access the admin interface at:")
    print(f"   {base_url}/admin/")
    print()
    print("4. If Chinese text still appears, restart the server:")
    print("   - Press Ctrl+C in the terminal running uvicorn")
    print("   - Run: LANG=en_US.UTF-8 python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
    print("="*60)

if __name__ == "__main__":
    test_admin_interface()
