# core/language.py
import unicodedata
import logging
import asyncio
from googletrans import Translator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from deep_translator import single_detection

logger = logging.getLogger(__name__)

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


def _detect_with_googletrans(text: str) -> str | None:
    try:
        translator = Translator(service_urls=["translate.googleapis.com"])
        res = asyncio.run(translator.detect(text))
        print(f"Googletrans detection result: {res.lang} with confidence {res.confidence} for '{text}'")
        return res.lang
    except Exception as e:
        logger.error(f"Error in detecting lang using googletrans: {e}")
        return None


def _detect_with_api(text: str, api_key: str | None) -> str | None:
    if not api_key:
        return None

    try:
        return single_detection(text[:1000], api_key=api_key) or None
    except Exception as e:
        logger.error(f"Error in detecting lang: {e}")
        return None


def _detect_from_script(text: str) -> str:
    script_map = {
        "LATIN": "en",
        "DEVANAGARI": "hi",
        "BENGALI": "bn",
        "GURMUKHI": "pa",
        "GUJARATI": "gu",
        "ORIYA": "or",
        "TAMIL": "ta",
        "TELUGU": "te",
        "KANNADA": "kn",
        "MALAYALAM": "ml",
    }

    counts: dict[str, int] = {}
    for char in text[:1000]:
        if not char.isalpha():
            continue
        try:
            script = unicodedata.name(char).split(" ")[0]
        except (ValueError, IndexError):
            continue
        counts[script] = counts.get(script, 0) + 1

    if not counts:
        return "unknown"

    predominant_script = max(counts, key=lambda script: counts[script])
    return script_map.get(predominant_script, "unknown")


def detect_language(text: str, lang_detect_api_key: str | None = None) -> str:
    """Detect language using translation service, optional API, then Unicode script."""
    if not text:
        return "unknown"

    return (
        # _detect_with_googletrans(text)
        # or 
        _detect_with_api(text, lang_detect_api_key)
        or _detect_from_script(text)
    )


def is_latin(text: str) -> bool:
    return all(ord(c) < 128 for c in text)


def is_indic(lang: str) -> bool:
    return lang in SUPPORTED_INDIC_LANG


def convert_to_latin(
    text: str, lang: str | None = None, lang_detect_api_key: str | None = None
) -> str:
    """
    Convert to latin variant if it's an Indic language. This is useful for better translation quality with models like mBART.
    """
    lang = lang or detect_language(text, lang_detect_api_key=lang_detect_api_key)
    if is_indic(lang):
        text = text.replace("।", ".")
        text = transliterate(
            text,
            get_indic_script_name(lang),
            sanscript.ISO_VEDIC,
        )
    return text
