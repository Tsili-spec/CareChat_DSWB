#!/usr/bin/env python3
"""
Test script for the CSV download endpoint
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.api.dashboard import download_feedback_csv

async def test_csv_endpoint():
    """Test the CSV download endpoint"""
    try:
        print("Testing CSV download endpoint...")
        
        # Test basic functionality without filters
        response = await download_feedback_csv(None, None, None, None)
        print(f"Response type: {type(response)}")
        print(f"Media type: {response.media_type}")
        
        # Check headers
        if hasattr(response, 'headers'):
            print("Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
        
        print("✅ CSV endpoint test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing CSV endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_csv_endpoint())
    sys.exit(0 if success else 1)
