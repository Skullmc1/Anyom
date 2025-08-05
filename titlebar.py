from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QPoint

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(42)
        self.setStyleSheet("""
            QWidget {
                background-color: #F4F4F7;
                border-bottom: 1px solid #CCC;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
            QLabel {
                color: #333;
                font-size: 15px;
                font-family: 'Plus Jakarta Sans';
                padding-left: 12px;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
                color: #5865F2;
                width: 36px;
                height: 36px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #E0E4FF;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(4)

        self.title = QLabel("Anyom")
        layout.addWidget(self.title)

        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.min_btn = QPushButton("–")
        self.min_btn.clicked.connect(self.minimize)
        layout.addWidget(self.min_btn)

        self.max_btn = QPushButton("□")
        self.max_btn.clicked.connect(self.maximize_restore)
        layout.addWidget(self.max_btn)

        self.close_btn = QPushButton("×")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        self.drag_pos = None
        self.maximized = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            self.parent.move(self.parent.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def minimize(self):
        self.parent.showMinimized()

    def maximize_restore(self):
        if self.maximized:
            self.parent.showNormal()
            self.maximized = False
        else:
            self.parent.showMaximized()
            self.maximized = True

    def close(self):
        self.parent.close()
