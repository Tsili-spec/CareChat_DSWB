from deep_translator import GoogleTranslator

class TextTranslator:
    def __init__(self):
        self.language_mapping = {'zh-cn': 'zh-CN', 'zh-tw': 'zh-TW', 'zh': 'zh-CN', 'he': 'iw'}
        self.cache = {}

    def translate(self, text: str, src_lang: str, dest_lang: str) -> str:
        if not text or src_lang == dest_lang:
            return text
        src_lang = self.language_mapping.get(src_lang, src_lang)
        dest_lang = self.language_mapping.get(dest_lang, dest_lang)
        cache_key = f"{text}:{src_lang}:{dest_lang}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        try:
            translator = GoogleTranslator(source=src_lang, target=dest_lang)
            translated = translator.translate(text)
            self.cache[cache_key] = translated
            return translated
        except Exception as e:
            print(f"❌ Translation error ({src_lang} → {dest_lang}): {e}")
            return text

text_translator = TextTranslator()

def translate_text(text: str, src_lang: str, dest_lang: str) -> str:
    return text_translator.translate(text, src_lang, dest_lang)# Translation functionality removed
