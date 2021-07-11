import os
import sys
import json
import glob
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QMessageBox
from canvas import Canvas
from bottom_panel import BotPanel
from label_panel import LabelPanel
from utils import read_ply
from utils import uv_to_xy
from utils import get_random_color


class MainWindow(QMainWindow):
    CANVAS_HEIGHT = 750
    CANVAS_WIDTH = 1200
    BOTPANEL_HEIGHT = 180
    BOTPANEL_WIDTH = 600
    LABELPANEL_HEIGHT = 750
    LABELPANEL_WIDTH = 180

    INITIAL_THICKNESS = 0.2
    THINKNESS_ADJUST_SIZE = 0.1
    HEIGHT_ADJUST_SIZE = 0.1
    ROTATE_STEP = np.pi / 72
    DEFAULT_CANVAS_MODE = 'DENSITY'
    DEFAULT_DENSITY_SCALE = 25

    SAME_CORNER_DIST = 1

    def __init__(self, basedir, outdir):
        super().__init__()
        self.setGeometry(0, 0, 1400, 900)
        self.setWindowTitle('Floorplan Labeler')

        self.canvas = Canvas(self)
        self.canvas.setGeometry(0, 0, self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
        self.canvas.sig_label_point[(int, int)].connect(self.add_point)
        self.canvas.sig_undo_label.connect(self.undo_label)

        self.botpanel = BotPanel(self)
        self.botpanel.setGeometry(0, self.CANVAS_HEIGHT+5, self.BOTPANEL_WIDTH, self.BOTPANEL_HEIGHT)
        self.botpanel.sig_set_height_ratio[(int, float)].connect(self.set_height)
        self.density_scale = self.DEFAULT_DENSITY_SCALE
        self.botpanel.sig_set_density_scale[int].connect(self.set_density_scale)
        # self.botpanel.sig_adjust_height[(int, int)].connect(self.adjust_height)
        # self.botpanel.sig_adjust_thickness[(int, int)].connect(self.adjust_thickness)

        self.labelpanel = LabelPanel(self)
        self.labelpanel.setGeometry(self.CANVAS_WIDTH+5, 0, self.LABELPANEL_WIDTH, self.LABELPANEL_HEIGHT)
        self.labelpanel.sig_delete_room[str].connect(self.delete_room)

        self.canvas_mode = self.DEFAULT_CANVAS_MODE
        self.canvas_mode_btn = QPushButton(f'mod: {self.canvas_mode}', self)
        self.canvas_mode_btn.clicked.connect(self.toggle_canvas_mode)
        self.canvas_mode_btn.setGeometry(self.CANVAS_WIDTH + 20, self.CANVAS_HEIGHT, 130, 30)

        self.label_mode = 'room'        # or 'axis'
        self.label_mode_btn = QPushButton(f'mod: {self.label_mode}', self)
        self.label_mode_btn.clicked.connect(self.toggle_label_mode)
        self.label_mode_btn.setGeometry(self.CANVAS_WIDTH + 20, self.CANVAS_HEIGHT + 30, 130, 30)

        self.save_btn = QPushButton('save', self)
        self.save_btn.setGeometry(self.CANVAS_WIDTH + 20, self.CANVAS_HEIGHT + 60, 130, 30)
        self.save_btn.clicked.connect(self.save_result)

        self.reset_btn = QPushButton('reset all', self)
        self.reset_btn.clicked.connect(self.reset_scene)
        self.reset_btn.setGeometry(self.CANVAS_WIDTH + 20, self.CANVAS_HEIGHT + 90, 130, 30)

        self.basedir = basedir
        self.outdir = outdir
        self.files = glob.glob(basedir + '/*.ply')
        self.files.sort()
        assert len(self.files) > 0, f'No ply data found in {basedir}'
        self.file_idx = 0
        self.reset_scene()
        self.show()

    def reset_scene(self):
        # Read file
        file_name = self.files[self.file_idx]
        self.points, self.colors = read_ply(file_name)

        self.is_dirty = False
        self.trans_x = 0
        self.trans_y = 0
        self.zoom = 0
        self.rotate = 0

        x_min, z_min, y_min = self.points.min(0)
        x_max, z_max, y_max = self.points.max(0)
        # Set initial height as one-third
        self.height_1 = z_min + (z_max - z_min) / 3
        self.height_2 = z_min + (z_max - z_min) / 3 * 2
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

        # Read result if the previous saved annotation can be found
        saved_file_name = os.path.basename(file_name).replace('.ply', '.json')
        saved_file_name = os.path.join(self.outdir, saved_file_name)
        if os.path.exists(saved_file_name):
            print(f'{saved_file_name} found. Load the result.')
            self.read_result(saved_file_name)

    def keyPressEvent(self, event):
        key = event.key()
        value_changed = True
        SHIFT_UNIT = 0.3
        if key == Qt.Key_Q:
            self.rotate += self.ROTATE_STEP
        elif key == Qt.Key_E:
            self.rotate -= self.ROTATE_STEP
        elif key == Qt.Key_W:
            self.trans_y += SHIFT_UNIT * self.zoom
        elif key == Qt.Key_S:
            self.trans_y -= SHIFT_UNIT * self.zoom
        elif key == Qt.Key_A:
            self.trans_x -= SHIFT_UNIT * self.zoom
        elif key == Qt.Key_D:
            self.trans_x += SHIFT_UNIT * self.zoom
        elif key == Qt.Key_Escape:
            self.close()
        elif key == Qt.Key_N or key == Qt.Key_P:
            # Next scene
            if self.is_dirty:
                ret = QMessageBox.question(self, 'Warning', 'Chaged not saved. Sure?', QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if ret == QMessageBox.Ok:
                    if key == Qt.Key_N:
                        self.next_scene()
                    else:
                        self.prev_scene()

            else:
                if key == Qt.Key_N:
                    self.next_scene()
                else:
                    self.prev_scene()
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

    def add_room(self, room_corners):
        assert len(room_corners) >= 3
        self.room_corner_list.append(room_corners)
        color = get_random_color()
        self.room_color_list.append(color)
        room_id = f'room {self.room_id_base}'
        self.room_id_base += 1
        self.labelpanel.add_label(room_id, color)
        self.room_id_list.append(room_id)

    def add_point(self, u, v):
        uv = np.array([u, v])
        center = np.mean(self.points[:, [0, 2]], axis=0)
        xy = uv_to_xy(uv, center, self.rotate, self.trans_x, self.trans_y, self.zoom, self.CANVAS_HEIGHT, self.CANVAS_WIDTH)
        self.is_dirty = True
        if self.label_mode == 'room':
            # Add new room label if click previous point and has at least 3 points
            if (len(self.cur_corners) >= 3
                    and np.sum(np.abs(self.cur_corners[0]-xy)) < self.SAME_CORNER_DIST):
                self.add_room(self.cur_corners)
                self.cur_corners = []
            else:
                self.cur_corners.append(xy)
        elif self.label_mode == 'axis':
            self.cur_corners.append(xy)
            if len(self.cur_corners) == 2:
                self.axis_corners = self.cur_corners
                self.cur_corners = []

        self.canvas.update()

    def toggle_label_mode(self):
        if self.label_mode == 'axis':
            self.label_mode = 'room'
        elif self.label_mode == 'room':
            self.label_mode = 'axis'
        # Clear current corners
        self.label_mode_btn.setText(f'mod: {self.label_mode}')
        self.cur_corners = []
        self.canvas.update()

    def toggle_canvas_mode(self):
        if self.canvas_mode == 'DENSITY':
            self.canvas_mode = 'SLICE'
        elif self.canvas_mode == 'SLICE':
            self.canvas_mode = 'DENSITY'
        # Clear current corners
        self.canvas_mode_btn.setText(f'mod: {self.canvas_mode}')
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

    def set_height(self, slice_id, ratio):
        x_min, z_min, y_min = self.points.min(0)
        x_max, z_max, y_max = self.points.max(0)

        if slice_id == 1:
            self.height_1 = z_min + (z_max - z_min) * ratio
        if slice_id == 2:
            self.height_2 = z_min + (z_max - z_min) * ratio
        self.canvas.update()
        self.botpanel.update()

    def set_density_scale(self, scale):
        self.density_scale = scale
        self.canvas.update()
        self.botpanel.update()

    def save_result(self):
        if len(self.axis_corners) == 0:
            # No axis corner labeled
            QMessageBox.about(self, 'Error', 'Missing axis aligned corner. Fail to save.')
            return

        if len(self.room_corner_list) == 0:
            # No axis corner labeled
            QMessageBox.about(self, 'Error', 'No room annotation. Fail to save.')
            return

        file_name = self.files[self.file_idx]
        file_name = os.path.basename(file_name).replace('.ply', '.json')
        file_name = os.path.join(self.outdir, file_name)
        print(f'save at {file_name}')

        def serialize_corners(corners):
            return [(f'{corner[0]:.4f}', f'{corner[1]:.4f}') for corner in corners]

        room_corners = [serialize_corners(corners) for corners in self.room_corner_list]
        axis_corners = serialize_corners(self.axis_corners)

        with open(file_name, 'w') as f:
            json.dump({
                'room_corners': room_corners,
                'axis_corners': axis_corners,
            }, f)
        QMessageBox.about(self, '', f'Saved {file_name}')
        self.is_dirty = False

    def read_result(self, fn):
        with open(fn, 'r') as f:
            d = json.load(f)

        room_list = d['room_corners']
        for room_corners in room_list:
            room_corners = [np.array([float(x[0]), float(x[1])]) for x in room_corners]
            self.add_room(room_corners)

        axis_corners = d['axis_corners']
        axis_corners = [np.array([float(x[0]), float(x[1])]) for x in axis_corners]
        self.axis_corners = axis_corners
        self.canvas.update()

    def prev_scene(self):
        if self.file_idx > 0:
            self.file_idx -= 1
            self.points, self.colors = read_ply(self.files[self.file_idx])
            self.reset_scene()
        else:
            QMessageBox.about(self, '', 'This is the first scene')

    def next_scene(self):
        if self.file_idx < len(self.files) - 1:
            self.file_idx += 1
            self.points, self.colors = read_ply(self.files[self.file_idx])
            self.reset_scene()
        else:
            QMessageBox.about(self, '', 'This is the last scene')


def main():
    print(sys.argv)
    app = QApplication(sys.argv)
    assert len(sys.argv) == 3, "Usage: python app.py [PLY_DIR] [OUTPUT_DIR]"
    w = MainWindow(basedir=sys.argv[1], outdir=sys.argv[2])
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
