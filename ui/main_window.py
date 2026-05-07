# ui/main_window.py

from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QAction, QMessageBox, QMenuBar

from ui.upload_screen import UploadScreen
from ui.list_screen import ListScreen
from ui.editor_screen import EditorScreen
from core.config import AppConfig
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

        # ---------------------------
        # 📁 File Menu
        # ---------------------------
        file_menu = menubar.addMenu("File")
        if not file_menu:
            return

        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.go_to_upload)

        open_action = QAction("Open Project", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.go_to_upload)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_current)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # ---------------------------
        # ⚙️ Settings Menu
        # ---------------------------
        settings_menu = menubar.addMenu("Settings")
        if not settings_menu:
            return

        light_theme_action = QAction("Light Theme", self)
        light_theme_action.triggered.connect(self.set_light_theme)

        dark_theme_action = QAction("Dark Theme", self)
        dark_theme_action.triggered.connect(self.set_dark_theme)

        settings_menu.addAction(light_theme_action)
        settings_menu.addAction(dark_theme_action)

        # ---------------------------
        # ❓ Help Menu
        # ---------------------------
        help_menu = menubar.addMenu("Help")
        if not help_menu:
            return

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)

        help_menu.addAction(about_action)

    def go_to_upload(self):
        self.stack.setCurrentWidget(self.upload_screen)

    def save_current(self):
        # trigger save in editor if active
        if self.stack.currentWidget() == self.editor_screen:
            self.editor_screen.save_translation()

    def set_light_theme(self):
        self.config.set("ui", "theme", "light")
        self.setStyleSheet(self.config.get_theme_stylesheet())

    def set_dark_theme(self):
        self.config.set("ui", "theme", "dark")
        self.setStyleSheet(self.config.get_theme_stylesheet())

    def show_about(self):
        QMessageBox.information(
            self,
            f"About {self.config.appname}",
            f"""{self.config.appname}
            
A structured desktop translation workbench.

Version: {self.config.appversion}
Author: {self.config.appauthor}
            """,
        )
