import json
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import measure     # Require measure for visualization


def read_json_label(fn):
    with open(fn, 'r') as f:
        d = json.load(f)
        room_list = d['room_corners']
        
        room_corners = []
        for corners in room_list:
            points = np.array([[float(x[0]), float(x[1])] for x in corners])
            room_corners.append(points)
        axis_corners = d['axis_corners']
        axis_corners = np.array([[float(x[0]), float(x[1])] for x in axis_corners])
    return room_corners, axis_corners

def norm(x):
    return np.sqrt(x[0] * x[0] + x[1] * x[1])


def visualize(label_fn, axis_align=False, grid_size=256):
    room_corners, axis_corners = read_json_label(label_fn)
    if axis_align:
        x, y = axis_corners[1, :] - axis_corners[0, :]
        yaw_angle = np.arctan(y / x)
        yaw_2d = np.array([
            np.cos(yaw_angle), -np.sin(yaw_angle),
            np.sin(yaw_angle),
            np.cos(yaw_angle)
        ]).reshape(2, 2)
        for i in range(len(room_corners)):
            room_corners[i] = np.dot(room_corners[i], yaw_2d)
    
    all_corners = np.concatenate(room_corners, axis=0)
    max_edge = np.max(all_corners.max(0)- all_corners.min(0))
    scale = grid_size / max_edge * 0.8
    trans = -all_corners.min(0)
    pad = grid_size * 0.1

    image = np.zeros((grid_size, grid_size), np.uint8)
    for room_idx, corners in enumerate(room_corners):
        corners = (corners + trans) * scale + pad
        for i in range(corners.shape[0]):
            j = (i+1) % corners.shape[0]
            x1, y1 = round(corners[i, 0]), round(corners[i, 1])
            x2, y2 = round(corners[j, 0]), round(corners[j, 1])
            cv2.line(image, (x1, y1), (x2, y2), color=1, thickness=3)
    image = measure.label(1 - image)
    plt.imshow(image)
    plt.savefig('test.png')

if __name__ == '__main__':
    # visualize('/home/ycliu/research/MP3D-VO-partial/data/2t7WUuJeko7_1.json', axis_align=True)
    visualize('/home/ycliu/research/MP3D-VO-partial/data/i5noydFURQK_1.json', axis_align=True)