# core/config.py

import configparser
import os


class AppConfig:
    def __init__(self, filepath="app.cfg"):
        self.filepath = filepath
        self.config = configparser.ConfigParser()

        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            self._create_default()

        self.config.read(self.filepath)

    def _create_default(self):
        self.config["app"] = {
            "name": "Anuvad",
            "version": "1.0"
        }

        self.config["paths"] = {
            "data_dir": "data",
            "default_export_dir": "exports"
        }

        self.config["user"] = {
            "author": "Unknown"
        }

        self.config["language"] = {
            "default_source": "en",
            "default_target": "bn",
            "auto_detect": "true"
        }

        self.config["ui"] = {
            "theme": "light",
            "font_family": "Segoe UI",
            "font_size": "14"
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
        return self.get("paths", "data_dir", "data")

    @property
    def export_dir(self):
        return self.get("paths", "default_export_dir", "exports")

    # ---------------------------
    # 🔹 User
    # ---------------------------
    @property
    def author(self):
        return self.get("user", "author", "Unknown")

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