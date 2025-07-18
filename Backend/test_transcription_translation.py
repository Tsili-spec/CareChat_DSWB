import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/services')))
from app.services.transcription_translation import transcribe_and_translate

# Load a sample audio file

def load_audio_bytes(file_path):
    with open(file_path, "rb") as f:
        return f.read()

if __name__ == "__main__":
    # Example test MP3 or WAV file (must exist)
    audio_path = "/home/asongna/Downloads/aud1.mp3"  # Use your real file path
    audio_bytes = load_audio_bytes(audio_path)

    # Call your transcription + translation pipeline
    result = transcribe_and_translate(audio_bytes, target_languages=["fr", "en", "sw"])

    # Print the results
    print("Detected Language:", result["detected_language"])
    print("Confidence:", result["confidence"])
    print("Original Text:", result["original_text"])
    print("Translations:")
    for lang, translation in result["translations"].items():
        print(f"{lang}: {translation}")
