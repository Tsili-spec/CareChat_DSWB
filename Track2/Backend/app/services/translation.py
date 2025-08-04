from deep_translator import GoogleTranslator

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
        return text  # Return original text if translation fails
