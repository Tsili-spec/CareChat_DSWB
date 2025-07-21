# --- Service API ---
from app.services.transcription import transcribe_audio
from app.services.translation import translate_text

def transcribe_and_translate(audio_data: bytes) -> dict:
    """Transcribe audio and translate French to English, leave English as is."""
    transcription = transcribe_audio(audio_data)
    original_text = transcription["text"]
    detected_language = transcription["language"]
    confidence = transcription["confidence"]
    translations = {}
    if detected_language == "fr":
        translations["en"] = translate_text(original_text, "fr", "en")
    elif detected_language == "en":
        translations["en"] = original_text
    else:
        translations[detected_language] = original_text
    return {
        "original_text": original_text,
        "detected_language": detected_language,
        "confidence": confidence,
        "translations": translations
    }
