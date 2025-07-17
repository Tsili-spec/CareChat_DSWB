from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Load NLLB-200 model and tokenizer once
_NLLB_MODEL_NAME = "facebook/nllb-200-distilled-600M"
_tokenizer = None
_model = None

def _load_nllb():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(_NLLB_MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(_NLLB_MODEL_NAME)

def translate_to_english(text: str, language: str) -> str:
    """
    Translate any text to English using NLLB-200, regardless of source language.
    """
    _load_nllb()
    # Map common language names to NLLB codes
    lang_map = {
        "en": "eng_Latn",
        "english": "eng_Latn",
        "eng": "eng_Latn",
        "fr": "fra_Latn",
        "french": "fra_Latn",
        "bassa": "bas_Latn",
        "basaa": "bas_Latn",
        "basa": "bas_Latn",
        # Add more mappings as needed
    }
    src_code = lang_map.get(language.lower(), None)
    if src_code is None:
        src_code = language if language in _tokenizer.lang_code_to_id else "eng_Latn"
    try:
        inputs = _tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        translated_tokens = _model.generate(
            **inputs,
            forced_bos_token_id=_tokenizer.lang_code_to_id["eng_Latn"],
            # Set source language
            decoder_start_token_id=_tokenizer.lang_code_to_id.get(src_code, _tokenizer.lang_code_to_id["eng_Latn"])
        )
        return _tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
    except Exception:
        return text
