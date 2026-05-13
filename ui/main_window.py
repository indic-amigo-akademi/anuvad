# ui/main_window.py

from PyQt5.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QAction,
    QActionGroup,
    QMessageBox,
    QMenuBar,
)

from ui.upload_screen import UploadScreen
from ui.list_screen import ListScreen
from ui.editor_screen import EditorScreen
from ui.custom_widget import MetadataEditDialog
from core.config import AppConfig
from core.i18n import APP_LANGUAGES
from models.translation_model import TranslationModel


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config

        self.setWindowTitle(config.appname)
        self.resize(900, 600)

        # Model (shared state)
        self.model = TranslationModel(config=config)

        # Screens
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.upload_screen = UploadScreen(self.model, config=config)
        self.list_screen = ListScreen(self.model, config=config)
        self.editor_screen = EditorScreen(self.model, config=config)

        self.stack.addWidget(self.upload_screen)
        self.stack.addWidget(self.list_screen)
        self.stack.addWidget(self.editor_screen)

        # Connections
        self.upload_screen.file_processed.connect(self.show_list_screen)
        self.list_screen.open_editor.connect(self.show_editor_screen)
        self.editor_screen.back_to_list.connect(self.show_list_screen)
        self.create_menu()

    # Navigation
    def show_list_screen(self):
        self.list_screen.refresh()
        self.stack.setCurrentWidget(self.list_screen)

    def show_editor_screen(self, index):
        self.model.set_index(index)
        self.editor_screen.load_current()
        self.stack.setCurrentWidget(self.editor_screen)

    def create_menu(self):
        menubar: QMenuBar = self.menuBar()
        if not menubar:
            return
        menubar.clear()

        # ---------------------------
        # 📁 File Menu
        # ---------------------------
        file_menu = menubar.addMenu(self.config.tr("file"))
        if not file_menu:
            return

        new_action = QAction(self.config.tr("new_project"), file_menu)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.go_to_upload)

        open_action = QAction(self.config.tr("open_project"), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.go_to_upload)

        save_action = QAction(self.config.tr("save"), self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_current)

        metadata_action = QAction(self.config.tr("edit_metadata"), self)
        metadata_action.triggered.connect(self.edit_metadata)

        exit_action = QAction(self.config.tr("exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(metadata_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # ---------------------------
        # ⚙️ Settings Menu
        # ---------------------------
        settings_menu = menubar.addMenu(self.config.tr("settings"))
        if not settings_menu:
            return

        light_theme_action = QAction(self.config.tr("light_theme"), self)
        light_theme_action.triggered.connect(self.set_light_theme)

        dark_theme_action = QAction(self.config.tr("dark_theme"), self)
        dark_theme_action.triggered.connect(self.set_dark_theme)

        settings_menu.addAction(light_theme_action)
        settings_menu.addAction(dark_theme_action)
        settings_menu.addSeparator()

        language_menu = settings_menu.addMenu(self.config.tr("app_language"))
        language_group = QActionGroup(self)
        language_group.setExclusive(True)
        for code, label in APP_LANGUAGES.items():
            language_action = QAction(label, self)
            language_action.setCheckable(True)
            language_action.setChecked(code == self.config.ui_language)
            language_action.triggered.connect(
                lambda checked=False, language=code: self.set_app_language(language)
            )
            language_group.addAction(language_action)
            language_menu.addAction(language_action)

        # ---------------------------
        # ❓ Help Menu
        # ---------------------------
        help_menu = menubar.addMenu(self.config.tr("help"))
        if not help_menu:
            return

        about_action = QAction(self.config.tr("about"), self)
        about_action.triggered.connect(self.show_about)

        help_menu.addAction(about_action)

    def go_to_upload(self):
        self.stack.setCurrentWidget(self.upload_screen)

    def save_current(self):
        current_widget = self.stack.currentWidget()

        if current_widget == self.editor_screen:
            self.editor_screen.save_changes()
        elif current_widget == self.list_screen:
            self.list_screen.save_changes()
        else:
            QMessageBox.information(
                self,
                self.config.tr("save"),
                self.config.tr("save_before_project"),
            )

    def set_light_theme(self):
        self.config.set("ui", "theme", "light")
        self.setStyleSheet(self.config.get_theme_stylesheet())

    def set_dark_theme(self):
        self.config.set("ui", "theme", "dark")
        self.setStyleSheet(self.config.get_theme_stylesheet())

    def set_app_language(self, language):
        if language == self.config.ui_language:
            return
        self.config.set("ui", "language", language)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.create_menu()
        self.upload_screen.retranslate_ui()
        self.list_screen.retranslate_ui()
        self.editor_screen.retranslate_ui()

    def edit_metadata(self):
        if not self.model.base_filename:
            QMessageBox.information(
                self,
                self.config.tr("no_project"),
                self.config.tr("no_project_open"),
            )
            return

        dlg = MetadataEditDialog(
            name=self.model.base_filename,
            author=self.model.author,
            title=self.config.tr("edit_metadata"),
            name_label=self.config.tr("project_name"),
            author_label=self.config.tr("project_author"),
            parent=self,
        )
        if dlg.exec_():
            new_name = dlg.project_name
            new_author = dlg.project_author
            if new_name and new_author:
                self.model.update_metadata(new_name, new_author, self.config.data_dir)
                QMessageBox.information(
                    self,
                    self.config.tr("success"),
                    self.config.tr("metadata_updated"),
                )

    def show_about(self):
        QMessageBox.information(
            self,
            self.config.tr("about_title", appname=self.config.appname),
            self.config.tr(
                "about_body",
                appname=self.config.appname,
                version=self.config.appversion,
                author=self.config.appauthor,
            ),
        )
