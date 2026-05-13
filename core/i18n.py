# core/i18n.py

import json
import os

from core.file_handler import resource_path

I18N_DIR = os.path.join("assets", "i18n")

LANGUAGE_LABELS = {
    "en": "English",
    "bn": "বাংলা",
    "hi": "हिन्दी",
}

TRANSLATIONS: dict[str, dict[str, str]] = {}
APP_LANGUAGES: dict[str, str] = {}


def _load_translations():
    global TRANSLATIONS, APP_LANGUAGES

    if not os.path.isdir(resource_path(I18N_DIR)):
        return

    for filename in os.listdir(resource_path(I18N_DIR)):
        if not filename.endswith(".json"):
            continue
        lang_code = filename.removesuffix(".json")
        filepath = os.path.join(I18N_DIR, filename)
        try:
            with open(resource_path(filepath), "r", encoding="utf-8") as f:
                TRANSLATIONS[lang_code] = json.load(f)
        except (json.JSONDecodeError, IOError, ValueError):
            continue

        label = LANGUAGE_LABELS.get(lang_code, lang_code)
        APP_LANGUAGES[lang_code] = label


_load_translations()


def translate(key: str, language: str, **kwargs) -> str:
    default = TRANSLATIONS.get("en", {})
    text = TRANSLATIONS.get(language, default).get(key, default.get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text