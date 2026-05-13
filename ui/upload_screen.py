# ui/upload_screen.py (enhanced)

import os

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QComboBox,
    QCheckBox,
    QListWidget,
    QHBoxLayout,
    QDialog,
)
from PyQt5.QtCore import pyqtSignal
from ui.custom_widget import DividerWidget, ComboInputDialog

from core.parser import parse_raw_text
from core.file_handler import get_base_filename, list_projects, read_abd_metadata
from core.language import detect_language, SUPPORTED_LANGUAGES
from core.config import AppConfig

from models.translation_model import TranslationModel


class UploadScreen(QWidget):
    file_processed = pyqtSignal()

    def __init__(self, model: TranslationModel, config: AppConfig):
        super().__init__()
        self.model = model
        self.config = config
        self.data_dir = config.data_dir
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # -------- Existing Projects --------
        self.resume_label = QLabel()
        self.resume_label.setObjectName("title")
        layout.addWidget(self.resume_label)

        self.project_list = QListWidget()
        self.project_list.itemDoubleClicked.connect(self.open_selected_project)
        layout.addWidget(self.project_list)

        btn_row = QHBoxLayout()

        self.refresh_btn = QPushButton()
        self.refresh_btn.clicked.connect(self.load_projects)

        self.open_btn = QPushButton()
        self.open_btn.clicked.connect(self.open_selected_project)

        btn_row.addWidget(self.refresh_btn)
        btn_row.addWidget(self.open_btn)

        layout.addLayout(btn_row)

        # -------- Divider --------
        # layout.addWidget(
        #     QLabel("──────── OR ────────"), alignment=Qt.AlignmentFlag.AlignCenter
        # )
        self.divider = DividerWidget()
        layout.addWidget(self.divider)

        # -------- New Project --------
        self.new_label = QLabel()
        self.new_label.setObjectName("title")
        layout.addWidget(self.new_label)

        self.upload_btn = QPushButton()
        self.upload_btn.clicked.connect(self.choose_file)
        layout.addWidget(self.upload_btn)

        self.lang_dropdown = QComboBox()
        for code, name in SUPPORTED_LANGUAGES.items():
            self.lang_dropdown.addItem(name, code)
        layout.addWidget(self.lang_dropdown)

        self.auto_detect = QCheckBox()
        self.auto_detect.setChecked(True)
        layout.addWidget(self.auto_detect)

        layout.addStretch()

        self.setLayout(layout)

        self.load_projects()
        self.retranslate_ui()

    def retranslate_ui(self):
        self.resume_label.setText(self.config.tr("resume_existing_project"))
        self.refresh_btn.setText(self.config.tr("refresh"))
        self.open_btn.setText(self.config.tr("open_selected"))
        self.divider.setText(self.config.tr("or"))
        self.new_label.setText(self.config.tr("new_project"))
        self.upload_btn.setText(self.config.tr("choose_file"))
        self.auto_detect.setText(self.config.tr("auto_detect_language"))

    # ---------------------------
    # 🔹 Load Existing Projects
    # ---------------------------
    def load_projects(self):
        self.project_list.clear()

        output_dir = self.data_dir
        if output_dir is None:
            raise ValueError("Data directory is not configured")
        projects = list_projects(output_dir)
        # print(projects)

        for base, files in projects.items():
            self.project_list.addItem(f"{base} ({len(files)} files)")

        self.projects = projects

    # ---------------------------
    # 🔹 Open Existing
    # ---------------------------
    def open_selected_project(self):
        index = self.project_list.currentRow()
        if index < 0:
            return

        base = list(self.projects.keys())[index]
        files = self.projects[base]

        src_file = None
        target_files = []

        # Determine which file is source and which is target based on metadata
        for f in files:
            filepath = os.path.join(self.data_dir, f)
            metadata = read_abd_metadata(filepath)
            tgt_lang = metadata.get("language", "")

            if tgt_lang == "":
                src_file = f
            else:
                target_files.append(f)

        if not src_file:
            return

        src_path = os.path.join(self.data_dir, src_file)

        self.model.load_source_data(src_path)

        if target_files:
            target_langs = [tgt_file.split(".")[-2] for tgt_file in target_files]
            for tgt_lang in target_langs:
                if tgt_lang not in self.model.avl_tgt_langs:
                    self.model.avl_tgt_langs.append(tgt_lang)

            # ask user for target language
            dlg = ComboInputDialog(
                title=self.config.tr("multiple_target_languages"),
                label=self.config.tr("pick_target_language"),
                items=[
                    (SUPPORTED_LANGUAGES[tgt_lang], tgt_lang)
                    for tgt_lang in target_langs
                ],
            )
            if dlg.exec_() == QDialog.Accepted:
                tgt_lang = dlg.selectedData()
                self.model.set_target_lang(
                    tgt_lang, data_dir=self.data_dir
                )

        self.file_processed.emit()

    # ---------------------------
    # 🔹 New File Upload
    # ---------------------------
    def choose_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            self.config.tr("open_file"),
            "",
            self.config.tr("text_files_filter"),
        )
        if not filepath:
            return

        data = parse_raw_text(filepath)
        base_filename = get_base_filename(filepath)

        if self.auto_detect.isChecked():
            src_lang = detect_language(data[0][1])
        else:
            src_lang = self.lang_dropdown.currentData()

        self.model.load_source_text(data, base_filename, src_lang)

        output_dir = self.data_dir
        if output_dir is None:
            raise ValueError("Data directory is not configured")
        self.model.save_source_file(output_dir)

        self.file_processed.emit()
