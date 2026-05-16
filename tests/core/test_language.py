# tests/core/test_language.py
"""Unit tests for core.language."""

import pytest

from core.language import detect_language, is_latin, is_indic, convert_to_latin


class TestDetectLanguage:
    def test_english(self):
        lang = detect_language("This is a simple English sentence.")
        assert lang == "en"

    def test_bengali(self):
        lang = detect_language("এটি একটি বাংলা বাক্য।")
        assert lang == "bn"

    def test_empty_returns_unknown(self):
        lang = detect_language("")
        assert lang == "unknown"

    def test_garbage_returns_unknown(self):
        lang = detect_language("!!!@@@###")
        assert lang in ("unknown", "en")


class TestIsLatin:
    def test_pure_ascii(self):
        assert is_latin("Hello World") is True

    def test_indic_text(self):
        assert is_latin("এটি বাংলা") is False

    def test_mixed_with_indic(self):
        assert is_latin("Hello বাংলা") is False

    def test_empty_string(self):
        assert is_latin("") is True


class TestIsIndic:
    def test_known_indic(self):
        assert is_indic("bn") is True
        assert is_indic("hi") is True
        assert is_indic("ta") is True

    def test_unknown(self):
        assert is_indic("xx") is False

    def test_latin(self):
        assert is_indic("en") is False


class TestConvertToLatin:
    def test_indic_conversion(self):
        result = convert_to_latin("এটি বাংলা", "bn")
        assert len(result) > 0
        assert result != "এটি বাংলা"
        # Should not contain Bengali script characters (U+0980-U+09FF)
        for ch in result:
            assert not ("ঀ" <= ch <= "৿"), f"Found Bengali char: {ch}"

    def test_already_latin(self):
        result = convert_to_latin("Hello World", "en")
        assert result == "Hello World"

    def test_none_lang_uses_detection(self):
        result = convert_to_latin("Hello")
        assert "Hello" in result