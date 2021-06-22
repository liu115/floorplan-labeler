import random
import numpy as np
from plyfile import PlyData
from PyQt5.QtGui import QPainter, QColor, QPen

def extend_array_to_homogeneous(array):
    """
    Returns the homogeneous form of a vector by attaching
    a unit vector as additional dimensions
    Parameters
    ----------
    array of (3, n) or (2, n)
    Returns (4, n) or (3, n)
    -------
    """
    try:
        assert array.shape[0] in (2, 3, 4)
        dim, samples = array.shape
        return np.vstack((array, np.ones((1, samples))))

    except:
        assert array.shape[1] in (2, 3, 4)
        array = array.T
        dim, samples = array.shape
        return np.vstack((array, np.ones((1, samples)))).T



def draw_debug_box(qtobj, diag=True):
    painter = QPainter(qtobj)
    width = qtobj.frameGeometry().width()
    height = qtobj.frameGeometry().height()
    pen = QPen()
    pen.setWidth(3)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.HighQualityAntialiasing)
    painter.setPen(pen)
    painter.drawRect(0+2, 0+2, width-3, height-3)
    if diag:
        painter.drawLine(0+2, 0+2, width-3, height-3)
        painter.drawLine(width-3, 0+2, 0+2, height-3)


def read_ply(fn):
    plydata = PlyData.read(fn)
    v = np.array([list(x) for x in plydata.elements[0]])
    points = np.ascontiguousarray(v[:, :3])
    colors = np.ascontiguousarray(v[:, 3:6])
    return points, colors


def rotate_xy(xy, theta):
    m = np.array([
        [np.cos(theta), np.sin(theta)],
        [-np.sin(theta), np.cos(theta)]
    ])
    return np.dot(xy, m)


def xy_to_uv(xy, center, rotate, trans_x, trans_y, zoom):
    '''
        xy: point cloud coordinate (N x 2)
    '''
    xy = rotate_xy(xy - center, rotate) + center
    uv = xy * zoom + np.array([trans_x, trans_y])
    return uv


def uv_to_xy(uv, center, rotate, trans_x, trans_y, zoom):
    '''
        uv: coordinate on canvas (N x 2)
    '''
    xy = (uv - np.array([trans_x, trans_y])) / zoom
    xy = rotate_xy(xy - center, -rotate) + center
    return xy


def get_random_color():
    # color = list(np.random.choice(range(256), size=3))
    # return color
    return QColor("#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]))