# core/translator.py
from deep_translator import (
    GoogleTranslator,
    MyMemoryTranslator,
    LingueeTranslator,
    PonsTranslator,
    MicrosoftTranslator,
    LibreTranslator,
)
from core.language import SUPPORTED_LANGUAGES

SUPPORTED_TRANSLATION_MODELS = [
    "google",
    "mymemory",
    "linguee",
    "pons",
    "microsoft",
    "libre",
]


class TranslateClient:
    def __init__(self, model="google", **kwargs):
        self._translators = {}
        self.model = model
        # self.__api_key = api_key
        self.__kwargs = kwargs

        if model not in SUPPORTED_TRANSLATION_MODELS:
            raise ValueError(f"Unsupported translation model: {model}")

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
            if self.model == "google":
                self._translators[key] = GoogleTranslator(source=source, target=target)
            elif self.model == "mymemory":
                self._translators[key] = MyMemoryTranslator(
                    source=SUPPORTED_LANGUAGES[source].lower(),
                    target=SUPPORTED_LANGUAGES[target].lower(),
                )
            elif self.model == "linguee":
                self._translators[key] = LingueeTranslator(
                    source=SUPPORTED_LANGUAGES[source].lower(),
                    target=SUPPORTED_LANGUAGES[target].lower(),
                )
            elif self.model == "pons":
                self._translators[key] = PonsTranslator(source=source, target=target)
            elif self.model == "microsoft":
                self._translators[key] = MicrosoftTranslator(
                    source=source, target=target, **self.__kwargs
                )
            elif self.model == "libre":
                self._translators[key] = LibreTranslator(source=source, target=target, **self.__kwargs)
            else:
                raise ValueError(f"Unsupported translation model: {self.model}")
        return self._translators[key]
