import requests
import os

# Test with the actual audio file
audio_file_path = "/home/asongna/Music/recordings/aud8.flac"

if os.path.exists(audio_file_path):
    files = {
        'audio': ('aud8.flac', open(audio_file_path, 'rb'), 'audio/flac')
    }
    data = {
        'patient_id': '6893883a6a73f9c7bc427559',
        'rating': 1,
        'language': 'en'
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/feedback/audio/',
            files=files,
            data=data,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")
    finally:
        files['audio'][1].close()
else:
    print(f"Audio file not found: {audio_file_path}")
