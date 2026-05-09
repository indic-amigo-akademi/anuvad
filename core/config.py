# core/config.py

import configparser
import os
from PyQt5.QtGui import QIcon
from core.file_handler import load_qss, resource_path


class AppConfig:
    def __init__(self, filepath="app.cfg"):
        self.filepath = resource_path(filepath)
        self.config = configparser.ConfigParser()
        self.config_dir = os.path.join(os.path.expanduser("~"), ".anuvad")
        self._stylesheet_cache = {}
        self._icon_cache = {}

        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            self._create_default()

        self.config.read(self.filepath)

    def _create_default(self):
        self.config["app"] = {"name": "Anuvad", "version": "1.0", "author": ""}

        self.config["paths"] = {"data_dir": "data", "default_export_dir": "exports"}

        self.config["user"] = {"author": "Anonymous"}

        self.config["language"] = {
            "default_source": "en",
            "default_target": "bn",
            "auto_detect": "true",
        }

        self.config["ui"] = {
            "theme": "light",
            "font_family": "'Segoe UI', 'Nirmala UI', sans-serif",
            "font_size": "14",
        }

        with open(self.filepath, "w") as f:
            self.config.write(f)

    # ---------------------------
    # 🔹 Getters
    # ---------------------------
    def get(self, section, key, fallback=None):
        return self.config.get(section, key, fallback=fallback)

    def get_int(self, section, key, fallback=0):
        return self.config.getint(section, key, fallback=fallback)

    def get_bool(self, section, key, fallback=False):
        return self.config.getboolean(section, key, fallback=fallback)

    # ---------------------------
    # 🔹 Paths
    # ---------------------------
    @property
    def data_dir(self):
        data_dir_path = os.path.join(
            self.config_dir, self.get("paths", "data_dir", "data") or "data"
        )
        if not os.path.exists(data_dir_path):
            os.makedirs(data_dir_path)
        return data_dir_path

    @property
    def export_dir(self):
        export_dir_path = os.path.join(
            self.config_dir,
            self.get("paths", "default_export_dir", "exports") or "exports",
        )
        if not os.path.exists(export_dir_path):
            os.makedirs(export_dir_path)
        return export_dir_path

    # ---------------------------
    # 🔹 User
    # ---------------------------
    @property
    def author(self):
        return self.get("user", "author", "Anonymous")

    # ---------------------------
    # 🔹 Language
    # ---------------------------
    @property
    def default_source_lang(self):
        return self.get("language", "default_source", "en")

    @property
    def default_target_lang(self):
        return self.get("language", "default_target", "bn")

    @property
    def auto_detect(self):
        return self.get_bool("language", "auto_detect", True)

    # ---------------------------
    # 🔹 UI
    # ---------------------------
    @property
    def font_family(self):
        return self.get("ui", "font_family", "Segoe UI")

    @property
    def font_size(self):
        return self.get_int("ui", "font_size", 14)

    @property
    def theme(self):
        return self.get("ui", "theme", "light")

    @property
    def appname(self):
        return self.get("app", "name", "Anuvad")

    @property
    def appauthor(self):
        return self.get("app", "author", "Anonymous")

    @property
    def appversion(self):
        return self.get("app", "version", "1.0")

    def get_theme_stylesheet(self):
        theme = self.theme
        if theme in self._stylesheet_cache:
            return self._stylesheet_cache[theme]

        stylesheet = (
            load_qss(os.path.join("assets", "qss", "main.qss"))
            + "\n"
            + load_qss(os.path.join("assets", "qss", f"{theme}.qss"))
        )
        self._stylesheet_cache[theme] = stylesheet
        return stylesheet

    # ---------------------------
    # 🔹 Save
    # ---------------------------
    def save(self):
        with open(self.filepath, "w") as f:
            self.config.write(f)

    def set(self, section, key, value):
        self.config.set(section, key, value)
        self.save()
        if section == "ui":
            self._stylesheet_cache.clear()

    def get_icon(self, name, color="light"):
        cache_key = (name, color)
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        icon_path = resource_path(os.path.join("assets", "icons", f"{name}.svg"))
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            icon.setThemeName(color)
        else:
            icon = QIcon(resource_path(os.path.join("assets", "icons", "default.svg")))

        self._icon_cache[cache_key] = icon
        return icon
