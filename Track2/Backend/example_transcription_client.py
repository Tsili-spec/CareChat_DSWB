"""
Example client for the CareChat Transcription API.
This script demonstrates how to interact with the transcription endpoints.
"""

import requests
import json
import os

class TranscriptionClient:
    """Client for interacting with the CareChat Transcription API."""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_supported_formats(self) -> dict:
        """Get information about supported audio formats."""
        try:
            response = self.session.get(f"{self.base_url}/transcribe/supported-formats/")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error getting supported formats: {e}")
            return {}
    
    def transcribe_simple(self, audio_file_path: str) -> dict:
        """Simple transcription of an audio file."""
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            with open(audio_file_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                response = self.session.post(f"{self.base_url}/transcribe/simple/", files=files)
                response.raise_for_status()
                return response.json()
        except requests.RequestException as e:
            print(f"❌ Error in simple transcription: {e}")
            return {}
    
    def transcribe_full(self, audio_file_path: str) -> dict:
        """Full transcription with detailed response."""
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            with open(audio_file_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                response = self.session.post(f"{self.base_url}/transcribe/", files=files)
                response.raise_for_status()
                return response.json()
        except requests.RequestException as e:
            print(f"❌ Error in full transcription: {e}")
            return {}

def print_json(data: dict, title: str = ""):
    """Pretty print JSON data."""
    if title:
        print(f"\n{title}")
        print("=" * len(title))
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    """Main example function."""
    print("🎵 CareChat Transcription API Client Example")
    print("=" * 50)
    
    # Initialize client
    client = TranscriptionClient()
    
    # Test 1: Get supported formats
    print("\n1. Getting supported formats...")
    formats = client.get_supported_formats()
    if formats:
        print_json(formats, "Supported Formats")
    
    # Look for test audio files
    test_files = [
        "upload/test_audio.mp3",
        "upload/test_audio.wav",
        "Data/clinical_summaries_test.csv",  # This won't work but shows error handling
    ]
    
    audio_file = None
    for test_file in test_files:
        if os.path.exists(test_file) and test_file.endswith(('.mp3', '.wav', '.m4a', '.flac')):
            audio_file = test_file
            break
    
    if not audio_file:
        print("\n⚠️ No test audio files found.")
        print("To test with actual audio, place an audio file in the upload/ directory.")
        print("Example: upload/test_audio.mp3")
        print("\nYou can record a short audio clip or download a sample audio file.")
        return
    
    print(f"\n📁 Using test audio file: {audio_file}")
    
    # Test 2: Simple transcription
    print("\n2. Testing simple transcription...")
    try:
        result = client.transcribe_simple(audio_file)
        if result:
            print_json(result, "Simple Transcription Result")
    except FileNotFoundError as e:
        print(f"❌ {e}")
    
    # Test 3: Full transcription
    print("\n3. Testing full transcription...")
    try:
        result = client.transcribe_full(audio_file)
        if result:
            print_json(result, "Full Transcription Result")
    except FileNotFoundError as e:
        print(f"❌ {e}")
    
    print("\n🎵 Example completed!")

if __name__ == "__main__":
    main()
