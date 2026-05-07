# ui/list_screen.py

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QComboBox,
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QColor

from models.translation_model import TranslationModel
from core.config import AppConfig

from core.language import SUPPORTED_LANGUAGES


class ListScreen(QWidget):
    open_editor = pyqtSignal(int)

    def __init__(self, model: TranslationModel, config: AppConfig):
        super().__init__()
        self.model = model
        self.config = config

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # ---------------------------
        # 🔹 Header Row
        # ---------------------------
        header_layout = QHBoxLayout()

        self.title = QLabel("Text Segments")
        self.title.setObjectName("title")

        self.lang_dropdown = QComboBox()
        self.lang_dropdown.currentIndexChanged.connect(self.change_target_language)

        header_layout.addWidget(self.title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Target Language:"))
        header_layout.addWidget(self.lang_dropdown)

        layout.addLayout(header_layout)

        # ---------------------------
        # 🔹 Table (2 columns)
        # ---------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels([f"Source", f"Translation"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.cellDoubleClicked.connect(self.handle_double_click)

        layout.addWidget(self.table, stretch=1)

        # ---------------------------
        # 🔹 Bottom Row
        # ---------------------------
        bottom_layout = QHBoxLayout()

        self.progress_label = QLabel("Show Progress")
        # self.progress_btn.clicked.connect(self.show_progress)

        self.open_btn = QPushButton("Open Selected")
        self.open_btn.clicked.connect(self.open_selected)

        bottom_layout.addWidget(self.progress_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.open_btn)

        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    # ---------------------------
    # 🔹 Refresh UI
    # ---------------------------
    def refresh(self):        
        self.table.setHorizontalHeaderLabels([f"Source ({self.model.src_lang})", f"Translation ({self.model.target_lang})"])
        self.populate_language_dropdown()
        self.populate_table()
        self.show_progress()

    # ---------------------------
    # 🔹 Language Dropdown
    # ---------------------------
    def populate_language_dropdown(self):
        self.lang_dropdown.blockSignals(True)
        self.lang_dropdown.clear()

        src_lang = self.model.src_lang

        for code, name in SUPPORTED_LANGUAGES.items():
            if code != src_lang and code in self.model.avl_tgt_langs:
                self.lang_dropdown.addItem(name, code)
        for code, name in SUPPORTED_LANGUAGES.items():
            if code != src_lang and code not in self.model.avl_tgt_langs:
                self.lang_dropdown.addItem(name, code)

        # Set default target
        if self.model.target_lang:
            index = self.lang_dropdown.findData(self.model.target_lang)
            if index >= 0:
                self.lang_dropdown.setCurrentIndex(index)
        else:
            # fallback to config default
            default = self.config.default_target_lang
            index = self.lang_dropdown.findData(default)
            if index >= 0:
                self.lang_dropdown.setCurrentIndex(index)

        self.lang_dropdown.blockSignals(False)

        # Apply selected
        self.change_target_language()

    def change_target_language(self):
        lang = self.lang_dropdown.currentData()
        if lang:
            self.model.set_target_lang(lang, data_dir=self.config.data_dir)
            self.table.setHorizontalHeaderLabels([f"Source ({self.model.src_lang})", f"Translation ({self.model.target_lang})"])
            self.populate_table()

    def resize_columns_equally(self):
        viewport = self.table.viewport()
        if viewport is None:
            return

        total_width = viewport.width()
        col_width = total_width // 2

        self.table.setColumnWidth(0, col_width)
        self.table.setColumnWidth(1, col_width)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_columns_equally()

    # ---------------------------
    # 🔹 Table Population
    # ---------------------------
    def populate_table(self):
        data = self.model.source_data
        self.table.setRowCount(len(data))

        for row, (idx, source_text) in enumerate(data):
            # Source column
            src_item = QTableWidgetItem(source_text)
            src_item.setFlags(
                Qt.ItemFlags(src_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            )

            # Target column
            translated = self.model.get_translation(idx)
            tgt_item = QTableWidgetItem(translated)

            # Optional: highlight translated rows
            if translated.strip():
                tgt_item.setBackground(QColor("lightgreen"))
                tgt_item.setForeground(QColor("black"))

            self.table.setItem(row, 0, src_item)
            self.table.setItem(row, 1, tgt_item)

        self.resize_columns_equally()

    # ---------------------------
    # 🔹 Actions
    # ---------------------------
    def open_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            self.open_editor.emit(row)

    def handle_double_click(self, row, col):
        self.open_editor.emit(row)

    def show_progress(self):
        percent = self.model.completion_percentage()
        total = self.model.total_items()
        done = self.model.translated_count()

        self.progress_label.setText(f"{percent:.1f}% ({done}/{total})")
