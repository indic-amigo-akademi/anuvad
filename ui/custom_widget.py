from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame, QLabel
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
