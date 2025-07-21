from app.services.translation import translate_to_english

def test_translation_french_to_english():
    french_text = "l'infirmière était lente et irrespectueuse"
    translated = translate_to_english(french_text, "french")
    print("Original:", french_text)
    print("Translated:", translated)
    assert translated != french_text
    assert "nurse" in translated or "slow" in translated or "disrespectful" in translated.lower()
