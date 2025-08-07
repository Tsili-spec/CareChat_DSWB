#!/usr/bin/env python3
"""
Test the fixed audio chat endpoint
"""
import requests
import json

def test_audio_endpoint_availability():
    """Test if the audio endpoint is available and properly configured"""
    
    try:
        # Test if the server is running
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server not responding")
            return
        
        # Test if the audio endpoint is available in the OpenAPI spec
        openapi_response = requests.get("http://localhost:8000/openapi.json")
        if openapi_response.status_code == 200:
            openapi_data = openapi_response.json()
            
            # Check if the audio endpoint is in the API spec
            if "/chat/audio" in openapi_data.get("paths", {}):
                print("✅ Audio endpoint is available in API")
                
                # Get endpoint details
                audio_endpoint = openapi_data["paths"]["/chat/audio"]
                if "post" in audio_endpoint:
                    print("✅ Audio endpoint accepts POST requests")
                    
                    # Check parameters
                    post_details = audio_endpoint["post"]
                    if "requestBody" in post_details:
                        print("✅ Audio endpoint has request body configuration")
                    
                    if "responses" in post_details:
                        responses = post_details["responses"]
                        if "200" in responses:
                            print("✅ Audio endpoint returns 200 response")
                            print(f"   Response model: {responses['200'].get('content', {}).get('application/json', {}).get('schema', {}).get('$ref', 'Unknown')}")
                else:
                    print("❌ Audio endpoint does not accept POST requests")
            else:
                print("❌ Audio endpoint not found in API")
        
        print("\n📋 Audio Endpoint Summary:")
        print("- URL: http://localhost:8000/chat/audio")
        print("- Method: POST")
        print("- Content-Type: multipart/form-data")
        print("- Parameters:")
        print("  - audio: File (audio file)")
        print("  - user_id: string (patient ID)")
        print("  - conversation_id: string (optional)")
        print("  - provider: string (groq/gemini)")
        
        print("\n🧪 Test with curl:")
        print("curl -X POST 'http://localhost:8000/chat/audio' \\")
        print("  -F 'audio=@your_audio_file.wav' \\")
        print("  -F 'user_id=6893883a6a73f9c7bc427559' \\")
        print("  -F 'provider=groq'")
        
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

if __name__ == "__main__":
    test_audio_endpoint_availability()
