# core/config.py

import configparser
import os
import shutil
from PyQt5.QtGui import QIcon
from core.file_handler import load_qss, resource_path, user_data_path
from core.i18n import translate


class AppConfig:
    def __init__(self, filepath="app.cfg"):
        self.filepath = user_data_path(filepath)
        self.config = configparser.ConfigParser()
        # self.config_dir = os.path.join(os.path.expanduser("~"), ".anuvad")
        self._stylesheet_cache = {}
        self._icon_cache = {}

        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            self._create_default()

        self.config.read(self.filepath)

    def _create_default(self):
        shutil.copyfile(resource_path("app.cfg"), self.filepath)

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
        data_dir_path = user_data_path(self.get("paths", "data_dir", "data") or "data")

        if not os.path.exists(data_dir_path):
            os.makedirs(data_dir_path)
        return data_dir_path

    @property
    def export_dir(self):
        export_dir_path = user_data_path(
            self.get("paths", "export_dir", "exports") or "exports"
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
    def ui_language(self):
        return self.get("ui", "language", "en")

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
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self.save()
        if section == "ui":
            self._stylesheet_cache.clear()

    def tr(self, key: str, **kwargs) -> str:
        return translate(key, self.ui_language or "en", **kwargs)

    def get_icon(self, name, color="light"):
        cache_key = (name, color)
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        icon_path = None
        candidate_paths = [
            os.path.join("assets", "icons", f"{name}_{color}.svg"),
            os.path.join("assets", "icons", color, f"{name}.svg"),
            os.path.join("assets", "icons", f"{name}.svg"),
        ]

        for candidate in candidate_paths:
            candidate_path = resource_path(candidate)
            if os.path.exists(candidate_path):
                icon_path = candidate_path
                break

        if icon_path is None:
            icon_path = resource_path(os.path.join("assets", "icons", "default.svg"))

        icon = QIcon(icon_path)
        self._icon_cache[cache_key] = icon
        return icon
