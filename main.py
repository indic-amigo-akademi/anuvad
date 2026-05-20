# main.py

import logging
from datetime import datetime
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import ctypes
import os
from ui.main_window import MainWindow
from core.config import AppConfig
from core.file_handler import resource_path, user_data_path


def on_exit(config: AppConfig):
    if os.name == "nt":
        ctypes.windll.user32.ExitProcess(0)
    config.save()


def main():
    logo_path = config.get("paths", "logo_path", "icon.ico")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path(logo_path)))
    # Set global styles
    app.setStyleSheet(config.get_theme_stylesheet())

    window = MainWindow(config=config)
    window.show()

    sys.exit(app.exec_())

    # Handling app exit
    on_exit(config)


if __name__ == "__main__":
    config = AppConfig()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=user_data_path(
            os.path.join(
                config.logs_dir,
                f"anuvad_{datetime.now().strftime('%Y-%m-%d')}.log",
            )
        ),
    )

    try:
        if os.name == "nt":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "iaa.anuvad.app"
            )

        main()
    except Exception as e:
        logging.exception("An unhandled exception occurred: %s", str(e))
        raise
