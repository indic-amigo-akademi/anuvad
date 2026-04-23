# main.py

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from ui.main_window import MainWindow
from core.config import AppConfig


def main():
    config = AppConfig()
    app = QApplication(sys.argv)
    font = QFont(config.font_family, config.font_size)

    themes_map = {
        "light": {
            "background_color": "#fefefe",
            "text_color": "#333",
            "button": {
                "background_color": "#acacac",
                "border_color": "#ccc"
            }
        },
        "dark": {
            "background_color": "#333",
            "text_color": "#fefefe",
            "button": {
                "background_color": "#5a5a5a",
                "border_color": "#777"
            }
        }
    }

    theme = config.get("ui", "theme", "light")
    if theme not in themes_map:
        theme = "light"

    # Set global styles
    app.setStyleSheet(f"""
    QWidget {{
        font-family: 'Segoe UI', 'Nirmala UI', sans-serif;
        font-size: 14px;
        background-color: {themes_map[theme]["background_color"]};
        color: {themes_map[theme]["text_color"]};
    }}

    QLabel#title {{
        font-size: 20px;
        font-weight: bold;
    }}

    QPushButton {{
        padding: 6px 12px;
        border-radius: 6px;
        border: 1px solid {themes_map[theme]["button"]["border_color"]};
        background-color: {themes_map[theme]["button"]["background_color"]};
        color: {themes_map[theme]["text_color"]};
    }}

    QListWidget {{
        padding: 6px;
    }}

    QTextEdit {{
        padding: 8px;
        font-size: 14px;
    }}
    """)
    app.setFont(font)
    
    window = MainWindow(config=config)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()