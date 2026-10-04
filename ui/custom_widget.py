from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QFrame,
    QLabel,
    QDialog,
    QVBoxLayout,
    QComboBox,
    QDialogButtonBox,
    QLineEdit,
    QFormLayout,
    QPlainTextEdit,
    QPushButton,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication

class DividerWidget(QWidget):
    def __init__(self, text="OR", parent=None):
        super().__init__(parent)
        self.setObjectName("divider")
        h = QHBoxLayout(self)
        left = QFrame()
        left.setObjectName("line")
        left.setFrameShape(QFrame.Shape.HLine)
        left.setFrameShadow(QFrame.Shadow.Sunken)
        right = QFrame()
        right.setObjectName("line")
        right.setFrameShape(QFrame.Shape.HLine)
        right.setFrameShadow(QFrame.Shadow.Sunken)
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("padding: 0 8px;")
        self.label.setFixedWidth(max(40, len(text) * 18))
        h.addWidget(left)
        h.addWidget(self.label)
        h.addWidget(right)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

    def setText(self, text):
        self.label.setText(text)
        self.label.setFixedWidth(max(40, len(text) * 18))


class ComboInputDialog(QDialog):
    def __init__(self, title="Choose item", label="Select:", items=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        items = items or []
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(label))
        self.combo = QComboBox(self)
        for text, data in items:
            self.combo.addItem(text, data)
        self.combo.setEditable(False)  # make non-editable; set True to allow typing
        layout.addWidget(self.combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setMinimumWidth(300)

    def selectedData(self):
        return self.combo.currentData()

    def selectedText(self):
        return self.combo.currentText()


class MetadataEditDialog(QDialog):
    def __init__(
        self,
        dialog_title: str,
        title: str,
        name: str,
        author: str,
        title_label: str,
        name_label: str,
        author_label: str,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(dialog_title)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        self.title_edit = QLineEdit(title)
        self.name_edit = QLineEdit(name)
        self.author_edit = QLineEdit(author)
        form.addRow(f"{title_label}:", self.title_edit)
        form.addRow(f"{name_label}:", self.name_edit)
        form.addRow(f"{author_label}:", self.author_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def project_title(self):
        return self.title_edit.text().strip()

    @property
    def project_name(self):
        return self.name_edit.text().strip()

    @property
    def project_author(self):
        return self.author_edit.text().strip()


class ResultDialog(QDialog):
    def __init__(self, result_text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Result")
        self.resize(500, 300)

        self.text_box = QPlainTextEdit(self)
        self.text_box.setPlainText(result_text)
        self.text_box.setReadOnly(True)

        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self.copy_text)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self.copy_button)
        buttons.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_box)
        layout.addLayout(buttons)

    def copy_text(self):
        clipboard = QGuiApplication.clipboard()
        if clipboard is None:
            return
        clipboard.setText(self.text_box.toPlainText())
        self.copy_button.setText("Copied!")
        # Restore the button label after a moment
        QTimer.singleShot(1200, lambda: self.copy_button.setText("Copy"))
