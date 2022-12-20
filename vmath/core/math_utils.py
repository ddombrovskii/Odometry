from Odometry.vmath.core.vectors import Vec2, Vec3
from typing import List, Union
import numpy as np
import random
import numba


@numba.njit(fastmath=True, parallel=True)
def median_filter_1d_np(array_data: np.ndarray, filter_size: int = 11,
                        range_start: int = 0, range_end: int = -1) -> np.ndarray:
    if filter_size % 2 != 1:
        raise Exception("Median filter length must be odd.")

    if array_data.ndim != 1:
        raise Exception("Input must be one-dimensional.")

    result = np.zeros_like(array_data)

    if range_start == range_end:
        return result

    if range_end < 0:
        range_end = array_data.size

    if range_end < range_start:
        range_end, range_start = range_start, range_end

    range_end = min(range_end, array_data.size)

    range_start = max(range_start, 0)

    half_filter_size = filter_size // 2

    for i in numba.prange(range_start, range_end):
        values_window = []
        for j in range(i - half_filter_size, i + half_filter_size):
            if j < 0:
                values_window.append(0.0)
                continue
            if j >= array_data.size:
                values_window.append(0.0)
                continue
            values_window.append(array_data[j])
        values_window = sorted(values_window)
        result[i] = values_window[len(values_window) // 2]
        values_window.clear()

    return result


@numba.njit(fastmath=True, parallel=True)
def median_filter_2d_np(array_data: np.ndarray, filter_size: int = 11):
    if filter_size % 2 != 1:
        raise Exception("Median filter length must be odd.")

    if array_data.ndim != 2:
        raise Exception("Input must be two-dimensional.")

    indexer = filter_size // 2

    height, width = array_data.shape

    result = np.zeros_like(array_data)

    for i in numba.prange(height):
        temp = []  # only for numba usage
        for j in range(width):
            for z in range(filter_size):
                if i + z - indexer < 0 or i + z - indexer > height - 1:
                    for c in range(filter_size):
                        temp.append(0.0)
                else:
                    if j + z - indexer < 0 or j + indexer > width - 1:
                        temp.append(0.0)
                    else:
                        for k in range(filter_size):
                            temp.append(array_data[i + z - indexer][j + k - indexer])
                result[i][j] = temp[len(temp) // 2]
            temp.clear()
    return result


@numba.njit(fastmath=True, parallel=True)
def m_f_list_float(array_data: List[float], filter_size: int = 11,
                   range_start: int = 0, range_end: int = -1) -> List[float]:
    if filter_size % 2 != 1:
        raise Exception("Median filter length must be odd.")

    if len(array_data) == 0:
        return array_data

    if range_start == range_end:
        return [0.0]

    if range_end < 0:
        range_end = len(array_data)

    if range_end < range_start:
        range_end, range_start = range_start, range_end

    result = [0.0] * (range_end - range_start)

    range_end = min(range_end, len(array_data))

    range_start = max(range_start, 0)

    half_filter_size = filter_size // 2

    for index in numba.prange(range_start, range_end):
        values_window = []
        for window_index in range(index - half_filter_size, index + half_filter_size):
            if window_index < 0:
                values_window.append(0.0)
                continue
            if window_index >= len(result):
                values_window.append(0.0)
                continue
            values_window.append(array_data[window_index])

        values_window = sorted(values_window)

        result[index - range_start] = values_window[len(values_window)//2]

        values_window.clear()

    return result


@numba.njit(fastmath=True, parallel=True)
def m_f_list_vec2(array_data: List[Vec2], filter_size: int = 11,
                  range_start: int = 0, range_end: int = -1) -> List[Vec2]:
    if filter_size % 2 != 1:
        raise Exception("Median filter length must be odd.")

    if len(array_data) == 0:
        return array_data

    if range_start == range_end:
        return [Vec2(0.0)]

    if range_end < 0:
        range_end = len(array_data)

    if range_end < range_start:
        range_end, range_start = range_start, range_end

    range_end = min(range_end, len(array_data))

    range_start = max(range_start, 0)

    half_filter_size = filter_size // 2

    result = [Vec2(0.0)] * (range_end - range_start)

    for index in numba.prange(range_start, range_end):
        values_window_x = []
        values_window_y = []
        for window_index in range(index - half_filter_size, index + half_filter_size):
            if window_index < 0:
                values_window_x.append(0.0)
                values_window_y.append(0.0)
                continue
            if window_index >= len(array_data):
                values_window_x.append(0.0)
                values_window_y.append(0.0)
                continue
            values_window_x.append(array_data[window_index].x)
            values_window_y.append(array_data[window_index].y)

        result[index - range_start] =\
            Vec2(values_window_x[len(values_window_x)//2], values_window_y[len(values_window_y)//2])
        values_window_x.clear()
        values_window_y.clear()

    return result


@numba.njit(fastmath=True, parallel=True)
def m_f_list_vec3(array_data: List[Vec3], filter_size: int = 11,
                  range_start: int = 0, range_end: int = -1) -> List[Vec3]:
    if filter_size % 2 != 1:
        raise Exception("Median filter length must be odd.")

    if len(array_data) == 0:
        return array_data

    if range_start == range_end:
        return [Vec3(0.0)]

    if range_end < 0:
        range_end = len(array_data)

    if range_end < range_start:
        range_end, range_start = range_start, range_end

    range_end = min(range_end, len(array_data))

    range_start = max(range_start, 0)

    half_filter_size = filter_size // 2

    result = [Vec3(0.0)] * (range_end - range_start)

    for index in numba.prange(range_start, range_end):
        values_window_x = []
        values_window_y = []
        values_window_z = []
        for window_index in range(index - half_filter_size, index + half_filter_size):
            if window_index < 0:
                values_window_x.append(0.0)
                values_window_y.append(0.0)
                values_window_z.append(0.0)
                continue
            if window_index >= len(result):
                values_window_x.append(0.0)
                values_window_y.append(0.0)
                values_window_z.append(0.0)
                continue
            values_window_x.append(array_data[window_index].x)
            values_window_y.append(array_data[window_index].y)
            values_window_z.append(array_data[window_index].z)

        result[index - range_start] = Vec3(values_window_x[len(values_window_x)//2],
                                           values_window_y[len(values_window_y)//2],
                                           values_window_z[len(values_window_z)//2])
        values_window_x.clear()
        values_window_y.clear()
        values_window_z.clear()

    return result


def median_filter_1d(data: Union[List[float], List[Vec2], List[Vec3]], window_size: int = 19,
                     range_start: int = 0, range_end: int = -1) -> Union[List[float], List[Vec2], List[Vec3]]:
    if isinstance(data[0], float):
        return m_f_list_float(data, window_size, range_start, range_end)
    if isinstance(data[0], Vec2):
        return m_f_list_vec2(data, window_size, range_start, range_end)
    if isinstance(data[0], Vec3):
        return m_f_list_vec3(data, window_size, range_start, range_end)
    raise Exception(f"Median filter 1d error :: unsupported type of list items \n list[0] got type of {type(data[0])}")


@numba.njit(fastmath=True)
def _prod_lists(iterable_a, iterable_b):
    return [a_i * b_i for a_i, b_i in zip(iterable_a, iterable_b)]


def _scalar_prod_lists(iterable_a, iterable_b):
    return sum((a_i * b_i for a_i, b_i in zip(iterable_a, iterable_b)))


@numba.njit(fastmath=True)
def _ones_list(size: int):
    return [1.0 for _ in range(size)]


@numba.njit(fastmath=True)
def _polynom(x: float, coefficients: np.ndarray) -> float:
    p: float = 0.0
    x_: float = 1.0
    for _c in coefficients:
        p += _c * x_
        x_ *= x
    return p


# @numba.njit(fastmath=True, parallel=True)
def rms_filter(x: List[float], y: List[float], order: int = 4) -> List[float]:
    a_m = np.zeros((order, order,), dtype=float)
    c_m = np.zeros((order,), dtype=float)
    _x = np.array(x)
    _y = np.array(x)
    for row in range(order):
        if row == 0:
            _x_row = np.ones_like(_x)
        else:
            _x_row *= _x

        c_m[row] = (_x_row * y).sum()

        for col in range(row + 1):
            if col == 0:
                _x_col = np.ones_like(_x)
            else:
                _x_col *= _x

            a_m[row][col] = (_x_col * _x_row).sum()
            a_m[col][row] = a_m[row][col]

    coefficients = np.linalg.inv(a_m) @ c_m

    return [_polynom(x_i, coefficients) for x_i in x]


def data_test():
    x = list(np.linspace(0, np.pi * 4, 2048))
    y = list(np.sin(x) + np.array([random.uniform(-0.33, 0.33) for _ in range(len(x))]))
    y__ = rms_filter(x, y,  11)
    import pylab as p
    p.plot(x, y, 'r')
    p.plot(x, y__, 'k')
    p.show()


def median_filter_test():
    import pylab as p
    x = list(np.linspace(0, 1, 101))
    x[12] = 1.5
    x[22] = 1.5
    x[32] = 1.5
    x[52] = 1.5
    # p.plot (x)
    y__  =  median_filter_1d (x, 9)
    #y__ = median_filter_1d_np(x,  5, range_start=-20, range_end=60)
    # print(f"shape: {y_.shape},  size: {y_.size}")
    # print(f"shape: {y__.shape}, size: {y__.size}")
    # p.plot (y_)
    p.plot(y__)
    p.show()


if __name__ == '__main__':
    a = (i for i in range(4))
    b = (i for i in range(4))
    # c = sum((a_i * b_i for a_i, b_i in zip(a, b)))
    # print(c)
    c = [a_i * b_i for a_i, b_i in zip(a, b)]
    print(c)
    [print(f"{i},{j}") for i, j in enumerate(c)]
    data_test()
    median_filter_test()

