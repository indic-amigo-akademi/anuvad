# core/language.py

from langdetect import detect, LangDetectException
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

SUPPORTED_INDIC_LANG = {
    "bn": "Bengali",
    "hi": "Hindi",
    "mr": "Marathi",
    "as": "Assamese",
    "or": "Odia",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "te": "Telugu",
}

SUPPORTED_LATIN_LANG = {
    "en": "English",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
}

SUPPORTED_LANGUAGES = SUPPORTED_INDIC_LANG | SUPPORTED_LATIN_LANG

INDIC_SCRIPT_NAMES = {
    "hi": sanscript.DEVANAGARI,
    "mr": sanscript.DEVANAGARI,
    "bn": sanscript.BENGALI,
    "as": sanscript.BENGALI,
    "or": sanscript.ORIYA,
    "ta": sanscript.TAMIL,
    "kn": sanscript.KANNADA,
    "ml": sanscript.MALAYALAM,
    "gu": sanscript.GUJARATI,
    "pa": sanscript.GURMUKHI,
    "te": sanscript.TELUGU,
}


def get_indic_script_name(lang: str) -> str:
    script = INDIC_SCRIPT_NAMES.get(lang, getattr(sanscript, lang.upper(), None))
    if script is None:
        raise ValueError(f"Unsupported Indic language code: {lang}")
    return script


def detect_language(text: str) -> str:
    """
    Detects language code from text
    """
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def is_latin(text: str) -> bool:
    return all(ord(c) < 128 for c in text)


def is_indic(lang: str) -> bool:
    return lang in SUPPORTED_INDIC_LANG


def convert_to_latin(text: str, lang: str | None = None) -> str:
    lang = lang or detect_language(text)
    if is_indic(lang):
        text = text.replace("।", ".")
        text = transliterate(
            text,
            get_indic_script_name(lang),
            sanscript.ISO_VEDIC,
        )
    return text
