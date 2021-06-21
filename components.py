from PyQt5.QtWidgets import QFrame, QWidget
from PyQt5.QtGui import QBrush, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, pyqtSignal
import numpy as np
from utils import draw_debug_box, rotate_xy


class Canvas(QFrame):

    def __init__(self, parent):
        super().__init__(parent)
        # rect = self.contentsRect()
        # print(rect)

    def paintEvent(self, event):
        draw_debug_box(self, diag=False)
        painter = QPainter(self)
        # # print(self.parent)
        p = self.parent()
        
        points = p.points
        xy = points[:, [0, 2]]
        xy_mean = np.mean(xy, axis=0)
        xy = rotate_xy(xy - xy_mean, p.rotate) + xy_mean
        xy = xy * p.zoom + np.array([p.trans_x, p.trans_y])
        # print(xy)
        for i in range(xy.shape[0]):
            x = int(xy[i, 0])
            y = int(xy[i, 1])
        #     print(x, y)
            painter.drawPoint(x, y)
        print(p.zoom)

    def clear(self):
        painter = QPainter(self)
        brush = QBrush(Qt.white)
        painter.setBrush(brush)
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        painter.drawRect(0, 0, width, height)

    def mousePressEvent(self, event):
        # TODO: Click -> start labeling
        print(event.x(), event.y())


class LabelPanel(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

    
    def paintEvent(self, event):
        draw_debug_box(self, diag=False)


class BotPanel(QFrame):

    def __init__(self, parent):
        super().__init__(parent)

    
    def paintEvent(self, event):
        draw_debug_box(self, diag=False)

    def mousePressEvent(self, event):
        print(event.x(), event.y())