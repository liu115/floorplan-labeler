from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel, QSlider
from PyQt5.QtCore import Qt, pyqtSignal


class BotPanel(QWidget):
    sig_set_height_ratio = pyqtSignal((int, float))
    sig_set_density_scale = pyqtSignal(int)
    # sig_adjust_height = pyqtSignal((int, int))
    # sig_adjust_thickness = pyqtSignal((int, int))

    def __init__(self, parent):
        super().__init__(parent)

        self.label_group = QWidget(self)
        self.label_group.setGeometry(0, 0, 600, 50)
        self.height_sld_group = QWidget(self)
        self.height_sld_group.setGeometry(0, 0, 600, 100)

        self.density_label = QLabel('density scale:', self)
        self.density_label.move(10, 150)
        self.density_sld = QSlider(Qt.Horizontal, self)
        self.density_sld.move(120, 150)
        self.density_sld.valueChanged.connect(lambda x: self.sig_set_density_scale.emit(x))

        layout1 = QHBoxLayout(self.label_group)
        self.label_z_min = QLabel('z_min', self)
        self.label_height_1 = QLabel('2', self)
        self.label_height_1.setStyleSheet('color: green')
        self.label_height_2 = QLabel('3', self)
        self.label_height_2.setStyleSheet('color: red')
        self.label_z_max = QLabel('z_max:', self)
        layout1.addWidget(self.label_z_min)
        layout1.addWidget(self.label_height_1)
        layout1.addWidget(self.label_height_2)
        layout1.addWidget(self.label_z_max)

        layout2 = QHBoxLayout(self.height_sld_group)
        self.sld1 = QSlider(Qt.Horizontal, self)
        self.sld1.valueChanged.connect(lambda x: self.change_height(1, x))
        self.sld2 = QSlider(Qt.Horizontal, self)
        self.sld2.valueChanged.connect(lambda x: self.change_height(2, x))
        layout2.addWidget(self.sld1)
        layout2.addWidget(self.sld2)

    def change_height(self, h, x):
        self.sig_set_height_ratio.emit(h, x / 100.0)

    def update(self):
        super().update()
        p = self.parent()
        points = p.points
        x_min, z_min, y_min = points.min(0)
        x_max, z_max, y_max = points.max(0)

        self.label_z_min.setText(f'z_min:{z_min:.2f}')
        self.label_z_max.setText(f'z_max:{z_max:.2f}')
        self.label_height_1.setText(f'{p.height_1:.2f}')
        self.label_height_2.setText(f'{p.height_2:.2f}')

        self.sld1.setValue((p.height_1 - z_min) / (z_max - z_min) * 100)
        self.sld2.setValue((p.height_2 - z_min) / (z_max - z_min) * 100)

        self.density_sld.setValue(p.density_scale)
