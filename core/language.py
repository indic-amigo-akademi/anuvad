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


def get_indic_script_name(lang: str) -> str:
    if lang in ["hi", "mr"]:
        return sanscript.DEVANAGARI
    if lang in ["bn", "as"]:
        return sanscript.BENGALI
    if lang in ["or"]:
        return sanscript.ORIYA
    if lang in ["ta"]:
        return sanscript.TAMIL
    if lang in ["kn"]:
        return sanscript.KANNADA
    if lang in ["ml"]:
        return sanscript.MALAYALAM
    if lang in ["gu"]:
        return sanscript.GUJARATI
    if lang in ["pa"]:
        return sanscript.GURMUKHI
    if lang in ["te"]:
        return sanscript.TELUGU

    return getattr(sanscript, lang.upper())


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


def convert_to_latin(text: str) -> str:
    lang = detect_language(text)
    if is_indic(lang):
        text = text.replace("।", ".")
        text = transliterate(
            text,
            get_indic_script_name(lang),
            sanscript.ISO_VEDIC,
        )
    return text
