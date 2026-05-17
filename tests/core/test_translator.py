"""Unit tests for core.translator."""

from core import translator as translator_module
from core.translator import TranslateClient


class FakeGoogleTranslator:
    instances = []

    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.calls = []
        FakeGoogleTranslator.instances.append(self)

    def translate(self, text):
        self.calls.append(text)
        return f"{self.source}->{self.target}:{text}"


def test_blank_text_returns_empty_without_creating_translator(monkeypatch):
    monkeypatch.setattr(translator_module, "GoogleTranslator", FakeGoogleTranslator)
    FakeGoogleTranslator.instances = []

    client = TranslateClient()

    assert client.translate("   ", "en", "bn") == ""
    assert FakeGoogleTranslator.instances == []


def test_translate_delegates_to_google_translator(monkeypatch):
    monkeypatch.setattr(translator_module, "GoogleTranslator", FakeGoogleTranslator)
    FakeGoogleTranslator.instances = []

    client = TranslateClient()

    assert client.translate("Hello", "en", "bn") == "en->bn:Hello"
    assert FakeGoogleTranslator.instances[0].calls == ["Hello"]


def test_get_translator_caches_by_language_pair(monkeypatch):
    monkeypatch.setattr(translator_module, "GoogleTranslator", FakeGoogleTranslator)
    FakeGoogleTranslator.instances = []
    client = TranslateClient()

    first = client.get_translator("en", "bn")
    second = client.get_translator("en", "bn")
    other = client.get_translator("bn", "en")

    assert first is second
    assert other is not first
    assert len(FakeGoogleTranslator.instances) == 2
