import sys
import numpy as np
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPen
# from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QPushButton
from components import Canvas, BotPanel, LabelPanel
from utils import read_ply




class MainWindow(QMainWindow):
    CANVAS_HEIGHT = 300
    CANVAS_WIDTH = 600
    BOTPANEL_HEIGHT = 180
    BOTPANEL_WIDTH = 600
    LABELPANEL_HEIGHT = 300
    LABELPANEL_WIDTH = 180


    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 800, 500)
        self.setWindowTitle('Floorplan Labeler')

        self.canvas = Canvas(self)
        self.canvas.setGeometry(0, 0, self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
        
        self.botpanel = BotPanel(self)
        self.botpanel.setGeometry(0, self.CANVAS_HEIGHT+5, self.BOTPANEL_WIDTH, self.BOTPANEL_HEIGHT)

        self.labelpanel = LabelPanel(self)
        self.labelpanel.setGeometry(self.CANVAS_WIDTH+5, 0, self.LABELPANEL_WIDTH, self.LABELPANEL_HEIGHT)
        self.reset_scene()
        self.show()

    def reset_scene(self):
        self.points, self.colors = read_ply('data/test.ply')
        self.trans_x = 0
        self.trans_y = 0
        self.zoom = 0
        self.rotate = 0

        x_min, _, y_min = self.points.min(0)
        x_max, _, y_max = self.points.max(0)

        h = self.CANVAS_HEIGHT
        w = self.CANVAS_WIDTH
        if h / (y_max - y_min) > w / (x_max - x_min):
            self.zoom = w / (x_max - x_min)
        else:
            self.zoom = h / (y_max - y_min)
        
        self.trans_x = -x_min * self.zoom
        self.trans_y = -y_min * self.zoom

        self.corner_list = []
        self.room_list = []
        self.x_corners = None
    
        self.canvas.repaint()

    def keyPressEvent(self, event):
        key = event.key()
        value_changed = True
        SHIFT_UNIT = 0.3
        if key == Qt.Key_Q:
            self.rotate -= np.pi / 18
        elif key == Qt.Key_E:
            self.rotate += np.pi / 18
        elif key == Qt.Key_W:
            self.trans_y -= SHIFT_UNIT * self.zoom
        elif key == Qt.Key_S:
            self.trans_y += SHIFT_UNIT * self.zoom
        elif key == Qt.Key_A:
            self.trans_x -= SHIFT_UNIT * self.zoom
        elif key == Qt.Key_D:
            self.trans_x += SHIFT_UNIT * self.zoom
        elif key == Qt.Key_Escape:
            self.close()
        else:
            value_changed = False
        
        if value_changed:
            self.canvas.repaint()

    def wheelEvent(self, event):
        d = event.angleDelta()
        if d.y() < 0:
            self.zoom *= 0.9
        elif d.y() > 0:
            self.zoom *= (1 / 0.9)
        self.canvas.repaint()
        

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())


if __name__== '__main__':
    main()