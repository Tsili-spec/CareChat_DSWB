#!/usr/bin/env python3

import requests
import time

def test_feedback_api():
    """Test the feedback API"""
    try:
        # Test data
        data = {
            'patient_id': '6893883a6a73f9c7bc427559',
            'rating': 3,
            'feedback_text': 'test feedback',
            'language': 'en'
        }
        
        print("Testing feedback API...")
        print(f"Data: {data}")
        
        # Test with a timeout
        response = requests.post(
            'http://localhost:8000/api/feedback/',
            data=data,
            headers={'accept': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_feedback_api()
