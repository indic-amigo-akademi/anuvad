"""Unit tests for core.config."""

import configparser

import pytest

from core import config as config_module
from core.config import AppConfig


@pytest.fixture
def config_path(tmp_path):
    return tmp_path / "test.cfg"


@pytest.fixture
def app_config(config_path, tmp_path, monkeypatch):
    monkeypatch.setattr(
        config_module.os.path, "expanduser", lambda path: str(tmp_path / "home")
    )
    return AppConfig(str(config_path))


def test_missing_config_creates_default_file(config_path, tmp_path, monkeypatch):
    monkeypatch.setattr(
        config_module.os.path, "expanduser", lambda path: str(tmp_path / "home")
    )

    cfg = AppConfig(str(config_path))

    assert config_path.exists()
    assert cfg.appname == "Anuvad"
    assert cfg.appversion == "1.0"
    assert cfg.author == "Anonymous"
    assert cfg.default_source_lang == "en"
    assert cfg.default_target_lang == "bn"
    assert cfg.auto_detect is True


def test_data_and_export_dirs_are_created_under_config_dir(app_config, tmp_path):
    data_dir = app_config.data_dir
    export_dir = app_config.export_dir

    assert data_dir == str(tmp_path / "home" / ".anuvad" / "data")
    assert export_dir == str(tmp_path / "home" / ".anuvad" / "exports")
    assert (tmp_path / "home" / ".anuvad" / "data").is_dir()
    assert (tmp_path / "home" / ".anuvad" / "exports").is_dir()


def test_getters_return_typed_values(app_config):
    assert app_config.get("ui", "font_family") == "'Segoe UI', 'Nirmala UI', sans-serif"
    assert app_config.get_int("ui", "font_size") == 14
    assert app_config.get_bool("language", "auto_detect") is True
    assert app_config.get("missing", "key", fallback="fallback") == "fallback"


def test_set_persists_value_and_clears_stylesheet_cache(app_config):
    app_config._stylesheet_cache["light"] = "cached"

    app_config.set("ui", "theme", "dark")

    persisted = configparser.ConfigParser()
    persisted.read(app_config.filepath)
    assert persisted.get("ui", "theme") == "dark"
    assert app_config._stylesheet_cache == {}


def test_set_creates_missing_section(app_config):
    app_config.set("custom", "enabled", "yes")

    assert app_config.get("custom", "enabled") == "yes"


def test_theme_stylesheet_is_cached(app_config, monkeypatch):
    calls = []

    def fake_load_qss(path):
        calls.append(path)
        return f"/* {path} */"

    monkeypatch.setattr(config_module, "load_qss", fake_load_qss)

    first = app_config.get_theme_stylesheet()
    second = app_config.get_theme_stylesheet()

    assert first == second
    assert calls == [
        config_module.os.path.join("assets", "qss", "main.qss"),
        config_module.os.path.join("assets", "qss", "light.qss"),
    ]


def test_tr_uses_configured_ui_language(app_config, monkeypatch):
    monkeypatch.setattr(
        config_module,
        "translate",
        lambda key, language, **kwargs: f"{language}:{key}:{kwargs['name']}",
    )
    app_config.set("ui", "language", "bn")

    assert app_config.tr("greeting", name="Anuvad") == "bn:greeting:Anuvad"
