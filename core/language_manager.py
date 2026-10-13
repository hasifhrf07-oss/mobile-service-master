"""Language Manager — Multi-language support"""
import os
import json

ROOT = os.path.dirname(os.path.dirname(__file__))
I18N_DIR = os.path.join(ROOT, "data", "i18n")

DEFAULT_LANG = "en"
CACHE = {}


def _load_lang(lang_code):
    """Load language file"""
    if lang_code in CACHE:
        return CACHE[lang_code]

    path = os.path.join(I18N_DIR, f"{lang_code}.json")
    if not os.path.exists(path):
        path = os.path.join(I18N_DIR, f"{DEFAULT_LANG}.json")

    try:
        data = json.load(open(path, "r", encoding="utf-8"))
        CACHE[lang_code] = data
        return data
    except Exception:
        return {}


def get_available_languages():
    """Get all available languages"""
    langs = []
    if os.path.isdir(I18N_DIR):
        for f in os.listdir(I18N_DIR):
            if f.endswith(".json"):
                code = f[:-5]
                data = _load_lang(code)
                langs.append({
                    "code": code,
                    "name": data.get("lang_name", code),
                })
    return sorted(langs, key=lambda x: x["code"])


def translate(key, lang=DEFAULT_LANG):
    """Translate a key (dot notation: nav.connect)"""
    data = _load_lang(lang)

    parts = key.split(".")
    current = data
    for p in parts:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            return key  # Return key if not found

    return current if isinstance(current, str) else key


def get_all_translations(lang=DEFAULT_LANG):
    """Get all translations for a language"""
    return _load_lang(lang)


if __name__ == "__main__":
    print("Available:", get_available_languages())
    print("EN nav.connect:", translate("nav.connect", "en"))
    print("BN nav.connect:", translate("nav.connect", "bn"))
