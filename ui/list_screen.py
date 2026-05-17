# ui/list_screen.py

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QPushButton,
    QLabel,
    QComboBox,
    QLineEdit,
    QAbstractItemView,
    QMenu,
    QMessageBox,
    QProgressDialog,
)
from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
    QThread,
    QTimer,
    QAbstractTableModel,
    QSortFilterProxyModel,
)
from PyQt5.QtGui import QColor

from models.translation_model import TranslationModel
from core.config import AppConfig

from core.language import SUPPORTED_LANGUAGES
from ui.translation_worker import TranslationWorker


class TranslationTableModel(QAbstractTableModel):
    def __init__(self, translation_model: TranslationModel, config: AppConfig):
        super().__init__()
        self.translation_model = translation_model
        self.config = config

    def rowCount(self, parent=None):
        if parent is not None and parent.isValid():
            return 0
        return len(self.translation_model.source_data)

    def columnCount(self, parent=None):
        if parent is not None and parent.isValid():
            return 0
        return 3

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        if row < 0 or row >= len(self.translation_model.source_data):
            return None

        idx, source_text = self.translation_model.source_data[row]
        translated = self.translation_model.get_translation(idx) or ""

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return str(idx)
            if index.column() == 1:
                return source_text
            return translated

        if role == Qt.UserRole:
            return row

        if role == Qt.BackgroundRole and index.column() == 2 and translated.strip():
            return QColor("lightgreen")

        if role == Qt.ForegroundRole and index.column() == 2 and translated.strip():
            return QColor("black")

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole or orientation != Qt.Horizontal:
            return None

        if section == 0:
            return "#"

        if section == 1:
            return f"{self.config.tr('source')} ({self.translation_model.src_lang})"

        if section == 2:
            return f"{self.config.tr('translation')} ({self.translation_model.target_lang})"

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def refresh(self):
        self.beginResetModel()
        self.endResetModel()


class TranslationFilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.search_text = ""

    def set_search_text(self, text):
        self.search_text = text.strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.search_text:
            return True

        source_index = self.sourceModel().index(source_row, 1, source_parent)
        target_index = self.sourceModel().index(source_row, 2, source_parent)
        source_text = source_index.data(Qt.DisplayRole) or ""
        translated = target_index.data(Qt.DisplayRole) or ""

        return (
            self.search_text in source_text.lower()
            or self.search_text in translated.lower()
        )


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
        self.search_timer.timeout.connect(self.apply_search)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # ---------------------------
        # 🔹 Header Row
        # ---------------------------
        header_layout = QHBoxLayout()

        self.title = QLabel()
        self.title.setObjectName("title")

        self.lang_dropdown = QComboBox()
        self.lang_dropdown.currentIndexChanged.connect(self.change_target_language)

        header_layout.addWidget(self.title)
        header_layout.addStretch()
        self.target_language_label = QLabel()
        header_layout.addWidget(self.target_language_label)
        header_layout.addWidget(self.lang_dropdown)

        layout.addLayout(header_layout)

        # ---------------------------
        # 🔹 Search Row
        # ---------------------------
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.schedule_search)

        self.clear_search_btn = QPushButton()
        self.clear_search_btn.clicked.connect(self.clear_search)

        self.search_label = QLabel()
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(self.clear_search_btn)

        layout.addLayout(search_layout)

        # ---------------------------
        # 🔹 Table (2 columns)
        # ---------------------------
        self.table_model = TranslationTableModel(self.model, self.config)
        self.filter_model = TranslationFilterProxyModel()
        self.filter_model.setSourceModel(self.table_model)

        self.table = QTableView()
        self.table.setModel(self.filter_model)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.doubleClicked.connect(self.handle_double_click)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table, stretch=1)

        # ---------------------------
        # 🔹 Bottom Row
        # ---------------------------
        bottom_layout = QHBoxLayout()

        self.progress_label = QLabel()
        # self.progress_btn.clicked.connect(self.show_progress)

        self.open_btn = QPushButton()
        self.open_btn.clicked.connect(self.open_selected)

        bottom_layout.addWidget(self.progress_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.open_btn)

        layout.addLayout(bottom_layout)

        self.setLayout(layout)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.title.setText(self.config.tr("text_segments"))
        self.target_language_label.setText(self.config.tr("target_language"))
        self.search_label.setText(self.config.tr("search"))
        self.search_input.setPlaceholderText(self.config.tr("search_placeholder"))
        self.clear_search_btn.setText(self.config.tr("clear"))
        self.open_btn.setText(self.config.tr("open_selected"))
        self.table_model.headerDataChanged.emit(Qt.Horizontal, 0, 2)
        self.show_progress()

    # ---------------------------
    # 🔹 Refresh UI
    # ---------------------------
    def refresh(self):
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
            self.populate_table()

    def resize_columns_equally(self):
        viewport = self.table.viewport()
        if viewport is None:
            return

        total_width = viewport.width()
        index_width = min(90, max(60, total_width // 10))
        text_width = (total_width - index_width) // 2

        self.table.setColumnWidth(0, index_width)
        self.table.setColumnWidth(1, text_width)
        self.table.setColumnWidth(2, text_width)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_columns_equally()

    # ---------------------------
    # 🔹 Table Population
    # ---------------------------
    def populate_table(self):
        self.table_model.refresh()
        self.apply_search()
        self.resize_columns_equally()

    # ---------------------------
    # 🔹 Actions
    # ---------------------------
    def schedule_search(self):
        self.search_timer.start()

    def apply_search(self):
        self.filter_model.set_search_text(self.search_input.text())

    def clear_search(self):
        self.search_input.clear()
        self.search_timer.stop()
        self.apply_search()

    def table_row_to_model_row(self, table_row):
        index = self.filter_model.index(table_row, 0)
        if not index.isValid():
            return None
        return index.data(Qt.UserRole)

    def selected_rows(self):
        rows = set()
        selection_model = self.table.selectionModel()

        if selection_model:
            for index in selection_model.selectedRows():
                model_row = self.table_row_to_model_row(index.row())
                if model_row is not None:
                    rows.add(model_row)

        current_index = self.table.currentIndex()
        current_row = current_index.row()

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
        suffix = (
            self.config.tr("item")
            if count == 1
            else self.config.tr("items", count=count)
        )

        menu = QMenu(self)
        clean_action = menu.addAction(
            self.config.tr("clean_translation_items", suffix=suffix)
        )
        translate_action = menu.addAction(
            self.config.tr("auto_translate_items", suffix=suffix)
        )
        clean_translate_action = menu.addAction(
            self.config.tr("clean_and_auto_translate_items", suffix=suffix)
        )

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

    def save_changes(self):
        if not self.model.target_lang:
            QMessageBox.critical(
                self,
                self.config.tr("error"),
                self.config.tr("target_language_not_set"),
            )
            return

        if not self.model.has_unsaved_changes:
            QMessageBox.information(
                self,
                self.config.tr("no_changes"),
                self.config.tr("no_unsaved_changes"),
            )
            return

        self.model.save_target_file(output_dir=self.config.data_dir)
        self.populate_table()
        self.show_progress()
        QMessageBox.information(
            self,
            self.config.tr("success"),
            self.config.tr("translation_saved"),
        )

    def auto_translate_selected(self, clean_first=False):
        rows = self.selected_rows()
        if not rows:
            return

        if not self.model.target_lang:
            QMessageBox.critical(
                self,
                self.config.tr("error"),
                self.config.tr("target_language_not_set"),
            )
            return

        if self.translation_thread and self.translation_thread.isRunning():
            QMessageBox.information(
                self,
                self.config.tr("translation_running"),
                self.config.tr("translation_running_message"),
            )
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
            self.config.tr("translating_selected_items"),
            self.config.tr("cancel"),
            0,
            len(items),
            self,
        )
        self.translation_progress.setWindowModality(Qt.WindowModal)
        self.translation_progress.setMinimumDuration(0)

        self.translation_thread = QThread(self)
        self.translation_worker = TranslationWorker(
            items,
            self.model.src_lang,
            self.model.target_lang,
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
        self.translation_progress.setLabelText(
            self.config.tr("translating_item", idx=idx)
        )
        self.translation_progress.setValue(position - 1)

    def handle_item_translated(self, idx, translated):
        self.model.translations[idx] = translated.strip()
        self.translation_updated += 1

    def handle_translation_error(self, message):
        self.translation_failed = True
        QMessageBox.critical(self, self.config.tr("error"), message)

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
            QMessageBox.information(
                self,
                self.config.tr("translation_stopped"),
                self.config.tr("translation_was_cancelled"),
            )

        self.translation_failed = False

    def open_selected(self):
        current_index = self.table.currentIndex()
        if current_index.isValid():
            model_row = current_index.data(Qt.UserRole)
            if model_row is not None:
                self.open_editor.emit(model_row)

    def handle_double_click(self, index):
        model_row = index.data(Qt.UserRole)
        if model_row is not None:
            self.open_editor.emit(model_row)

    def show_progress(self):
        percent = self.model.completion_percentage()
        total = self.model.total_items()
        done = self.model.translated_count()

        self.progress_label.setText(f"{percent:.1f}% ({done}/{total})")
