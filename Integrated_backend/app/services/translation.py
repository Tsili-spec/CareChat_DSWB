from deep_translator import GoogleTranslator
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text from source language to target language using Google Translate
    
    Args:
        text: Text to translate
        source_lang: Source language code (e.g., 'fr', 'en')
        target_lang: Target language code (e.g., 'en', 'fr')
        
    Returns:
        Translated text
    """
    try:
        if source_lang == target_lang:
            return text
            
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        
        logger.info(f"Successfully translated text from {source_lang} to {target_lang}")
        return translated
        
    except Exception as e:
        logger.error(f"Translation failed from {source_lang} to {target_lang}: {e}")
        # Return original text if translation fails
        return text
