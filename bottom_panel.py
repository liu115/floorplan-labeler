from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget, QLabel, QLineEdit, QGridLayout, QSpinBox
from PyQt5.QtCore import Qt, pyqtSignal

from utils import draw_debug_box


class BotPanel(QWidget):
    sig_adjust_height = pyqtSignal((int, int))
    sig_adjust_thickness = pyqtSignal((int, int))

    def __init__(self, parent):
        super().__init__(parent)

        self.btn_group = QWidget(self)
        self.btn_group.setGeometry(0, 0, 600, 100)
        layout = QHBoxLayout(self.btn_group)

        # For slice 1
        btn_add_height_1 = QPushButton('+ h1')
        btn_add_height_1.clicked.connect(lambda: self.sig_adjust_height.emit(1, +1))
        btn_mns_height_1 = QPushButton('- h1')
        btn_mns_height_1.clicked.connect(lambda: self.sig_adjust_height.emit(1, -1))
        btn_add_thick_1 = QPushButton('+ t1')
        btn_add_thick_1.clicked.connect(lambda: self.sig_adjust_thickness.emit(1, +1))
        btn_mns_thick_1 = QPushButton('- t1')
        btn_mns_thick_1.clicked.connect(lambda: self.sig_adjust_thickness.emit(1, -1))
        layout.addWidget(btn_add_height_1)
        layout.addWidget(btn_mns_height_1)
        layout.addWidget(btn_add_thick_1)
        layout.addWidget(btn_mns_thick_1)

        # For slice 2
        btn_add_height_2 = QPushButton('+ h2')
        btn_add_height_2.clicked.connect(lambda: self.sig_adjust_height.emit(2, +1))
        btn_mns_height_2 = QPushButton('- h2')
        btn_mns_height_2.clicked.connect(lambda: self.sig_adjust_height.emit(2, -1))
        btn_add_thick_2 = QPushButton('+ t2')
        btn_add_thick_2.clicked.connect(lambda: self.sig_adjust_thickness.emit(2, +1))
        btn_mns_thick_2 = QPushButton('- t2')
        btn_mns_thick_2.clicked.connect(lambda: self.sig_adjust_thickness.emit(2, -1))

        layout.addWidget(btn_add_height_2)
        layout.addWidget(btn_mns_height_2)
        layout.addWidget(btn_add_thick_2)
        layout.addWidget(btn_mns_thick_2)

    
    def paintEvent(self, event):
        draw_debug_box(self, diag=False)

        painter = QPainter(self)
        p = self.parent()
        points = p.points
        x_min, z_min, y_min = points.min(0)
        x_max, z_max, y_max = points.max(0)

        painter.drawText(30, 100, f'z_min: {z_min:.2f}, z_max: {z_max:.2f}')
        painter.drawText(30, 120, f'Band 1 (green) height: {p.height_1:.2f}, thickness: {p.thick_1:.2f}')
        painter.drawText(30, 140, f'Band 2 (red) height: {p.height_2:.2f}, thickness: {p.thick_2:.2f}')
