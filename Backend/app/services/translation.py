from textblob import TextBlob

def translate_to_english(text: str, language: str) -> str:
    # If already English, return as is
    if language.lower() in ["en", "english", "eng"]:
        return text
    try:
        blob = TextBlob(text)
        translated = blob.translate(to="en")
        return str(translated)
    except Exception:
        # If translation fails, fallback to original text
        return text
