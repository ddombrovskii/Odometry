from collections import namedtuple
from typing import Tuple
import numpy as np
import platform
import json
import os


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
        def print_(vectors: np.ndarray):
            return ',\n\t\t'.join(f"{{ \"x\": {v[0]:20}, \"y\": {v[1]:20}, \"z\": {v[2]:20}}}" for v in vectors)
        return "{\n\t\"camera_matrix\": \n\t{\n" \
               f"\t\t\"m00\": {self.camera_matrix[0][0]:20}, \"m01\": {self.camera_matrix[0][1]:20}, \"m02\": {self.camera_matrix[0][2]:20},\n"\
               f"\t\t\"m10\": {self.camera_matrix[1][0]:20}, \"m11\": {self.camera_matrix[1][1]:20}, \"m12\": {self.camera_matrix[1][2]:20},\n"\
               f"\t\t\"m20\": {self.camera_matrix[2][0]:20}, \"m21\": {self.camera_matrix[2][1]:20}, \"m22\": {self.camera_matrix[2][2]:20}\n\t}},\n" \
               f"\t\"distortion\": \n\t[\n\t\t{', '.join(f'{value:20}' for value in self.distortion_coefficients.flat)}\n\t],\n" \
               f"\t\"translation_vectors\": \n\t[\n\t\t{(print_(self.translation_vectors))}\n\t],\n" \
               f"\t\"rotation_vectors\": \n\t[\n\t\t{(print_(self.rotation_vectors))}\n\t]\n}}"


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


# if __name__ == "__main__":
#     info = load_camera_calib_info("calibration_results_new.json")
#     print(info)
#     # with open("calibration_results_new.json", "wt") as output:
#     #     print(info, file=output)

