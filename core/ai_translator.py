"""
AI Dynamic Translator
Uses AI Engine to translate missing strings on the fly and caches them.
"""
import os
import json
from core.ai_engine import ask_ai

I18N_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "i18n")
os.makedirs(I18N_DIR, exist_ok=True)

def get_translation(lang_code, text_key):
    """Get translation from cache or translate using AI"""
    file_path = os.path.join(I18N_DIR, f"{lang_code}.json")
    
    # Load existing cache
    cache = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}
            
    # Return if exists
    if text_key in cache:
        return cache[text_key]
        
    # If not exists, ask AI to translate
    prompt = f"Translate the following English UI text into language code '{lang_code}'. Return ONLY the translated text, no extra explanation:\n\n'{text_key}'"
    response = ask_ai(prompt)
    
    if response.get("ok"):
        translated = response.get("answer", "").strip()
        # Save to cache
        cache[text_key] = translated
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return translated
        
    return text_key # Fallback to English if AI fails
