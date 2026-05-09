# ui/translation_worker.py

from PyQt5.QtCore import QObject, pyqtSignal

from core.translator import TranslateClient


class TranslationWorker(QObject):
    item_translated = pyqtSignal(int, str)
    progress = pyqtSignal(int, int, int)
    error = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, items, source_lang, target_lang, timeout=10):
        super().__init__()
        self.items = items
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.timeout = timeout
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        translator = TranslateClient(timeout=self.timeout)
        total = len(self.items)

        for position, item in enumerate(self.items, start=1):
            if self._cancelled:
                self.finished.emit(True)
                return

            idx, source_text = item
            self.progress.emit(position, total, idx)

            try:
                translated = translator.translate(
                    source_text,
                    self.source_lang,
                    self.target_lang,
                )
            except Exception as e:
                self.error.emit(str(e))
                self.finished.emit(True)
                return

            self.item_translated.emit(idx, translated)

        self.finished.emit(False)
