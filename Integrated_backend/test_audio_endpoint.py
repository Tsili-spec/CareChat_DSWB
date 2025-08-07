#!/usr/bin/env python3
"""
Test script for the audio chat endpoint
"""
import requests
import json
from pathlib import Path

def test_audio_endpoint():
    """Test the audio chat endpoint with a sample audio file"""
    
    # API endpoint
    url = "http://localhost:8000/chat/audio"
    
    # Test data
    data = {
        "user_id": "test_patient_123",
        "conversation_id": None,  # New conversation
        "provider": "groq"
    }
    
    # Note: In a real scenario, you would upload an actual audio file
    # For this test, we'll show the expected request format
    
    print("🎤 Audio Chat Endpoint Test")
    print("=" * 50)
    print(f"Endpoint: {url}")
    print(f"Method: POST")
    print(f"Content-Type: multipart/form-data")
    print()
    print("Expected form data:")
    print(f"  - audio: [audio file] (WAV, MP3, M4A, FLAC, OGG)")
    print(f"  - user_id: {data['user_id']}")
    print(f"  - conversation_id: {data['conversation_id']}")
    print(f"  - provider: {data['provider']}")
    print()
    print("Response format:")
    print("""{
    "conversation_id": "string",
    "transcribed_text": "string",
    "detected_language": "string", 
    "transcription_confidence": float,
    "user_message": {
        "message_id": "string",
        "role": "user",
        "content": "string",
        "timestamp": "datetime",
        "model_used": "string"
    },
    "assistant_message": {
        "message_id": "string", 
        "role": "assistant",
        "content": "string",
        "timestamp": "datetime",
        "model_used": "string"
    },
    "provider": "string"
}""")
    print()
    print("🔧 Usage Example with curl:")
    print(f"""curl -X POST "{url}" \\
  -F "audio=@/path/to/audio/file.wav" \\
  -F "user_id={data['user_id']}" \\
  -F "provider={data['provider']}" """)
    print()
    print("📝 Usage Example with Python requests:")
    print("""
import requests

# Upload audio file
with open('audio_file.wav', 'rb') as audio_file:
    files = {'audio': audio_file}
    data = {
        'user_id': 'patient_123',
        'provider': 'groq'
    }
    response = requests.post('http://localhost:8000/chat/audio', files=files, data=data)
    result = response.json()
    print(f"Transcribed: {result['transcribed_text']}")
    print(f"AI Response: {result['assistant_message']['content']}")
""")

if __name__ == "__main__":
    test_audio_endpoint()
