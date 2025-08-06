from app.services.transcription import transcribe_audio
from app.services.translation import translate_text
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def transcribe_and_translate(audio_data: bytes) -> dict:
    """
    Transcribe audio and translate French to English, leave English as is.
    
    Args:
        audio_data: Audio file data as bytes
        
    Returns:
        Dictionary containing original text, detected language, confidence, and translations
    """
    try:
        # Transcribe audio
        transcription = transcribe_audio(audio_data)
        original_text = transcription["text"]
        detected_language = transcription["language"]
        confidence = transcription["confidence"]
        
        # Handle translations
        translations = {}
        if detected_language == "fr":
            translations["en"] = translate_text(original_text, "fr", "en")
        elif detected_language == "en":
            translations["en"] = original_text
        else:
            # For other languages, attempt to translate to English
            translations["en"] = translate_text(original_text, detected_language, "en")
            translations[detected_language] = original_text
        
        logger.info(f"Successfully processed audio: {detected_language} -> translations")
        
        return {
            "original_text": original_text,
            "detected_language": detected_language,
            "confidence": confidence,
            "translations": translations
        }
        
    except Exception as e:
        logger.error(f"Audio transcription and translation failed: {e}")
        return {
            "original_text": "",
            "detected_language": "unknown",
            "confidence": 0.0,
            "translations": {}
        }
