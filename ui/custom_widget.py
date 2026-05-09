from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QFrame,
    QLabel,
    QDialog,
    QVBoxLayout,
    QComboBox,
    QDialogButtonBox,
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
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("padding: 0 8px;")
        label.setFixedWidth(len(text) * 18)
        h.addWidget(left)
        h.addWidget(label)
        h.addWidget(right)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)


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
