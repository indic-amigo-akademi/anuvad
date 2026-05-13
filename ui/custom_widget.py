from PyQt5.QtWidgets import (
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
)
from PyQt5.QtCore import Qt


class DividerWidget(QWidget):
    def __init__(self, text="OR", parent=None):
        super().__init__(parent)
        self.setObjectName("divider")
        h = QHBoxLayout(self)
        left = QFrame()
        left.setObjectName("line")
        left.setFrameShape(QFrame.HLine)
        left.setFrameShadow(QFrame.Sunken)
        right = QFrame()
        right.setObjectName("line")
        right.setFrameShape(QFrame.HLine)
        right.setFrameShadow(QFrame.Sunken)
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
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
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
        name: str,
        author: str,
        title: str,
        name_label: str,
        author_label: str,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        self.name_edit = QLineEdit(name)
        self.author_edit = QLineEdit(author)
        form.addRow(f"{name_label}:", self.name_edit)
        form.addRow(f"{author_label}:", self.author_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def project_name(self):
        return self.name_edit.text().strip()

    @property
    def project_author(self):
        return self.author_edit.text().strip()
