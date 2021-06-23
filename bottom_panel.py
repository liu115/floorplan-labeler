from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout, QSpinBox
from PyQt5.QtCore import Qt, pyqtSignal

from utils import draw_debug_box


class BotPanel(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        grid = QGridLayout()
        grid.setSpacing(10)

    
    def paintEvent(self, event):
        draw_debug_box(self, diag=False)