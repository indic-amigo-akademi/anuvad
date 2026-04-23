# ui/upload_screen.py (enhanced)

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
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

from core.parser import parse_raw_text, parse_structured_file
from core.file_handler import get_base_filename, save_structured_file, list_projects
from core.language import detect_language, SUPPORTED_LANGUAGES
from core.config import AppConfig
from core.file_handler import read_abd_file

from models.translation_model import TranslationModel


class UploadScreen(QWidget):
    file_processed = pyqtSignal()

    def __init__(self, model: TranslationModel, config: AppConfig):
        super().__init__()
        self.model = model
        self.config = config
        self.data_dir = config.data_dir

        sectionTitleFont = QFont(
            config.font_family, config.get_int("ui", "font_size_md", 14), QFont.Bold
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Title
        self.title = QLabel(config.get("app", "title", "Anuvad"))
        self.title.setObjectName("title")
        layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        # -------- Existing Projects --------
        resumeLabel = QLabel("Resume Existing Project")
        resumeLabel.setFont(sectionTitleFont)
        layout.addWidget(resumeLabel)

        self.project_list = QListWidget()
        self.project_list.itemDoubleClicked.connect(self.open_selected_project)
        layout.addWidget(self.project_list)

        btn_row = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_projects)

        self.open_btn = QPushButton("Open Selected")
        self.open_btn.clicked.connect(self.open_selected_project)

        btn_row.addWidget(self.refresh_btn)
        btn_row.addWidget(self.open_btn)

        layout.addLayout(btn_row)

        # -------- Divider --------
        layout.addWidget(
            QLabel("──────── OR ────────"), alignment=Qt.AlignmentFlag.AlignCenter
        )

        # -------- New Project --------
        newLabel = QLabel("New Project")
        newLabel.setFont(sectionTitleFont)
        layout.addWidget(newLabel)

        self.upload_btn = QPushButton("Choose File")
        self.upload_btn.clicked.connect(self.choose_file)
        layout.addWidget(self.upload_btn)

        self.lang_dropdown = QComboBox()
        for code, name in SUPPORTED_LANGUAGES.items():
            self.lang_dropdown.addItem(name, code)
        layout.addWidget(self.lang_dropdown)

        self.auto_detect = QCheckBox("Auto Detect Language")
        self.auto_detect.setChecked(True)
        layout.addWidget(self.auto_detect)

        layout.addStretch()

        self.setLayout(layout)

        self.load_projects()

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
        target_file = None

        # Determine which file is source and which is target based on metadata
        for f in files:
            filepath = f"{self.data_dir}/{f}"
            metadata, _ = read_abd_file(filepath)
            tgt_lang = metadata.get("language", "")
            src_lang = metadata.get("source_language", "en")

            if tgt_lang == "":
                src_file = f
            else:
                target_file = f

        if not src_file:
            return

        src_path = f"{self.data_dir}/{src_file}"

        self.model.load_source_data(src_path)

        if target_file:
            tgt_path = f"{self.data_dir}/{target_file}"
            self.model.load_target_data(tgt_path)

        self.file_processed.emit()

    # ---------------------------
    # 🔹 New File Upload
    # ---------------------------
    def choose_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Text Files (*.txt)"
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
