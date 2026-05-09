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
    QLineEdit,
    QAbstractItemView,
    QMenu,
    QMessageBox,
    QProgressDialog,
)
from PyQt5.QtCore import pyqtSignal, Qt, QThread, QTimer
from PyQt5.QtGui import QColor

from models.translation_model import TranslationModel
from core.config import AppConfig

from core.language import SUPPORTED_LANGUAGES
from ui.translation_worker import TranslationWorker


class ListScreen(QWidget):
    open_editor = pyqtSignal(int)

    def __init__(self, model: TranslationModel, config: AppConfig):
        super().__init__()
        self.model = model
        self.config = config
        self.translation_thread = None
        self.translation_worker = None
        self.translation_progress = None
        self.translation_updated = 0
        self.translation_failed = False
        self.translation_dirty = False
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(200)
        self.search_timer.timeout.connect(self.populate_table)

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
        # 🔹 Search Row
        # ---------------------------
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search source or translation...")
        self.search_input.textChanged.connect(self.schedule_search)

        self.clear_search_btn = QPushButton("Clear")
        self.clear_search_btn.clicked.connect(self.clear_search)

        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(self.clear_search_btn)

        layout.addLayout(search_layout)

        # ---------------------------
        # 🔹 Table (2 columns)
        # ---------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels([f"Source", f"Translation"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.cellDoubleClicked.connect(self.handle_double_click)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

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
        search_text = self.search_input.text().strip().lower()
        filtered_data = []

        for model_row, (idx, source_text) in enumerate(data):
            translated = self.model.get_translation(idx)
            if search_text and (
                search_text not in source_text.lower()
                and search_text not in translated.lower()
            ):
                continue

            filtered_data.append((model_row, idx, source_text, translated))

        self.table.setRowCount(len(filtered_data))

        for row, (model_row, idx, source_text, translated) in enumerate(filtered_data):
            # Source column
            src_item = QTableWidgetItem(source_text)
            src_item.setData(Qt.UserRole, model_row)
            src_item.setFlags(
                Qt.ItemFlags(src_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            )

            # Target column
            tgt_item = QTableWidgetItem(translated)
            tgt_item.setData(Qt.UserRole, model_row)

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
    def schedule_search(self):
        self.search_timer.start()

    def clear_search(self):
        self.search_input.clear()
        self.search_timer.stop()
        self.populate_table()

    def table_row_to_model_row(self, table_row):
        item = self.table.item(table_row, 0)
        if not item:
            return None
        return item.data(Qt.UserRole)

    def selected_rows(self):
        rows = set()
        selection_model = self.table.selectionModel()

        if selection_model:
            for index in selection_model.selectedRows():
                model_row = self.table_row_to_model_row(index.row())
                if model_row is not None:
                    rows.add(model_row)

        current_row = self.table.currentRow()

        if not rows and current_row >= 0:
            model_row = self.table_row_to_model_row(current_row)
            if model_row is not None:
                rows.add(model_row)

        return sorted(rows)

    def show_context_menu(self, position):
        clicked_index = self.table.indexAt(position)
        selection_model = self.table.selectionModel()
        is_selected = (
            selection_model.isSelected(clicked_index)
            if selection_model and clicked_index.isValid()
            else False
        )

        if clicked_index.isValid() and not is_selected:
            self.table.selectRow(clicked_index.row())

        selected_rows = self.selected_rows()
        if not selected_rows:
            return

        count = len(selected_rows)
        suffix = "Item" if count == 1 else f"{count} Items"

        menu = QMenu(self)
        clean_action = menu.addAction(f"Clean Translation for {suffix}")
        translate_action = menu.addAction(f"Auto-Translate {suffix}")
        clean_translate_action = menu.addAction(f"Clean and Auto-Translate {suffix}")

        action = menu.exec_(self.table.viewport().mapToGlobal(position))

        if action == clean_action:
            self.clean_selected_translations()
        elif action == translate_action:
            self.auto_translate_selected(clean_first=False)
        elif action == clean_translate_action:
            self.auto_translate_selected(clean_first=True)

    def clean_selected_translations(self):
        rows = self.selected_rows()
        if not rows:
            return

        for row in rows:
            idx, _ = self.model.get_item_by_index(row)
            self.model.translations[idx] = ""

        self.model.save_target_file(output_dir=self.config.data_dir)
        self.populate_table()
        self.show_progress()

    def auto_translate_selected(self, clean_first=False):
        rows = self.selected_rows()
        if not rows:
            return

        if not self.model.target_lang:
            QMessageBox.critical(self, "Error", "Target language not set")
            return

        if self.translation_thread and self.translation_thread.isRunning():
            QMessageBox.information(self, "Translation Running", "Please wait for the current translation to finish.")
            return

        items = []
        for row in rows:
            idx, source_text = self.model.get_item_by_index(row)
            if clean_first:
                self.model.translations[idx] = ""
            items.append((idx, source_text))

        self.translation_updated = 0
        self.translation_failed = False
        self.translation_dirty = clean_first
        self.translation_progress = QProgressDialog(
            "Translating selected items...",
            "Cancel",
            0,
            len(items),
            self,
        )
        self.translation_progress.setWindowModality(Qt.WindowModal)
        self.translation_progress.setMinimumDuration(0)

        timeout = self.config.get_int("api", "timeout", fallback=10)
        self.translation_thread = QThread(self)
        self.translation_worker = TranslationWorker(
            items,
            self.model.src_lang,
            self.model.target_lang,
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

    def handle_translation_progress(self, position, total, idx):
        if not self.translation_progress:
            return

        self.translation_progress.setMaximum(total)
        self.translation_progress.setLabelText(f"Translating item #{idx}...")
        self.translation_progress.setValue(position - 1)

    def handle_item_translated(self, idx, translated):
        self.model.translations[idx] = translated.strip()
        self.translation_updated += 1

    def handle_translation_error(self, message):
        self.translation_failed = True
        QMessageBox.critical(self, "Error", message)

    def handle_translation_finished(self, cancelled):
        if self.translation_progress:
            self.translation_progress.setValue(self.translation_progress.maximum())
            self.translation_progress.close()
            self.translation_progress = None

        if self.translation_updated or self.translation_dirty:
            self.model.save_target_file(output_dir=self.config.data_dir)
            self.populate_table()
            self.show_progress()

        self.translation_worker = None
        self.translation_thread = None
        self.translation_updated = 0
        self.translation_dirty = False

        if cancelled and not self.translation_failed:
            QMessageBox.information(self, "Translation Stopped", "Translation was cancelled.")

        self.translation_failed = False

    def open_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            model_row = self.table_row_to_model_row(row)
            if model_row is not None:
                self.open_editor.emit(model_row)

    def handle_double_click(self, row, col):
        model_row = self.table_row_to_model_row(row)
        if model_row is not None:
            self.open_editor.emit(model_row)

    def show_progress(self):
        percent = self.model.completion_percentage()
        total = self.model.total_items()
        done = self.model.translated_count()

        self.progress_label.setText(f"{percent:.1f}% ({done}/{total})")
