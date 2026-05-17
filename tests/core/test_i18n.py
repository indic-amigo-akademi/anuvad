"""Unit tests for core.i18n."""

from core import i18n


def test_translate_returns_requested_language_value(monkeypatch):
    monkeypatch.setattr(
        i18n,
        "TRANSLATIONS",
        {
            "en": {"greeting": "Hello"},
            "bn": {"greeting": "Nomoskar"},
        },
    )

    assert i18n.translate("greeting", "bn") == "Nomoskar"


def test_translate_falls_back_to_english(monkeypatch):
    monkeypatch.setattr(i18n, "TRANSLATIONS", {"en": {"save": "Save"}, "bn": {}})

    assert i18n.translate("save", "bn") == "Save"
    assert i18n.translate("save", "missing") == "Save"


def test_translate_falls_back_to_key_when_missing(monkeypatch):
    monkeypatch.setattr(i18n, "TRANSLATIONS", {"en": {}})

    assert i18n.translate("unknown.key", "en") == "unknown.key"


def test_translate_formats_kwargs(monkeypatch):
    monkeypatch.setattr(
        i18n,
        "TRANSLATIONS",
        {"en": {"welcome": "Welcome, {name}."}},
    )

    assert i18n.translate("welcome", "en", name="Asha") == "Welcome, Asha."
