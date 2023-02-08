import platform
from ctypes import CDLL, Structure, c_int, c_float, POINTER, Array
from typing import Any
from PIL import Image, ImageDraw
import cv2
import numpy as np
from matplotlib import pyplot as plt


a_star_lib = None
if platform.system() == 'Linux':
    a_star_lib = CDLL('./lib_astar.so')
elif platform.system() == 'Windows':
    if platform.architecture()[0] == '64bit':
        a_star_lib = CDLL('./x64/AStar.dll')
    else:
        a_star_lib = CDLL('./x86/AStar.dll')

class Pt(Structure):
    _fields_ = ("row", c_int), ("col", c_int)


class Path(Structure):
    _fields_ = ("cost", c_float), ("n_points", c_int), ("path_points", POINTER(Pt))


class Map(Structure):
    _fields_ = ("cols", c_int), ("rows", c_int), ("weights", POINTER(c_float))

find_path_func = a_star_lib.find_path
find_path_func.argtypes = [POINTER(Map), POINTER(Pt), POINTER(Pt)]
find_path_func.restype = POINTER(Path)

path_del_func = a_star_lib.path_del
path_del_func.argtypes = [POINTER(Path)]


class PathFinder:
    def __init__(self):
        self._find_path_func = a_star_lib.find_path
        self._find_path_func.argtypes = [POINTER(Map), POINTER(Pt), POINTER(Pt)]
        self._find_path_func.restype = POINTER(Path)

        self._path_del_func = a_star_lib.path_del
        self._path_del_func.argtypes = [POINTER(Path)]


def print_path_data(path_p: Path):
    print(f"cost: {path_p.contents.cost}")
    print(f"n_points: {path_p.contents.n_points}")
    for i in range(path_p.contents.n_points):
        print(f"({path_p.contents.path_points[i].row}, {path_p.contents.path_points[i].col})")


def test_path_finder_on_binary_map():
    _F = 1.0
    _X = 1000.0
    py_weights = [_F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F,
                  _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F,
                  _F, _X, _F, _X, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _F, _F, _X, _F, _X, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _F,
                  _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F,
                  _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F,
                  _F, _F, _F, _X, _F, _X, _X, _X, _X, _X, _X, _F, _F, _X, _F, _F, _F, _F, _F, _X, _F, _X, _X, _X, _X, _X, _X, _F, _F, _X, _F, _F,
                  _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F,
                  _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F,
                  _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F,
                  _F, _X, _F, _X, _X, _X, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _X, _X, _X, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F,
                  _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F,
                  _F, _X, _F, _F, _F, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F,
                  _F, _X, _X, _X, _X, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F, _F, _X, _X, _X, _X, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F,
                  _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F,
                  _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F,
                  _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F,
                  _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F,
                  _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F,
                  _F, _X, _F, _X, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _F, _F, _X, _F, _X, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _F,
                  _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F,
                  _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _X, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F,
                  _F, _F, _F, _X, _F, _X, _X, _X, _X, _X, _X, _F, _F, _X, _F, _F, _F, _F, _F, _X, _F, _X, _X, _X, _X, _X, _X, _F, _F, _X, _F, _F,
                  _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F,
                  _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F,
                  _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _X, _F, _F,
                  _F, _X, _F, _X, _X, _X, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _X, _X, _X, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F,
                  _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F,
                  _F, _X, _F, _F, _F, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F, _F, _X, _F, _F, _F, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F,
                  _F, _X, _X, _X, _X, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F, _F, _X, _X, _X, _X, _F, _F, _X, _X, _F, _X, _F, _X, _F, _F, _F,
                  _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F,
                  _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F,
                  _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _X, _F, _F, _F
                  ]

    c_weights = (c_float * len(py_weights))(*py_weights)
    rows, cols = c_int(32), c_int(32)

    new_map = Map(rows, cols, c_weights)
    start_pt = Pt(0, 0)
    end_pt = Pt(31, 31)

    path_p = a_star_lib.find_path(new_map, start_pt, end_pt)
    print_path_data(path_p)
    path_del_func(path_p)


def test_path_finder_on_non_binary_map():
    _F = 1.0
    _X = 1000.0
    _B = 500.0

    weights_7x30 = [
        _F, _F, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X,
        _F, _F,
        _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _B, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F,
        _F, _F,
        _X, _F, _X, _X, _F, _F, _F, _F, _F, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F,
        _F, _X,
        _X, _B, _X, _X, _F, _F, _F, _F, _F, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F,
        _F, _X,
        _X, _F, _F, _F, _F, _X, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F,
        _F, _X,
        _X, _F, _F, _F, _F, _X, _X, _F, _F, _F, _F, _F, _F, _X, _X, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F, _F,
        _F, _F,
        _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X, _X,
        _F, _F
    ]
    cols = 30
    rows = 7
    c_weights = (c_float * len(weights_7x30))(*weights_7x30)

    tests = [
        (Pt(0, 0), Pt(4, 1)),
        (Pt(0, 0), Pt(1, 14)),
        (Pt(0, 0), Pt(0, 29)),
        (Pt(0, 0), Pt(6, 29))
    ]

    mew_map = Map(c_int(cols), c_int(rows), c_weights)
    for points in tests:
        start_point = points[0]
        end_point = points[1]

        print(f"start point: ({start_point.row}, {start_point.col})")
        print(f"end point: ({end_point.row}, {end_point.col})")

        path_p = find_path_func(mew_map, start_point, end_point)
        print_path_data(path_p)
        path_del_func(path_p)
