# ui/editor_screen.py

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QSplitter,
    QMessageBox,
    QProgressDialog,
)
from PyQt5.QtCore import pyqtSignal, Qt, QThread

from core.config import AppConfig
from core.language import convert_to_latin, is_latin
from ui.translation_worker import TranslationWorker


class EditorScreen(QWidget):
    back_to_list = pyqtSignal()

    def __init__(self, model, config: AppConfig):
        super().__init__()
        self.model = model
        self.config = config
        self.translation_thread = None
        self.translation_worker = None
        self.translation_progress = None
        self.translation_failed = False
        self.current_translation_dirty = False
        self.loading_current = False

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Header
        self.title = QLabel("Translation Editor")
        self.title.setObjectName("title")
        main_layout.addWidget(self.title)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(5)

        left_label = QLabel("Source Text")
        left_layout.addWidget(left_label)

        self.source_text = QTextEdit()
        self.source_text.setReadOnly(True)
        left_layout.addWidget(self.source_text)

        self.source_text_roman = QLabel()
        self.source_text_roman.setWordWrap(True)
        self.source_text_roman.setFixedHeight(200)
        left_layout.addWidget(self.source_text_roman)
        self.set_latin_text(self.source_text.toPlainText(), self.source_text_roman)

        left_panel.setLayout(left_layout)

        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)

        right_label = QLabel("Translated Text")
        right_layout.addWidget(right_label)

        self.translated_text = QTextEdit()
        right_layout.addWidget(self.translated_text)

        self.translated_text_roman = QLabel()
        self.translated_text_roman.setWordWrap(True)
        self.translated_text_roman.setFixedHeight(200)
        right_layout.addWidget(self.translated_text_roman)
        self.set_latin_text(self.translated_text.toPlainText(), self.translated_text_roman)

        right_panel.setLayout(right_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([450, 450])

        main_layout.addWidget(splitter, stretch=1)

        # ---------------------------
        # 🔹 Navigation bar
        # ---------------------------
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)

        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self.go_previous)

        self.auto_btn = QPushButton("Auto Translate")
        self.auto_btn.setObjectName("primary")
        self.auto_btn.setIcon(
            config.get_icon("translate")
        )
        self.auto_btn.clicked.connect(self.auto_translate)

        self.save_btn = QPushButton("Save")
        self.save_btn.setIcon(
            config.get_icon("save")
        )
        self.save_btn.setObjectName("accent")
        self.save_btn.clicked.connect(lambda: self.save_translation(True))

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.go_next)

        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.go_back)

        self.translated_text.textChanged.connect(self.handle_translation_text_changed)
        self.source_text.textChanged.connect(lambda: self.set_latin_text(self.source_text.toPlainText(), self.source_text_roman))

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.auto_btn)
        nav_layout.addWidget(self.save_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.back_btn)

        main_layout.addLayout(nav_layout)

        self.setLayout(main_layout)

    def set_latin_text(self, text:str, label:QLabel):
        if is_latin(text):
            label.setText("")
        else:
            label.setText(convert_to_latin(text))

    # ---------------------------
    # 🔹 Load Data
    # ---------------------------
    def load_current(self):
        self.loading_current = True
        self.source_text.setText(self.model.get_current_source_text())
        self.translated_text.setText(self.model.get_current_translation())
        self.current_translation_dirty = False
        self.loading_current = False

    def handle_translation_text_changed(self):
        self.set_latin_text(self.translated_text.toPlainText(), self.translated_text_roman)
        if not self.loading_current:
            self.current_translation_dirty = True

    # ---------------------------
    # 🔹 Save
    # ---------------------------
    def save_translation(self, save_to_file=True):
        self.model.save_current_translation(
            self.translated_text.toPlainText(), save_to_file=save_to_file
        )
        self.current_translation_dirty = False
        if save_to_file:
            QMessageBox.information(self, "Success", "Translation saved")

    def save_if_dirty(self, save_to_file=False):
        if self.current_translation_dirty:
            self.save_translation(save_to_file=save_to_file)

    def save_changes(self):
        self.save_if_dirty(save_to_file=False)
        if not self.model.target_lang:
            QMessageBox.critical(self, "Error", "Target language not set")
            return

        self.model.save_target_file(output_dir=self.config.data_dir)
        QMessageBox.information(self, "Success", "Translation saved")

    # ---------------------------
    # 🔹 Auto Translate
    # ---------------------------
    def auto_translate(self):
        source_text = self.model.get_current_source_text()
        src_lang = self.model.src_lang
        tgt_lang = self.model.target_lang
        current_id = self.model.get_current_id()

        if not tgt_lang:
            QMessageBox.critical(self, "Error", "Target language not set")
            return

        if current_id is None:
            return

        if self.translation_thread and self.translation_thread.isRunning():
            QMessageBox.information(self, "Translation Running", "Please wait for the current translation to finish.")
            return

        self.translation_failed = False
        self.set_translation_controls_enabled(False)
        self.translation_progress = QProgressDialog(
            "Translating current item...",
            "Cancel",
            0,
            1,
            self,
        )
        self.translation_progress.setWindowModality(Qt.WindowModal)
        self.translation_progress.setMinimumDuration(0)

        timeout = self.config.get_int("api", "timeout", fallback=10)
        self.translation_thread = QThread(self)
        self.translation_worker = TranslationWorker(
            [(current_id, source_text)],
            src_lang,
            tgt_lang,
            timeout=timeout,
        )
        self.translation_worker.moveToThread(self.translation_thread)

        self.translation_thread.started.connect(self.translation_worker.run)
        self.translation_worker.progress.connect(self.handle_translation_progress)
        self.translation_worker.item_translated.connect(self.handle_item_translated)
        self.translation_worker.error.connect(self.handle_translation_error)
        self.translation_worker.finished.connect(self.handle_translation_finished)
        self.translation_worker.finished.connect(self.translation_thread.quit)
        self.translation_worker.finished.connect(self.translation_worker.deleteLater)
        self.translation_thread.finished.connect(self.translation_thread.deleteLater)
        self.translation_progress.canceled.connect(self.translation_worker.cancel)

        self.translation_thread.start()

    def set_translation_controls_enabled(self, enabled):
        self.auto_btn.setEnabled(enabled)
        self.prev_btn.setEnabled(enabled)
        self.next_btn.setEnabled(enabled)
        self.back_btn.setEnabled(enabled)

    def handle_translation_progress(self, position, total, idx):
        if not self.translation_progress:
            return

        self.translation_progress.setMaximum(total)
        self.translation_progress.setLabelText(f"Translating item #{idx}...")
        self.translation_progress.setValue(position - 1)

    def handle_item_translated(self, idx, translated):
        if idx == self.model.get_current_id():
            self.translated_text.setText(translated)

    def handle_translation_error(self, message):
        self.translation_failed = True
        QMessageBox.critical(self, "Error", message)

    def handle_translation_finished(self, cancelled):
        if self.translation_progress:
            self.translation_progress.setValue(self.translation_progress.maximum())
            self.translation_progress.close()
            self.translation_progress = None

        self.set_translation_controls_enabled(True)
        self.translation_worker = None
        self.translation_thread = None

        if cancelled and not self.translation_failed:
            QMessageBox.information(self, "Translation Stopped", "Translation was cancelled.")

        self.translation_failed = False

    # ---------------------------
    # 🔹 Navigation
    # ---------------------------
    def go_next(self):
        self.save_if_dirty(save_to_file=False)
        if self.model.has_next():
            self.model.next()
            self.load_current()

    def go_previous(self):
        self.save_if_dirty(save_to_file=False)
        if self.model.has_previous():
            self.model.previous()
            self.load_current()

    def go_back(self):
        self.save_if_dirty(save_to_file=False)
        self.back_to_list.emit()
