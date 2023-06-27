from ctypes import CDLL, Structure, c_int, c_float, POINTER
from PIL import Image, ImageOps, ImageFilter
from Utilities.Geometry import Vector2
from matplotlib import pyplot as plt
from typing import List
import numpy as np
import platform

a_star_lib: CDLL | None = None

_map_2_new = None
_map_2_del = None
_map_3_new = None
_map_3_del = None
# 2D functions
_path_2_new = None
_path_2_del = None
_find_path_2 = None
# 3D functions
_path_3_new = None
_path_3_del = None
_find_path_3 = None


def _load_library():
    global a_star_lib
    if isinstance(a_star_lib, CDLL):
        return True
    try:
        if platform.system() == 'Linux':
            a_star_lib = CDLL('./PathFinder/lib_astar.so')
            return True

        elif platform.system() == 'Windows':
            if platform.architecture()[0] == '64bit':
                # a_star_lib = CDLL('./PathFinder/x64/AStar.dll')
                a_star_lib = CDLL(r'./PathFinder/x64/AStar.dll')
                return True
            else:
                a_star_lib = CDLL('./PathFinder/x86/AStar.dll')
                return True
        return False

    except FileNotFoundError as _:
        print("unable to find AStar.dll...")
        return False


def _load_library_functions():
    global a_star_lib

    if not isinstance(a_star_lib, CDLL):
        return

    global _map_2_new
    global _map_2_del
    global _map_3_new
    global _map_3_del
    # 2D functions
    global _path_2_new
    global _path_2_del
    global _find_path_2
    # 3D functions
    global _path_3_new
    global _path_3_del
    global _find_path_3

    _map_2_new = a_star_lib.map_2_new
    _map_2_new.argtypes = [c_int, c_int, NP_ARRAY_2_D_POINTER]
    _map_2_new.restype = POINTER(_Map2)

    _map_2_del = a_star_lib.map_2_del
    _map_2_del.argtypes = [POINTER(_Map2)]

    _map_3_new = a_star_lib.map_3_new
    _map_3_new.argtypes = [c_int, c_int, c_int, NP_ARRAY_3_D_POINTER]
    _map_3_new.restype = POINTER(_Map3)

    _map_3_del = a_star_lib.map_3_del
    _map_3_del.argtypes = [POINTER(_Map3)]

    # 2D functions
    _path_2_new = a_star_lib.path_2_new
    _path_2_new.argtypes = [c_int]
    _path_2_new.restype = POINTER(_Path2)

    _path_2_del = a_star_lib.path_2_del
    _path_2_del.argtypes = [POINTER(_Path2)]

    _find_path_2 = a_star_lib.find_path_2
    _find_path_2.argtypes = [POINTER(_Map2), POINTER(_Pt2), POINTER(_Pt2), c_int]
    _find_path_2.restype = POINTER(_Path2)

    # 3D functions
    _path_3_new = a_star_lib.path_3_new
    _path_3_new.argtypes = [c_int]
    _path_3_new.restype = POINTER(_Path3)

    _path_3_del = a_star_lib.path_3_del
    _path_3_del.argtypes = [POINTER(_Path3)]

    _find_path_3 = a_star_lib.find_path_3
    _find_path_3.argtypes = [POINTER(_Map3), POINTER(_Pt3), POINTER(_Pt3), c_int]
    _find_path_3.restype = POINTER(_Path3)


def load_library() -> bool:
    global a_star_lib

    if isinstance(a_star_lib, CDLL):
        return True
    if not _load_library():
        return False

    _load_library_functions()
    return True


class _Pt2(Structure):
    _fields_ = ("row", c_int), ("col", c_int)


class _Pt3(Structure):
    _fields_ = ("row", c_int), ("col", c_int), ("layer", c_int)


class _Path2(Structure):
    _fields_ = ("cost", c_float), ("n_points", c_int), ("path_points", POINTER(_Pt2))


class _Path3(Structure):
    _fields_ = ("cost", c_float), ("n_points", c_int), ("path_points", POINTER(_Pt3))


NP_ARRAY_2_D_POINTER = np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags="aligned, contiguous")

NP_ARRAY_3_D_POINTER = np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags="aligned, contiguous")


class _Map2(Structure):
    _fields_ = ("cols", c_int), ("rows", c_int), ("weights", NP_ARRAY_2_D_POINTER)


class _Map3(Structure):
    _fields_ = ("cols", c_int), ("rows", c_int), ("layers", c_int), ("weights", NP_ARRAY_3_D_POINTER)


class Map2:
    def __init__(self, array: np.ndarray):
        self.__array = None
        self.__array_np = None
        if array.ndim != 2:
            raise RuntimeError()
        self.__array_np = array
        self.__array = _map_2_new(array.shape[0], array.shape[1], array)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __del__(self):
        if self.__array is None:
            return
        _map_2_del(self.__array)

    @property
    def rows(self) -> int:
        return self.__array.contents.rows

    @property
    def cols(self) -> int:
        return self.__array.contents.cols

    @property
    def weights(self):
        return self.__array.contents.weights

    @property
    def ptr(self) -> _Map2:
        return self.__array


class Map3:
    def __init__(self, array: np.ndarray):
        self.__array = None
        if array.ndim != 3:
            raise RuntimeError()
        self.__array = _map_3_new(array.shape[0], array.shape[1], array.shape[2], array)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __del__(self):
        if self.__array is None:
            return
        _map_3_del(self.__array)

    @property
    def rows(self) -> int:
        return self.__array.contents.rows

    @property
    def cols(self) -> int:
        return self.__array.contents.cols

    @property
    def layers(self) -> int:
        return self.__array.contents.layers

    @property
    def weights(self):
        return self.__array.contents.weights

    @property
    def ptr(self) -> _Map3:
        return self.__array


class RunningAverage:
    def __init__(self, bucket_size: int = 8):
        self._values     = []
        self._values_sum = 0.0
        self._capacity   = min(max(bucket_size, 2), 128)

    def reset(self):
        self._values     = []
        self._values_sum = 0.0

    @property
    def window_size(self) -> int:
        return self._capacity

    @window_size.setter
    def window_size(self, value: int) -> None:
        assert isinstance(value, int)
        self._capacity = min(max(value, 2), 128)

    def __call__(self, x) -> float:
        return self.update(x)

    def update(self, x) -> float:
        self._values.append(x)
        self._values_sum += x
        if len(self._values) == self._capacity:
            self._values_sum -= self._values[0]
            del self._values[0]
        return self._values_sum / len(self._values)


class PathFinder:
    def __init__(self, path_to_map: str = None, invert: bool = True, scale_ratio: float = 1.0,
                 size: Vector2 = None, origin: Vector2 = None):
        if not load_library():
            raise RuntimeError("AStart DLL not found...")
        self._physical_size: Vector2 = Vector2(1, 1) if size is None else size
        self._physical_origin: Vector2 = Vector2(0, 0) if origin is None else origin
        self._map = None
        self.load_map_image(path_to_map, invert, scale_ratio)

    def load_map_image(self, path_to_map: str, invert: bool = True, scale_ratio: float = 0.250) -> bool:
        try:
            scale_ratio = max(scale_ratio, 0.1)
            img = ImageOps.grayscale(Image.open(path_to_map))
            img_resized = img.resize((int(img.size[0] * scale_ratio), int(img.size[1] * scale_ratio)))
            img_arr = 1.0 + np.asarray(img_resized, dtype=np.float32) / 255.0 * 99.

            if invert:
                img_arr = 100.0 - img_arr

            self._map = Map2(img_arr)
            return True
        except IOError as error:
            print(error.args)
            return False

    def search_path(self, p1: Vector2, p2: Vector2) -> List[Vector2]:
        _start_point = _Pt2(self._map.rows - int((p1.x - self._physical_origin.x + self._physical_size.x * 0.5) /
                                                 self._physical_size.x * (self._map.rows - 1)),
                            self._map.cols - int((p1.y - self._physical_origin.y + self._physical_size.y * 0.5) /
                                                 self._physical_size.y * (self._map.cols - 1)))

        _end_point = _Pt2(self._map.rows - int((p2.x - self._physical_origin.x + self._physical_size.x * 0.5) /
                                               self._physical_size.x * (self._map.rows - 1)),
                          self._map.cols - int((p2.y - self._physical_origin.y + self._physical_size.y * 0.5) /
                                               self._physical_size.y * (self._map.cols - 1)))

        print(f"start : row {str(_start_point.row):>5} | col {str(_start_point.col): >5}")
        print(f" end  : row {str(_end_point.row):>5} | col {str(_end_point.col): >5}")

        _path_p = _find_path_2(self._map.ptr, _start_point, _end_point, 5)
        if _path_p.contents.n_points == 0:
            print("empty path...")
            return []
        path_points = []
        x_smooth = RunningAverage(16)
        y_smooth = RunningAverage(16)
        for i in range(_path_p.contents.n_points):
            p = _path_p.contents.path_points[i]
            x = x_smooth(-p.row / (self._map.rows - 1) + 0.5)
            y = y_smooth(-p.col / (self._map.cols - 1) + 0.5)
            # if i % 4 != 0:
            #     if i != _path_p.contents.n_points - 1:
            #         continue
            point = Vector2(x, y) * self._physical_size - self._physical_origin

            path_points.append(point)

            # if len(path_points) <= 3:
            #     continue
            # factor = abs(Vector2.cross((path_points[-3] - path_points[-2].normalized()),
            #                            (path_points[-2] - path_points[-1].normalized())))
            # if factor < 0.1:
            #     del path_points[-2]

        return path_points


class PathFinderFigure:

    def __init__(self, path_to_map: str = None, invert: bool = True, scale_ratio: float = 1.0):
        if not load_library():
            raise RuntimeError("AStart DLL not found...")
        self._fig = None
        self._ax = None
        self._start_point = None
        self._end_point = None
        self._path_p = None
        self._map = None
        self._fig, self._ax = plt.subplots()
        self.load_map_image(path_to_map, invert, scale_ratio)

    def __call__(self, *args, **kwargs):
        self.start()

    def load_map_image(self, path_to_map: str, invert: bool = True, scale_ratio: float = 1.0) -> bool:
        try:
            scale_ratio = max(scale_ratio, 0.1)
            img = ImageOps.grayscale(Image.open(path_to_map))
            blur_filter = ImageFilter.GaussianBlur(5.0)
            # threshold_filter = ImageFilter.MaxFilter()
            # median_filter = ImageFilter.MedianFilter()
            img = img.filter(blur_filter)
            # img = img.filter(threshold_filter)
            # img = img.filter(median_filter)

            img_resized = img.resize((int(img.size[0] * scale_ratio), int(img.size[1] * scale_ratio)))
            img_arr = 1.0 + np.asarray(img_resized, dtype=np.float32) / 255.0 * 99.0
            img_arr_dy = img_arr[1:, :] - img_arr[:-1, :]
            img_arr_dx = img_arr[:, 1:] - img_arr[:, :-1]
            img_arr_dy = img_arr_dy[:, :-1]
            img_arr_dx = img_arr_dx[:-1, :]
            img_arr = np.sqrt(img_arr_dx * img_arr_dx + img_arr_dy * img_arr_dy)
            min_value = np.min(img_arr)
            max_value = np.max(img_arr)
            scale = max_value - min_value
            img_arr -= min_value
            img_arr /= scale
            img_arr *= 99.0
            img_arr += 1.0
            # rows, cols = img_arr.shape
            # for row in range(rows):
            #     for col in range(cols):
            #         if img_arr[row, col] < 10.0:
            #             img_arr[row, col] = 1.0
            #             continue
            #         img_arr[row, col] = 100.0
            # img_arr = 100.0 - img_arr
            self._map = Map2(img_arr)
            self._ax.imshow(img_arr)
            return True
        except IOError as error:
            print(error.args)
            return False

    def onclick(self, event):
        if event.dblclick:
            self._ax.lines.clear()
            self._fig.canvas.draw()
            self._start_point = None
            self._end_point = None
            self._path_p = None
            return

        try:
            x, y = int(event.xdata), int(event.ydata)
        except TypeError as error:
            print(error.args)
            return

        if self._start_point is None:
            self._start_point = _Pt2(y, x)
            self._ax.plot(x, y, marker='o', markersize=5, color='red', label='start')
            self._fig.canvas.draw()
            print(f"Start point: {y}, {x}")
        else:
            self._end_point = _Pt2(y, x)
            self._ax.plot(x, y, marker='*', markersize=5, color='green', label='end')
            self._fig.canvas.draw()
            print(f"End point: {y}, {x}")

        if self._start_point is not None and self._end_point is not None:
            self._path_p = _find_path_2(self._map.ptr, self._start_point, self._end_point, 5)
            if self._path_p.contents.n_points == 0:
                print("empty path...")
                return
            print('\n')
            print(f"cost     = {self._path_p.contents.cost}")
            print(f"n_points = {self._path_p.contents.n_points}")
            path_data_x = []
            path_data_y = []
            n_avg = 16
            x_smooth = RunningAverage(n_avg)
            y_smooth = RunningAverage(n_avg)
            for i in range(self._path_p.contents.n_points):
                # path_data_x.append(self._path_p.contents.path_points[i].col)
                # path_data_y.append(self._path_p.contents.path_points[i].row)
                x = x_smooth(self._path_p.contents.path_points[i].col)
                y = y_smooth(self._path_p.contents.path_points[i].row)
                # if i % 3 != 0:
                #     if i != self._path_p.contents.n_points-1:
                #         continue
                path_data_x.append(x)
                path_data_y.append(y)

            for i in range(n_avg):
                x = x_smooth(self._end_point.col)
                y = y_smooth(self._end_point.row)
                if (path_data_x[-1] - x) ** 2 + (path_data_y[-1] - y) ** 2 < 0.5:
                    continue
                path_data_x.append(x)
                path_data_y.append(y)
            if path_data_x[-1] != self._end_point.col or path_data_y[-1] != self._end_point.row:
                path_data_x.append(self._end_point.col)
                path_data_y.append(self._end_point.row)
            self._end_point = None
            self._start_point = None
            self._ax.plot(path_data_x, path_data_y, 'r', linewidth=1)
            # self._ax.plot(path_data_x, path_data_y, '.g', linewidth=1)
            self._ax.plot(path_data_x[0], path_data_y[0], marker='o', markersize=3, color='blue', label='start')
            self._ax.plot(path_data_x[-1], path_data_y[-1], marker='o', markersize=3, color='green', label='end')
            self._fig.canvas.draw()

    def start(self):
        cid = self._fig.canvas.mpl_connect('button_press_event', self.onclick)
        self._fig.suptitle('One click - select point\nDouble click - clear figure')
        plt.show()



