from ctypes import CDLL, Structure, c_int, c_float, POINTER
from matplotlib import pyplot as plt
from PIL import Image, ImageOps
import numpy as np
import platform
# matplotlib.use('Qt5Agg') # wtf


a_star_lib = None
if platform.system() == 'Linux':
    a_star_lib = CDLL('./path_finder/lib_astar.so')
elif platform.system() == 'Windows':
    if platform.architecture()[0] == '64bit':
        a_star_lib = CDLL(r'E:\GitHub\Odometry\Odometry\AStar\x64\Release\AStar.dll')
        # a_star_lib = CDLL('./path_finder/x64/AStar.dll')
    else:
        a_star_lib = CDLL('./path_finder/x86/AStar.dll')
if a_star_lib is None:
    raise ImportError("unable to find AStar.dll...")


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


_map_2_new = a_star_lib.map_2_new
_map_2_new.argtypes = [c_int, c_int, NP_ARRAY_2_D_POINTER]
_map_2_new.restype  = POINTER(_Map2)

_map_2_del = a_star_lib.map_2_del
_map_2_del.argtypes = [POINTER(_Map2)]

_map_3_new = a_star_lib.map_3_new
_map_3_new.argtypes = [c_int, c_int, c_int, NP_ARRAY_3_D_POINTER]
_map_3_new.restype  = POINTER(_Map3)

_map_3_del = a_star_lib.map_3_del
_map_3_del.argtypes = [POINTER(_Map3)]

# 2D functions
_path_2_new = a_star_lib.path_2_new
_path_2_new.argtypes = [c_int]
_path_2_new.restype  = POINTER(_Path2)

_path_2_del = a_star_lib.path_2_del
_path_2_del.argtypes = [POINTER(_Path2)]

_find_path_2 = a_star_lib.find_path_2
_find_path_2.argtypes = [POINTER(_Map2), POINTER(_Pt2), POINTER(_Pt2), c_int]
_find_path_2.restype  = POINTER(_Path2)

# _print_map2 = a_star_lib.print_map2
# _print_map2.argtypes = [POINTER(_Map2)]

# 3D functions
_path_3_new = a_star_lib.path_3_new
_path_3_new.argtypes = [c_int]
_path_3_new.restype = POINTER(_Path3)

_path_3_del = a_star_lib.path_3_del
_path_3_del.argtypes = [POINTER(_Path3)]

_find_path_3 = a_star_lib.find_path_3
_find_path_3.argtypes = [POINTER(_Map3), POINTER(_Pt3), POINTER(_Pt3), c_int]
_find_path_3.restype = POINTER(_Path3)


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


class PathFinder:

    def __init__(self, path_to_map: str = None, invert: bool = True, scale_ratio: float = 1.0):
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

    def load_map_image(self, path_to_map: str, invert: bool = True, scale_ratio: float = 0.250) -> bool:
        try:
            scale_ratio = max(scale_ratio, 0.1)
            img = ImageOps.grayscale(Image.open(path_to_map))
            img_resized = img.resize((int(img.size[0] * scale_ratio), int(img.size[1] * scale_ratio)))
            img_arr = np.asarray(img_resized, dtype=np.float32) / 255.0 * 1000.0
            if invert:
                img_arr = 1000.0 - img_arr
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
            self._ax.plot(x, y, marker='o', markersize=3, color='red', label='start')
            self._fig.canvas.draw()
            print(f"Start point: {y}, {x}")
        else:
            self._end_point = _Pt2(y, x)
            self._ax.plot(x, y, marker='o', markersize=3, color='green', label='end')
            self._fig.canvas.draw()
            print(f"End point: {y}, {x}")

        if self._start_point is not None and self._end_point is not None:
            self._path_p = _find_path_2(self._map.ptr, self._start_point, self._end_point, 0)
            self._end_point   = None
            self._start_point = None
            if self._path_p.contents.n_points == 0:
                print("empty path...")
                return
            print(f"cost     = {self._path_p.contents.cost}")
            print(f"n_points = {self._path_p.contents.n_points}\n")
            path_data_x = []
            path_data_y = []
            for i in range(self._path_p.contents.n_points):
                path_data_x.append(self._path_p.contents.path_points[i].col)
                path_data_y.append(self._path_p.contents.path_points[i].row)

            self._ax.plot(path_data_x, path_data_y, color='red', linewidth=1)
            self._ax.plot(path_data_x[0], path_data_y[0], marker='o', markersize=3, color='blue', label='start')
            self._ax.plot(path_data_x[-1], path_data_y[-1], marker='o', markersize=3, color='green', label='end')
            self._fig.canvas.draw()

    def start(self):
        cid = self._fig.canvas.mpl_connect('button_press_event', self.onclick)
        self._fig.suptitle('One click - select point\nDouble click - clear figure')
        plt.show()



