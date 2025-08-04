"""
Enhanced CareChat Transcription + Chat API Client Example.
This script demonstrates how to use the transcription endpoint with chat functionality.
"""

import requests
import json
import os
from uuid import uuid4

class EnhancedTranscriptionClient:
    """Client for interacting with the CareChat Enhanced Transcription + Chat API."""
    
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
        """Simple transcription of an audio file (no chat functionality)."""
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
    
    def transcribe_with_chat(
        self, 
        audio_file_path: str, 
        user_id: str, 
        conversation_id: str = None,
        provider: str = "groq"
    ) -> dict:
        """Enhanced transcription with chat functionality."""
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            with open(audio_file_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {
                    'user_id': user_id,
                    'provider': provider
                }
                
                if conversation_id:
                    data['conversation_id'] = conversation_id
                
                response = self.session.post(f"{self.base_url}/transcribe/", files=files, data=data)
                response.raise_for_status()
                return response.json()
        except requests.RequestException as e:
            print(f"❌ Error in enhanced transcription: {e}")
            return {}

def print_json(data: dict, title: str = ""):
    """Pretty print JSON data."""
    if title:
        print(f"\n{title}")
        print("=" * len(title))
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    """Main example function."""
    print("🎵 CareChat Enhanced Transcription + Chat API Client Example")
    print("=" * 65)
    
    # Initialize client
    client = EnhancedTranscriptionClient()
    
    # Test 1: Get supported formats
    print("\n1. Getting supported formats...")
    formats = client.get_supported_formats()
    if formats:
        print_json(formats, "Supported Formats")
    
    # Look for test audio files
    test_files = [
        "upload/test_audio.mp3",
        "upload/test_audio.wav",
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
        print("\nYou can record a short audio clip with a question like:")
        print("'What are the symptoms of diabetes?' or 'How can I manage high blood pressure?'")
        return
    
    print(f"\n📁 Using test audio file: {audio_file}")
    
    # Generate a test user ID (in real usage, this would come from your user system)
    test_user_id = str(uuid4())
    print(f"📝 Using test user ID: {test_user_id}")
    
    # Test 2: Simple transcription (unchanged functionality)
    print("\n2. Testing simple transcription...")
    try:
        result = client.transcribe_simple(audio_file)
        if result:
            print_json(result, "Simple Transcription Result")
    except FileNotFoundError as e:
        print(f"❌ {e}")
    
    # Test 3: Enhanced transcription with chat
    print("\n3. Testing enhanced transcription + chat...")
    try:
        result = client.transcribe_with_chat(
            audio_file, 
            user_id=test_user_id,
            provider="groq"
        )
        if result:
            print_json(result, "Enhanced Transcription + Chat Result")
            
            # Extract and display key information
            if "transcription" in result and "chat_response" in result:
                print(f"\n🎤 Transcribed Text: {result['transcription']['text']}")
                print(f"🌍 Detected Language: {result['transcription']['detected_language']}")
                print(f"📊 Confidence: {result['transcription']['confidence']:.2f}")
                print(f"🤖 AI Response: {result['chat_response']['assistant_message']['content']}")
                print(f"💬 Conversation ID: {result['chat_response']['conversation_id']}")
                
                # Test continuing the conversation
                conversation_id = result['chat_response']['conversation_id']
                print(f"\n4. Testing conversation continuation...")
                print(f"   Using conversation ID: {conversation_id}")
                
    except FileNotFoundError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎵 Enhanced transcription example completed!")
    print("\n💡 Key Features:")
    print("   ✅ Speech-to-text transcription")
    print("   ✅ Automatic language detection")
    print("   ✅ AI-powered chat responses")
    print("   ✅ Conversation memory/context")
    print("   ✅ Multiple LLM providers (Groq, Gemini)")
    print("   ✅ Healthcare-focused responses")

if __name__ == "__main__":
    main()
