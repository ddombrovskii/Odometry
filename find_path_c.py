from ctypes import CDLL, Structure, c_int, c_float, POINTER, Array
from typing import Any
from PIL import Image, ImageDraw
import cv2
import numpy as np

# a_star_lib = CDLL('./AStar/x64/Release/AStar.dll')
a_star_lib = CDLL('./AStar/lib_astar.so')

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

    # a_star_lib.print_map(new_map)

    path_p = a_star_lib.find_path(new_map, start_pt, end_pt)

    print_path_data(path_p)

    path_del_func(path_p)
    print("Path pointer was deleted")


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

    tests_3 = [
        (Pt(0, 0), Pt(4, 1)),
        (Pt(0, 0), Pt(1, 14)),
        (Pt(0, 0), Pt(0, 29)),
        (Pt(0, 0), Pt(6, 29))
    ]

    mew_map = Map(c_int(cols), c_int(rows), c_weights)
    for points in tests_3:
        start_point = points[0]
        end_point = points[1]

        print(f"start point: ({start_point.row}, {start_point.col})")
        print(f"end point: ({end_point.row}, {end_point.col})")

        path_p = find_path_func(mew_map, start_point, end_point)
        print_path_data(path_p)
        path_del_func(path_p)


def get_weights_from_binary_image(img_path: str, scale: float = 0.25) -> [Array[Any], int, int, list]:
    image = cv2.imread(img_path, 0)
    image = cv2.bitwise_not(image)
    resized_image = image
    print(f"{scale=}")
    print(f"original image shape: {resized_image.shape}")
    if scale != 1.0:
        down_points = (int(image.shape[1] * scale), int(image.shape[0] * scale))
        resized_image = cv2.resize(image, down_points, interpolation=cv2.INTER_LINEAR)
    print(f"resized image shape: {resized_image.shape}")
    py_weights = []
    for row in resized_image:
        py_weights += list(row)
    py_weights = np.array(py_weights, dtype=int)
    py_weights %= 2
    py_weights *= 999
    py_weights += 1
    c_weights = (c_float * len(py_weights))(*py_weights)
    return c_weights, resized_image.shape[0], resized_image.shape[1], resized_image


def get_weights_from_non_binary_image(img_path: str, scale: float = 0.25) -> [Array[Any], int, int, Image.Image]:
    img = Image.open(img_path)
    print(f"{scale=}")
    print(f"original image shape: {img.size}")
    resized_image = img.resize((int(img.size[0]*scale), int(img.size[1]*scale)))
    print(f"resized image shape: {resized_image.size}")
    img_arr = np.asarray(resized_image)
    img_arr = cv2.bitwise_not(img_arr)
    py_weights = []
    for row in img_arr:
        py_weights += list(row)
    py_weights = np.array(py_weights, dtype=int)
    py_weights += 1
    c_weights = (c_float * len(py_weights))(*py_weights)
    return c_weights, img_arr.shape[0], img_arr.shape[1], resized_image


def print_weights(c_weights: Array[Any], rows: int, cols: int):
    for i in range(rows):
        for j in range(cols):
            print(c_weights[i * rows + j], end=" ")
        print()


def find_first_zero(c_weights: POINTER(c_float), rows: int, cols: int) -> Pt:
    for i in range(rows):
        for j in range(cols):
            if c_weights[rows * i + j] == 0.0:
                return Pt(i, j)


def find_last_zero(c_weights: POINTER(c_float), rows: int, cols: int) -> Pt:
    for i in range(rows - 1, -1, -1):
        for j in range(cols - 1, -1, -1):
            if c_weights[rows * i + j] == 0.0:
                return Pt(i, j)


def select_point(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print(f'({y}, {x})')


def show_path(image, path_p: POINTER(Path), start_point, end_point):
    if not isinstance(image, Image.Image):
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        for i in range(path_p.contents.n_points):
            x = path_p.contents.path_points[i].col
            y = path_p.contents.path_points[i].row

            # отмечаю выбранные точки на картинке
            image = cv2.circle(image, (x, y), radius=1, color=(255, 0, 0), thickness=-1)

        image = cv2.circle(image, (start_point.col, start_point.row), radius=3, color=(0, 255, 0), thickness=-1)
        image = cv2.circle(image, (end_point.col, end_point.row), radius=3, color=(0, 0, 255), thickness=-1)
        cv2.imshow("path", image)
        cv2.waitKey(0)
    else:
        rgb_image = image.convert('RGB')
        draw = ImageDraw.Draw(rgb_image)
        for i in range(path_p.contents.n_points):
            x = path_p.contents.path_points[i].col
            y = path_p.contents.path_points[i].row

            draw.point((x, y), fill='blue')
        draw.point((start_point.col, start_point.row), fill='green')
        draw.point((start_point.col, start_point.row), fill='red')
        rgb_image.show("Founded path")


def test_path_finder_on_map_from_img():
    # c_weights, rows, cols, resized_image = get_weights_from_binary_image("./mapping/map1.png")
    # c_weights, rows, cols, resized_image = get_weights_from_binary_image("./mapping/map_low_res.png", scale=1.0)
    c_weights, rows, cols, resized_image = get_weights_from_non_binary_image("./mapping/map_blured.png")

    # создаю окно для получения координат начальной и конечной точек (дабл клик ЛКМ)
    # cv2.namedWindow("select point")
    # cv2.setMouseCallback("select point", select_point)
    # cv2.imshow("select point", resized_image)
    # cv2.waitKey(0)

    tests_1 = [
        (Pt(5, 97), Pt(139, 32)),
        (Pt(5, 97), Pt(98, 192)),
        (Pt(5, 97), Pt(104, 72)),
        (Pt(5, 97), Pt(4, 178)),
        (Pt(98, 193), Pt(4, 179)),
        (Pt(98, 193), Pt(42, 3)),
        (Pt(61, 137), Pt(57, 52))
    ]

    tests_2 = [
        (Pt(3, 2), Pt(84, 5)),
        (Pt(3, 2), Pt(143, 5)),
        (Pt(3, 2), Pt(142, 36)),
        (Pt(3, 2), Pt(143, 82)),
        (Pt(3, 2), Pt(143, 146)),
        (Pt(3, 2), Pt(142, 190)),
        (Pt(3, 2), Pt(113, 192)),
        (Pt(3, 2), Pt(61, 176)),
        (Pt(3, 2), Pt(68, 158)),
        (Pt(3, 2), Pt(24, 184)),
        (Pt(3, 2), Pt(22, 131)),
        (Pt(3, 2), Pt(41, 87)),
        (Pt(3, 2), Pt(94, 66)),
    ]

    map_from_img = Map(c_int(cols), c_int(rows), c_weights)

    for points in tests_1:
        start_point = points[0]
        end_point = points[1]

        print(f"start point: ({start_point.row}, {start_point.col})")
        print(f"end point: ({end_point.row}, {end_point.col})")

        path_p = find_path_func(map_from_img, start_point, end_point)
        # print_path_data(path_p)
        show_path(resized_image, path_p, start_point, end_point)
        path_del_func(path_p)


if __name__ == "__main__":
    test_path_finder_on_binary_map()
    # test_path_finder_on_non_binary_map()

    # test_path_finder_on_map_from_img()
    # a_star_lib.test_lib()