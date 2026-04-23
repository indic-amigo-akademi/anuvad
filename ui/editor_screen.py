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
    QStyle
)
from PyQt5.QtCore import pyqtSignal, Qt

from core.config import AppConfig
from core.translator import create_translator


class EditorScreen(QWidget):
    back_to_list = pyqtSignal()

    def __init__(self, model, config: AppConfig):
        super().__init__()
        self.model = model
        self.config = config

        # ✅ Translator
        self.translator = create_translator(config) if config else None

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

        left_panel.setLayout(left_layout)

        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)

        right_label = QLabel("Translated Text")
        right_layout.addWidget(right_label)

        self.translated_text = QTextEdit()
        right_layout.addWidget(self.translated_text)

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
            self.style().standardIcon(QStyle.SP_DialogSaveButton)
        )
        self.save_btn.setObjectName("accent")
        self.save_btn.clicked.connect(lambda: self.save_translation(True))

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.go_next)

        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.back_to_list.emit)

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.auto_btn)
        nav_layout.addWidget(self.save_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.back_btn)

        main_layout.addLayout(nav_layout)

        self.setLayout(main_layout)

    # ---------------------------
    # 🔹 Load Data
    # ---------------------------
    def load_current(self):
        self.source_text.setText(self.model.get_current_source_text())
        self.translated_text.setText(self.model.get_current_translation())

    # ---------------------------
    # 🔹 Save
    # ---------------------------
    def save_translation(self, save_to_file=True):
        self.model.save_current_translation(
            self.translated_text.toPlainText(), save_to_file=save_to_file
        )
        if save_to_file:
            QMessageBox.information(self, "Success", "Translation saved")

    # ---------------------------
    # 🔹 Auto Translate
    # ---------------------------
    def auto_translate(self):
        if not self.translator:
            QMessageBox.critical(self, "Error", "Translator not configured")
            return

        source_text = self.model.get_current_source_text()
        src_lang = self.model.src_lang
        tgt_lang = self.model.target_lang

        if not tgt_lang:
            QMessageBox.critical(self, "Error", "Target language not set")
            return

        try:
            translated = self.translator.translate(source_text, src_lang, tgt_lang)
            self.translated_text.setText(translated)

        except Exception as e:
            # self.translated_text.setText(f"[ERROR] {str(e)}")
            QMessageBox.critical(self, "Error", str(e))

    # ---------------------------
    # 🔹 Navigation
    # ---------------------------
    def go_next(self):
        self.save_translation(save_to_file=False)
        if self.model.has_next():
            self.model.next()
            self.load_current()

    def go_previous(self):
        self.save_translation(save_to_file=False)
        if self.model.has_previous():
            self.model.previous()
            self.load_current()
