# main.py

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from ui.main_window import MainWindow
from core.config import AppConfig
from PyQt5.QtGui import QIcon
import ctypes
import os

def on_exit(config: AppConfig):
    if os.name == "nt":
        ctypes.windll.user32.ExitProcess(0)
    config.save()


def main():
    config = AppConfig()
    logo_path = config.get("app", "logo_path", "icon.ico")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(logo_path))
    # Set global styles
    app.setStyleSheet(config.get_theme_stylesheet())
    
    window = MainWindow(config=config)
    window.show()

    sys.exit(app.exec_())
    
    # Handling app exit 
    on_exit(config)


if __name__ == "__main__":
    if os.name == "nt":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("iaa.anuvad.app")
    
    main()