#!/usr/bin/env python3
"""
Debug MongoDB Connection Issues
"""

import asyncio
import motor.motor_asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_urls():
    """Test different MongoDB URL configurations"""
    
    # URLs to test
    test_urls = [
        "mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017",
        "mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017/carechat",
        "mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017/admin"
    ]
    
    print("🔍 Testing MongoDB Connection URLs")
    print("=" * 60)
    
    # Check environment variable
    env_url = os.getenv("DATABASE_URL")
    print(f"📋 DATABASE_URL from .env: {env_url}")
    print("=" * 60)
    
    async def test_single_url(url, description):
        """Test a single MongoDB URL"""
        print(f"\n🔗 Testing: {description}")
        print(f"   URL: {url}")
        
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(
                url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # Test basic connection
            await client.admin.command('ping')
            print("   ✅ Connection successful!")
            
            # Test database access
            db = client.carechat
            collections = await db.list_collection_names()
            print(f"   📂 Collections accessible: {len(collections)}")
            print(f"   📋 Collection names: {collections[:5]}{'...' if len(collections) > 5 else ''}")
            
            # Test a simple operation
            test_collection = db.connection_test
            result = await test_collection.insert_one({"test": True, "url": description})
            print(f"   💾 Test insert successful: {result.inserted_id}")
            
            # Clean up
            await test_collection.delete_one({"_id": result.inserted_id})
            print("   🧹 Test document cleaned up")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            return False
    
    async def run_tests():
        """Run all connection tests"""
        results = []
        
        for i, url in enumerate(test_urls, 1):
            description = f"Test {i}"
            if "carechat" in url:
                description += " (with database in URL)"
            elif "admin" in url:
                description += " (with admin database)"
            else:
                description += " (no database specified)"
                
            success = await test_single_url(url, description)
            results.append((url, success))
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY:")
        print("=" * 60)
        
        for url, success in results:
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{status}: {url}")
        
        successful_urls = [url for url, success in results if success]
        if successful_urls:
            print(f"\n🎉 {len(successful_urls)} URL(s) working successfully!")
            print("✅ Recommended URL:", successful_urls[0])
            return successful_urls[0]
        else:
            print("\n❌ No URLs working!")
            return None
    
    return asyncio.run(run_tests())

if __name__ == "__main__":
    working_url = test_urls()
    
    if working_url:
        print(f"\n🔧 RECOMMENDATION:")
        print(f"Use this URL in your .env file:")
        print(f"DATABASE_URL={working_url}")
        sys.exit(0)
    else:
        print("\n❌ All connection tests failed!")
        sys.exit(1)
