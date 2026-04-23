# ui/main_window.py

from PyQt5.QtWidgets import QMainWindow, QStackedWidget

from ui.upload_screen import UploadScreen
from ui.list_screen import ListScreen
from ui.editor_screen import EditorScreen
from core.config import AppConfig


from models.translation_model import TranslationModel


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config

        self.setWindowTitle(config.get("app", "name", "Anuvad"))
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

    # Navigation
    def show_list_screen(self):
        self.list_screen.refresh()
        self.stack.setCurrentWidget(self.list_screen)

    def show_editor_screen(self, index):
        self.model.set_index(index)
        self.editor_screen.load_current()
        self.stack.setCurrentWidget(self.editor_screen)
