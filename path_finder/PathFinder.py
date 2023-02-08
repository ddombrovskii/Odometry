import platform
from ctypes import CDLL, Structure, c_int, c_float, POINTER, Array
from typing import Any, List
from cv2 import bitwise_not
import numpy as np
from PIL import Image, ImageOps, ImageDraw
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
import matplotlib
matplotlib.use('Qt5Agg')


a_star_lib = None
if platform.system() == 'Linux':
    a_star_lib = CDLL('./path_finder/lib_astar.so')
elif platform.system() == 'Windows':
    if platform.architecture()[0] == '64bit':
        a_star_lib = CDLL('./path_finder/x64/AStar.dll')
    else:
        a_star_lib = CDLL('./path_finder/x86/AStar.dll')

class Pt2(Structure):
    _fields_ = ("row", c_int), ("col", c_int)

class Pt3(Structure):
    _fields_ = ("row", c_int), ("col", c_int), ("layer", c_int)


class Path2(Structure):
    _fields_ = ("cost", c_float), ("n_points", c_int), ("path_points", POINTER(Pt2))


class Path3(Structure):
    _fields_ = ("cost", c_float), ("n_points", c_int), ("path_points", POINTER(Pt3))


class Map2(Structure):
    _fields_ = ("cols", c_int), ("rows", c_int), ("weights", POINTER(c_float))


class Map3(Structure):
    _fields_ = ("cols", c_int), ("rows", c_int), ("layers", c_int), ("weights", POINTER(c_float))


class PathFinder:
    def __init__(self):
        self.test_lib = a_star_lib.test_lib

        # 2D functions
        self._path_2_new = a_star_lib.path_2_new
        self._path_2_new.argtypes = [c_int]
        self._path_2_new.restype = POINTER(Path2)

        self._path_2_del = a_star_lib.path_2_del
        self._path_2_del.argtypes = [POINTER(Path2)]

        self._find_path_2 = a_star_lib.find_path_2
        self._find_path_2.argtypes = [POINTER(Map2), POINTER(Pt2), POINTER(Pt2)]
        self._find_path_2.restype = POINTER(Path2)

        self._print_map2 = a_star_lib.print_map2
        self._print_map2.argtypes = [POINTER(Map2)]


        # 3D functions
        self._path_3_new = a_star_lib.path_3_new
        self._path_3_new.argtypes = [c_int]
        self._path_3_new.restype = POINTER(Path3)

        self._path_3_del = a_star_lib.path_3_del
        self._path_3_del.argtypes = [POINTER(Path3)]

        self._find_path_3 = a_star_lib.find_path_3
        self._find_path_3.argtypes = [POINTER(Map3), POINTER(Pt3), POINTER(Pt3)]
        self._find_path_3.restype = POINTER(Path3)

        self._fig = None
        self._ax = None
        self._start_point = None
        self._end_point = None
        self._path_p = None
        self._map = None
        self._image_arr = None


    def __get_weights_from_image(self, img_path: str, img_type: str = 'binary',  scale: float = 0.25) -> [Array[Any], int, int, List]:
        if img_type.lower() not in ['binary', 'non_binary']:
            assert ValueError("image type might be one of this: 'binary' or 'non_biary'")

        try:
            img = ImageOps.grayscale(Image.open(img_path))
            resized_image = img.resize((int(img.size[0]*scale), int(img.size[1]*scale)))
            img_arr = np.asarray(resized_image)
            img_arr = bitwise_not(img_arr)
            py_weights = []
            for row in img_arr:
                 py_weights += list(row)
            py_weights = np.array(py_weights, dtype=int)

            if img_type == 'binary':
                py_weights %= 2
                py_weights *= 999
            py_weights += 1

            c_weights = (c_float * len(py_weights))(*py_weights)
            return c_weights, img_arr.shape[0], img_arr.shape[1], img_arr
        except Exception as ex:
            print(ex)
            exit(-1)


    def find_path_on_image(self, img_path: str, scale: float = 0.25):
        c_weights, rows, cols, self._image_arr = self.__get_weights_from_image(img_path, img_type='non_binary', scale=scale)
        self._map = Map2(c_int(cols), c_int(rows), c_weights)

        self._fig, self._ax = plt.subplots()
        self._ax.imshow(self._image_arr)

        def onclick(event):
            if not event.dblclick:
                x, y = int(event.xdata), int(event.ydata)
                if self._start_point is None:
                    self._start_point = Pt2(y, x)
                    self._end_point = None
                    self._path_p = None
                    self._ax.plot(x, y, marker='o', markersize=3, color='red', label='start')
                    self._fig.canvas.draw()
                    print(f"Start point: {y}, {x}")
                else:
                    self._end_point = Pt2(y, x)
                    self._ax.plot(x, y, marker='o', markersize=3, color='green', label='end')
                    self._fig.canvas.draw()
                    print(f"End point: {y}, {x}")

                if self._start_point is not None and self._end_point is not None:
                    self._path_p = self._find_path_2(self._map, self._start_point, self._end_point)

                if self._path_p is not None:
                    self. _start_point = None
                    cost = self._path_p.contents.cost
                    n_points = self._path_p.contents.n_points
                    print(f"{cost=}")
                    print(f"{n_points=}\n")
                    path_data_x = []
                    path_data_y = []
                    if n_points > 0:
                        for i in range(n_points):
                            path_data_x.append(self._path_p.contents.path_points[i].col)
                            path_data_y.append(self._path_p.contents.path_points[i].row)
                        self._ax.plot(path_data_x, path_data_y, color='blue', linewidth=1)
                        self._ax.plot(path_data_x[0], path_data_y[0], marker='o', markersize=3, color='red', label='start')
                        self._ax.plot(path_data_x[n_points - 1], path_data_y[n_points - 1], marker='o', markersize=3, color='green', label='end')
                        self._fig.canvas.draw()
                    else:
                        print("Path not found\n")
            else:
                plt.cla()
                self._ax.imshow(self._image_arr)
                self._fig.canvas.draw()
                self._start_point = None

        cid = self._fig.canvas.mpl_connect('button_press_event', onclick)
        self._fig.suptitle('One click - select point\nDouble click - clear figure')
        plt.show()