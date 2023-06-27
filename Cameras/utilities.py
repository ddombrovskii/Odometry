from collections import namedtuple
import matplotlib.pyplot as plt
from typing import Tuple
import numpy as np
import cv2 as cv
import platform
import json
import os


def create_fourcc(fourcc: str) -> int:
    if len(fourcc) < 4:
        return 0
    return ord(fourcc[0]) | (ord(fourcc[1]) << 8) | (ord(fourcc[2]) << 16) | (ord(fourcc[3]) << 24)


def get_screen_resolution() -> Tuple[int, int]:
    if platform.system() == 'Linux':
        screen = os.popen("xrandr -q -d :0").readlines()[0]
        return int(screen.split()[7]), int(screen.split()[9][:-1])
    if platform.system() == 'Windows':
        cmd = 'wmic desktopmonitor get screenheight, screenwidth'
        h, w = tuple(map(int, os.popen(cmd).read().split()[-2::]))
        return w, h
    return 0, 0


class CameraCalibrationInfo(namedtuple('CameraCalibrationInfo', 'camera_matrix, distortion_coefficients, translation_vectors, rotation_vectors')):
    __slots__ = ()

    def __new__(cls, cm: np.ndarray, dc: np.ndarray, tv: np.ndarray, rv: np.ndarray):
        if cm.shape != (3, 3):
            raise ValueError("CameraCalibrationInfo: camera_matrix.size != (3,3)")
        tv = np.array([[vi for vi in v.flat] for v in tv])
        rv = np.array([[vi for vi in v.flat] for v in rv])
        return super().__new__(cls, cm, dc, tv, rv)

    def __str__(self):
        _fmt = '>20.5f'

        def print_(vectors: np.ndarray):
            return ',\n\t\t'.join(f"{{ \"x\": {v[0]:{_fmt}}, \"y\": {v[1]:{_fmt}}, \"z\": {v[2]:{_fmt}}}}" for v in vectors)
        return "{\n\t\"camera_matrix\": \n\t{\n" \
               f"\t\t\"m00\": {self.camera_matrix[0][0]:{_fmt}}, \"m01\": {self.camera_matrix[0][1]:{_fmt}}, \"m02\": {self.camera_matrix[0][2]:{_fmt}},\n"\
               f"\t\t\"m10\": {self.camera_matrix[1][0]:{_fmt}}, \"m11\": {self.camera_matrix[1][1]:{_fmt}}, \"m12\": {self.camera_matrix[1][2]:{_fmt}},\n"\
               f"\t\t\"m20\": {self.camera_matrix[2][0]:{_fmt}}, \"m21\": {self.camera_matrix[2][1]:{_fmt}}, \"m22\": {self.camera_matrix[2][2]:{_fmt}}\n\t}},\n" \
               f"\t\"distortion\": \n\t[\n\t\t{', '.join(f'{value:{_fmt}}' for value in self.distortion_coefficients.flat)}\n\t],\n" \
               f"\t\"translation_vectors\": \n\t[\n\t\t{(print_(self.translation_vectors))}\n\t],\n" \
               f"\t\"rotation_vectors\": \n\t[\n\t\t{(print_(self.rotation_vectors))}\n\t]\n}}"


class CameraCalibrationArgs(namedtuple('CameraCalibrationArgs',
                                       'criteria, obj_points, image_points, '
                                       'ches_board_size, obj_points_array, recalibrate')):
    __slots__ = ()

    def __new__(cls, criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001),
                ches_board_size=(6, 6), recalibrate=False):
        _obj_p: np.ndarray = np.zeros((ches_board_size[0] * ches_board_size[1], 3), dtype=np.float32)
        _obj_p[:, :2] = np.mgrid[0:ches_board_size[0], 0:ches_board_size[1]].T.reshape(-1, 2)
        return super().__new__(cls, criteria, [], [], ches_board_size, _obj_p, recalibrate)

    def __str__(self):
        sep  = ','
        return f"{{" \
               f"\"criteria\":       [{sep.join(f'{v:>5}' for v in self.criteria)}],\n" \
               f"\"ches_board_size\":[{self.ches_board_size[0]:>5.3f}, {self.ches_board_size[1]:>5}],\n" \
               f"\"recalibrate\":     {'true' if self.recalibrate else 'false'}\n" \
               f"}}"


def load_camera_calib_info(file_path: str) -> CameraCalibrationInfo:
    """
    :param file_path:
    :return:
    """
    if not os.path.exists(file_path):
        return None
    json_file = None
    cm = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    dc = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    tv = []
    rv = []
    with open(file_path, "rt") as input_file:
        json_file = json.load(input_file)
        if json_file is None:
            return None
        if "camera_matrix" in json_file:
            node = json_file["camera_matrix"]
            for i in range(9):
                row, col = divmod(i, 3)
                try:
                    cm[row][col] = float(node[f"m{row}{col}"])
                except RuntimeWarning as _ex:
                    val = node[f"m{row}{col}"]
                    print(f"camera_matrix read error: m{row}{col} = {val}]")

        if "translation_vectors" in json_file:
            nodes = json_file["translation_vectors"]
            for node in nodes:
                try:
                    tv.append([float(node["x"]), float(node["y"]), float(node["z"])])
                except RuntimeWarning as _ex:
                    print(f"translation_vectors read error: {node['x']}, {node['y']}, {node['z']}]")

        if "rotation_vectors" in json_file:
            nodes = json_file["rotation_vectors"]
            for node in nodes:
                try:
                    rv.append([float(node["x"]), float(node["y"]), float(node["z"])])
                except RuntimeWarning as _ex:
                    print(f"rotation_vectors read error: {node['x']}, {node['y']}, {node['z']}]")

        if "distortion" in json_file:
            node = json_file["distortion"]
            for index, val in enumerate(node):
                try:
                    dc[index] = float(val)
                except RuntimeWarning as _ex:
                    print(f"distortion read error at index: {index}, with val: {val}]")
    return CameraCalibrationInfo(cm, dc, np.array(tv), np.array(rv))


def show_slam_results(file_path: str):
    transforms = []
    with open(file_path, 'rt') as input_file:
        json_file = json.load(input_file)
        if json_file is None:
            return None
        if "way_points_transforms" not in json_file:
            return
        nodes = json_file["way_points_transforms"]
        for node in nodes:
            cm = np.zeros((3, 4), dtype=np.float32)
            for i in range(12):
                row, col = divmod(i, 4)
                try:
                    cm[row][col] = float(node[f"m{row}{col}"])
                except RuntimeWarning as _ex:
                    val = node[f"m{row}{col}"]
                    print(f"slam transform matrix read error: m{row}{col} = {val}]")
            transforms.append(cm)

    x = [t[0][3] for t in transforms]
    y = [t[1][3] for t in transforms]
    z = [t[2][3] for t in transforms]

    ex = [t[:][0] for t in transforms]
    ey = [t[:][1] for t in transforms]
    ez = [t[:][2] for t in transforms]

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    ax.plot(x, y, z, 'k')
    for i in range(min(128, len(x))):
        p = (x[i], y[i], z[i])
        print(p)
        ax.plot([x[i], x[i] + ex[i][0]],
                [y[i], y[i] + ex[i][1]],
                [z[i], z[i] + ex[i][2]], 'r')
        ax.plot([x[i], x[i] + ey[i][0]],
                [y[i], y[i] + ey[i][1]],
                [z[i], z[i] + ey[i][2]], 'g')
        ax.plot([x[i], x[i] + ez[i][0]],
                [y[i], y[i] + ez[i][1]],
                [z[i], z[i] + ez[i][2]], 'b')
    plt.show()


if __name__ == "__main__":
    show_slam_results("optical_odometry 17; 50; 14.json")
    # with open("calibration_results_new.json", "wt") as output:
    #     print(info, file=output)

