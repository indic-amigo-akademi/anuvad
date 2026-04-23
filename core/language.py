# core/language.py

from langdetect import detect, LangDetectException


SUPPORTED_LANGUAGES = {
    "en": "English",
    "bn": "Bengali",
    "hi": "Hindi",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
}


def detect_language(text: str) -> str:
    """
    Detects language code from text
    """
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"
