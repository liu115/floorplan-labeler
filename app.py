import sys
import numpy as np
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
from canvas import Canvas
from bottom_panel import BotPanel
from label_panel import LabelPanel
from utils import read_ply
from utils import xy_to_uv, uv_to_xy
from utils import get_random_color


class MainWindow(QMainWindow):
    CANVAS_HEIGHT = 300
    CANVAS_WIDTH = 600
    BOTPANEL_HEIGHT = 180
    BOTPANEL_WIDTH = 600
    LABELPANEL_HEIGHT = 300
    LABELPANEL_WIDTH = 180

    INITIAL_THICKNESS = 0.1
    THINKNESS_ADJUST_SIZE = 0.1
    HEIGHT_ADJUST_SIZE = 0.1

    SAME_CORNER_DIST = 1

    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 800, 500)
        self.setWindowTitle('Floorplan Labeler')

        self.canvas = Canvas(self)
        self.canvas.setGeometry(0, 0, self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
        self.canvas.sig_label_point[(int, int)].connect(self.add_point)
        self.canvas.sig_undo_label.connect(self.undo_label)
        
        self.botpanel = BotPanel(self)
        self.botpanel.setGeometry(0, self.CANVAS_HEIGHT+5, self.BOTPANEL_WIDTH, self.BOTPANEL_HEIGHT)
        self.botpanel.sig_adjust_height[(int, int)].connect(self.adjust_height)
        self.botpanel.sig_adjust_thickness[(int, int)].connect(self.adjust_thickness)

        self.labelpanel = LabelPanel(self)
        self.labelpanel.setGeometry(self.CANVAS_WIDTH+5, 0, self.LABELPANEL_WIDTH, self.LABELPANEL_HEIGHT)
        self.labelpanel.sig_delete_room[str].connect(self.delete_room)
        
        self.save_btn = QPushButton('save', self)
        self.save_btn.move(650, 400)
        self.save_btn.clicked.connect(self.save_result)

        self.label_mode = 'room'        # or 'axis'
        self.mode_btn = QPushButton(f'{self.label_mode}', self)
        self.mode_btn.clicked.connect(self.switch_label_mode)
        self.mode_btn.move(650, 360)

        self.reset_btn = QPushButton('reset all', self)
        self.reset_btn.clicked.connect(self.reset_scene)
        self.reset_btn.move(650, 440)
        
        self.points, self.colors = read_ply('data/test.ply')
        self.reset_scene()
        self.show()
        self.setFocus()

    def reset_scene(self):
        self.trans_x = 0
        self.trans_y = 0
        self.zoom = 0
        self.rotate = 0

        x_min, z_min, y_min = self.points.min(0)
        x_max, z_max, y_max = self.points.max(0)
        # Set initial height as one-third
        self.height_1 = (z_max + z_min) / 3
        self.height_2 = (z_max + z_min) / 3 * 2
        self.thick_1 = self.INITIAL_THICKNESS
        self.thick_2 = self.INITIAL_THICKNESS

        h = self.CANVAS_HEIGHT
        w = self.CANVAS_WIDTH
        if h / (y_max - y_min) > w / (x_max - x_min):
            self.zoom = w / (x_max - x_min)
        else:
            self.zoom = h / (y_max - y_min)
        
        self.trans_x = -x_min * self.zoom
        self.trans_y = -y_min * self.zoom

        self.cur_corners = []
        self.room_id_base = 0
        self.room_corner_list = []
        self.room_color_list = []
        self.room_id_list = []
        self.axis_corners = []
    
        self.labelpanel.clear()
        self.canvas.update()
        self.botpanel.update()

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
        elif key == Qt.Key_Enter:
            self.setFocus()
            # TODO: Setup height
        else:
            value_changed = False
        
        if value_changed:
            self.canvas.update()
            self.labelpanel.update()

    def wheelEvent(self, event):
        d = event.angleDelta()
        if d.y() < 0:
            self.zoom *= 0.9
        elif d.y() > 0:
            self.zoom *= (1 / 0.9)
        self.canvas.update()
    
    def add_point(self, u, v):
        uv = np.array([u, v])
        center = np.mean(self.points[:, [0, 2]], axis=0)
        xy = uv_to_xy(uv, center, self.rotate, self.trans_x, self.trans_y, self.zoom)

        if self.label_mode == 'room':
            # Add new room label if click previous point and has at least 3 points
            if (len(self.cur_corners) >= 3
                and np.sum(np.abs(self.cur_corners[0]-xy)) < self.SAME_CORNER_DIST):
                self.room_corner_list.append(self.cur_corners)

                color = get_random_color()
                self.room_color_list.append(color)
                room_id = f'room {self.room_id_base}'
                self.room_id_base += 1
                self.labelpanel.add_label(room_id, color)
                self.room_id_list.append(room_id)
                self.cur_corners = []
            else:
                self.cur_corners.append(xy)
        elif self.label_mode == 'axis':
            self.cur_corners.append(xy)
            if len(self.cur_corners) == 2:
                self.axis_corners = self.cur_corners
                self.cur_corners = []

        self.canvas.update()

    def switch_label_mode(self):
        if self.label_mode == 'axis':
            self.label_mode = 'room'
        elif self.label_mode == 'room':
            self.label_mode = 'axis'
        # Clear current corners
        self.mode_btn.setText(f'{self.label_mode}')
        self.cur_corners = []
        self.canvas.update()

    def undo_label(self):
        if len(self.cur_corners) > 0:
            self.cur_corners.pop()
            self.canvas.update()

    def delete_room(self, room_id):
        idx = self.room_id_list.index(room_id)
        print(room_id, idx)
        self.room_id_list.pop(idx)
        self.room_color_list.pop(idx)
        self.room_corner_list.pop(idx)
        self.canvas.update()

    def adjust_height(self, slice_id, direction):
        if slice_id == 1:
            self.height_1 += direction * self.HEIGHT_ADJUST_SIZE
        elif slice_id == 2:
            self.height_2 += direction * self.HEIGHT_ADJUST_SIZE
        self.canvas.update()
        self.botpanel.update()
    
    def adjust_thickness(self, slice_id, direction):
        if slice_id == 1:
            self.thick_1 += direction * self.THINKNESS_ADJUST_SIZE
        elif slice_id == 2:
            self.thick_2 += direction * self.THINKNESS_ADJUST_SIZE
        self.canvas.update()
        self.botpanel.update()

    def save_result(self):
        # TODO
        print('save all')

    
    def read_result(self):
        # TODO
        pass

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())


if __name__== '__main__':
    main()