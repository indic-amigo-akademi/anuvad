"""Shared pytest fixtures for Anuvad tests."""

import configparser
import os

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QWidget

from core.config import AppConfig
from models.translation_model import TranslationModel

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class SimpleQtBot:
    """Small qtbot-compatible helper backed by PyQt5.QtTest."""

    def __init__(self, app):
        self.app = app
        self.widgets = []

    def addWidget(self, widget):
        self.widgets.append(widget)
        widget.show()
        self.app.processEvents()

    def mouseClick(self, widget: QWidget, button: Qt.MouseButton = Qt.LeftButton):
        QTest.mouseClick(widget, button)
        self.app.processEvents()

    def mouseDClick(self, widget: QWidget, button: Qt.MouseButton = Qt.LeftButton):
        QTest.mouseDClick(widget, button)
        self.app.processEvents()

    def keyClicks(self, widget: QWidget, text: str):
        QTest.keyClicks(widget, text)
        self.app.processEvents()

    def wait(self, ms: int):
        QTest.qWait(ms)
        self.app.processEvents()


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


@pytest.fixture
def qtbot(qapp):
    return SimpleQtBot(qapp)


@pytest.fixture
def app_config(tmp_path, monkeypatch):
    monkeypatch.setattr(os.path, "expanduser", lambda path: str(tmp_path / "home"))

    cfg = configparser.ConfigParser()
    cfg["app"] = {"name": "TestApp", "version": "1.0", "author": "Tester"}
    cfg["paths"] = {
        "data_dir": str(tmp_path / "data"),
        "default_export_dir": str(tmp_path / "exports"),
    }
    cfg["user"] = {"author": "Test Author"}
    cfg["language"] = {
        "default_source": "en",
        "default_target": "bn",
        "auto_detect": "true",
    }
    cfg["ui"] = {
        "theme": "light",
        "language": "en",
        "font_family": "sans-serif",
        "font_size": "14",
    }

    cfg_path = tmp_path / "test.cfg"
    with open(cfg_path, "w", encoding="utf-8") as f:
        cfg.write(f)

    return AppConfig(str(cfg_path))


@pytest.fixture
def translation_model(app_config):
    return TranslationModel(app_config)


@pytest.fixture
def loaded_model(translation_model):
    translation_model.load_source_text(
        [(1, "Hello"), (2, "World"), (3, "Goodbye")],
        "testbook",
        "en",
    )
    translation_model.set_target_lang("bn", data_dir=translation_model.config.data_dir)
    return translation_model
