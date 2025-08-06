"""
Translation service using Google Translate
Based on Track2 implementation
"""
from deep_translator import GoogleTranslator
import logging

logger = logging.getLogger(__name__)

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text from source language to target language using Google Translate.
    
    Args:
        text: Text to translate
        source_lang: Source language code (e.g., 'fr', 'en')
        target_lang: Target language code (e.g., 'fr', 'en')
    
    Returns:
        Translated text
    """
    try:
        if not text.strip():
            return ""
        
        if source_lang == target_lang:
            return text
        
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        return translated if translated else text
    
    except Exception as e:
        print(f"❌ Translation error: {e}")
        logger.error(f"Translation error: {e}")
        return text  # Return original text if translation fails

def detect_language(text: str) -> str:
    """
    Detect the language of the given text
    
    Args:
        text: Text to analyze
    
    Returns:
        Language code (e.g., 'en', 'fr', 'es')
    """
    try:
        text_lower = text.lower()
        
        # Simple language detection based on common words
        french_indicators = ["bonjour", "merci", "oui", "non", "je", "tu", "il", "elle", "nous", "vous", "ils", "est", "dans", "pour", "avec"]
        spanish_indicators = ["hola", "gracias", "sí", "no", "yo", "tú", "él", "ella", "nosotros", "vosotros", "es", "en", "para", "con"]
        english_indicators = ["hello", "thank", "yes", "no", "the", "and", "or", "but", "because", "when", "is", "in", "for", "with"]
        
        french_count = sum(1 for word in french_indicators if word in text_lower)
        spanish_count = sum(1 for word in spanish_indicators if word in text_lower)
        english_count = sum(1 for word in english_indicators if word in text_lower)
        
        if french_count > max(spanish_count, english_count):
            return "fr"
        elif spanish_count > max(french_count, english_count):
            return "es"
        else:
            return "en"
            
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return "en"  # Default to English

def get_supported_languages() -> dict:
    """Get list of supported languages"""
    return {
        "en": "English",
        "fr": "French",
        "es": "Spanish"
    }
