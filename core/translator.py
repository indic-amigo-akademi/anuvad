# core/translator.py
from deep_translator import GoogleTranslator


class TranslateClient:
    def __init__(self):
        self._translators = {}

    # ---------------------------
    # 🔹 Single Translation
    # ---------------------------
    def translate(self, text: str, source: str, target: str) -> str:
        if not text.strip():
            return ""

        translator = self.get_translator(source, target)
        return translator.translate(text)

    def get_translator(self, source: str, target: str):
        key = (source, target)
        if key not in self._translators:
            self._translators[key] = GoogleTranslator(source=source, target=target)
        return self._translators[key]
