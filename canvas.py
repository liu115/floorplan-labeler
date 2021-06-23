from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QSpinBox
from PyQt5.QtWidgets import QListView
from PyQt5.QtGui import QPolygon, QStandardItem, QPolygonF
from PyQt5.QtGui import QBrush, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QPoint, QPointF
import numpy as np
from utils import draw_debug_box, xy_to_uv, uv_to_xy


def paint_point_style(painter, color):
    pen = QPen(color, 3, Qt.SolidLine)
    painter.setPen(pen)

def paint_corner_style(painter, color):
    pen = QPen(color, 10, Qt.SolidLine)
    painter.setPen(pen)

def paint_edge_style(painter, color):
    pen = QPen(color, 3, Qt.DotLine)
    painter.setPen(pen)

def paint_room_style(painter, color):
    pen = QPen(color, 3, Qt.DotLine)
    color = QColor(color)
    color.setAlpha(100)
    brush = QBrush(color)
    painter.setPen(pen)
    painter.setBrush(brush)

def convert_qpointf(xy):
    points = []
    for i in range(xy.shape[0]):
        points.append(QPointF(xy[i, 0], xy[i, 1]))
    return points


class Canvas(QFrame):
    sig_label_point = pyqtSignal((int, int))
    sig_undo_label = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

    def paintEvent(self, event):
        # draw_debug_box(self, diag=False)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        p = self.parent()
        
        points = p.points
        xy = points[:, [0, 2]]
        z = points[:, 1]
        center = np.mean(xy, axis=0)
        uv = xy_to_uv(xy, center, p.rotate, p.trans_x, p.trans_y, p.zoom)

        # Draw layer 1
        paint_point_style(painter, QColor(0, 255, 0, 127))
        mask_1 = (z > p.height_1 - p.thick_1) & (z <= p.height_1 + p.thick_1)
        uv_1 = uv[mask_1, :]
        painter.drawPoints(QPolygonF(convert_qpointf(uv_1)))

        # Draw layer 2
        paint_point_style(painter, QColor(255, 0, 0, 127))
        mask_2 = (z > p.height_2 - p.thick_2) & (z <= p.height_2 + p.thick_2)
        uv_2 = uv[mask_2, :]
        painter.drawPoints(QPolygonF(convert_qpointf(uv_2)))

        # Draw current labeling corners
        if len(p.cur_corners) > 0:
            xy_corners = np.stack(p.cur_corners)
            uv_corners = xy_to_uv(xy_corners, center, p.rotate, p.trans_x, p.trans_y, p.zoom)

            for i in range(uv_corners.shape[0]):
                paint_corner_style(painter, QColor(0, 0, 255, 255))
                point = QPointF(uv_corners[i, 0], uv_corners[i, 1])
                painter.drawPoint(point)
                if i > 0:
                    prev_point = QPointF(uv_corners[i-1, 0], uv_corners[i-1, 1])
                    paint_edge_style(painter, QColor(0, 0, 255, 255))
                    painter.drawLine(point, prev_point)

        # Draw rooms
        for i, room_corners in enumerate(p.room_corner_list):
            color = p.room_color_list[i]
            paint_room_style(painter, color)
            xy_corners = np.stack(room_corners)
            uv_corners = xy_to_uv(xy_corners, center, p.rotate, p.trans_x, p.trans_y, p.zoom)
            painter.drawPolygon(QPolygonF(convert_qpointf(uv_corners)))
            paint_corner_style(painter, color)
            painter.drawPoints(QPolygonF(convert_qpointf(uv_corners)))

        # Dras axis 
        if len(p.axis_corners) == 2:
            axis_corners = np.stack(p.axis_corners)
            uv_corners = xy_to_uv(axis_corners, center, p.rotate, p.trans_x, p.trans_y, p.zoom)
            paint_corner_style(painter, QColor(0, 255, 255, 255))
            point1 = QPointF(uv_corners[0, 0], uv_corners[0, 1])
            painter.drawPoint(point1)
            point2 = QPointF(uv_corners[1, 0], uv_corners[1, 1])
            painter.drawPoint(point2)
            paint_edge_style(painter, QColor(0, 255, 255, 255))
            painter.drawLine(point1, point2)

    def clear(self):
        painter = QPainter(self)
        brush = QBrush(Qt.white)
        painter.setBrush(brush)
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        painter.drawRect(0, 0, width, height)

    def mousePressEvent(self, event):
        if not self.hasFocus():
            self.setFocus()
        
        x, y = event.x(), event.y()
        # if not self.is_labeling:
        #     self.is_labeling = True
        if event.button() == Qt.LeftButton:
            self.sig_label_point.emit(x, y)
        elif event.button() == Qt.RightButton:
            self.sig_undo_label.emit()
            
