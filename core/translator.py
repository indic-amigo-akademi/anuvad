# core/translator.py
from typing import Dict, List
import requests
from deep_translator import GoogleTranslator


class TranslateClient:
    def __init__(self, timeout: int = 10, throttle: int = 5):
        self.timeout = timeout
        self.throttle = throttle
        pass

    # ---------------------------
    # 🔹 Single Translation
    # ---------------------------
    def translate(self, text: str, source: str, target: str) -> str:
        if not text.strip():
            return ""

        self.translator = GoogleTranslator(source=source, target=target)

        return self.translator.translate(text)


# ---------------------------
# 🔹 Factory
# ---------------------------
def create_translator(config):
    return TranslateClient(
        timeout=config.get_int("api", "timeout", fallback=10)
    )
