from Odometry.vmath.core.vectors import Vec2, Vec3
from typing import List
import numpy as np


def median_filter_1d(array_data: np.ndarray, filter_size: int = 15, do_copy: bool = False,
                     range_start: int = 0, range_end: int = -1) -> np.ndarray:
    if filter_size % 2 != 1:
        raise Exception("Median filter length must be odd.")

    if array_data.ndim != 1:
        raise Exception("Input must be one-dimensional.")

    if do_copy:
        result = np.zeros_like(array_data)
    else:
        result = array_data

    if range_start == range_end:
        return result

    if range_end < 0:
        range_end = array_data.size

    if range_end < range_start:
        range_end, range_start = range_start, range_end

    range_end = min(range_end, array_data.size)

    range_start = max(range_start, 0)

    import bisect

    values_window = []

    half_filter_size = filter_size // 2

    for i in range(range_start, range_end):
        for j in range(i - half_filter_size, i + half_filter_size):
            if j < 0:
                bisect.insort(values_window, 0)
                continue
            if j >= array_data.size:
                bisect.insort(values_window, 0)
                continue
            bisect.insort(values_window, array_data[j])

        result[i] = values_window[len(values_window)//2]

        values_window.clear()

    return result


def median_filter_2d(array_data: np.ndarray, filter_size: int = 15, do_copy: bool = False):
    import bisect

    if filter_size % 2 != 1:
        raise Exception("Median filter length must be odd.")

    if array_data.ndim != 2:
        raise Exception("Input must be two-dimensional.")

    indexer = filter_size // 2

    height, width = array_data.shape

    temp = []

    if do_copy:
        result = np.zeros_like(array_data)
    else:
        result = array_data

    for i in range(height):
        # temp = [] only for numba usage
        for j in range(width):
            for z in range(filter_size):
                if i + z - indexer < 0 or i + z - indexer > height - 1:
                    for c in range(filter_size):
                        bisect.insort(temp, 0)
                else:
                    if j + z - indexer < 0 or j + indexer > width - 1:
                        bisect.insort(temp, 0)
                    else:
                        for k in range(filter_size):
                            bisect.insort(temp, array_data[i + z - indexer][j + k - indexer])
                result[i][j] = temp[len(temp) // 2]
            temp.clear()
    return result


def m_f_list_vec2(array_data: List[Vec2], filter_size: int = 5, do_copy: bool = False,
                  range_start: int = 0, range_end: int = -1) -> List[Vec2]:
    if filter_size % 2 != 1:
        raise Exception("Median filter length must be odd.")

    if do_copy:
        result = array_data.copy()
    else:
        result = array_data

    if range_start == range_end:
        return result

    if range_end < 0:
        range_end = len(array_data)

    if range_end < range_start:
        range_end, range_start = range_start, range_end

    range_end = min(range_end, len(array_data))

    range_start = max(range_start, 0)

    import bisect

    values_window_x = []

    values_window_y = []

    half_filter_size = filter_size // 2

    for index in range(range_start, range_end):
        for window_index in range(index - half_filter_size, index + half_filter_size):
            if window_index < 0:
                bisect.insort(values_window_x, 0)
                bisect.insort(values_window_y, 0)
                continue
            if window_index >= len(result):
                bisect.insort(values_window_x, 0)
                bisect.insort(values_window_y, 0)
                continue
            bisect.insort(values_window_x, array_data[window_index].x)
            bisect.insort(values_window_y, array_data[window_index].y)

        result.append(Vec2(values_window_x[len(values_window_x)//2], values_window_y[len(values_window_y)//2]))
        values_window_x.clear()
        values_window_y.clear()

    return result


def m_f_list_vec3(array_data: List[Vec3], filter_size: int = 5, do_copy: bool = False,
                  range_start: int = 0, range_end: int = -1) -> List[Vec3]:
    if filter_size % 2 != 1:
        raise Exception("Median filter length must be odd.")

    if filter_size % 2 != 1:
        raise Exception("Median filter length must be odd.")

    if do_copy:
        result = array_data.copy()
    else:
        result = array_data

    if range_start == range_end:
        return result

    if range_end < 0:
        range_end = len(array_data)

    if range_end < range_start:
        range_end, range_start = range_start, range_end

    range_end = min(range_end, len(array_data))

    range_start = max(range_start, 0)

    import bisect

    values_window_x = []

    values_window_y = []

    values_window_z = []

    half_filter_size = filter_size // 2

    result = []

    for index in range(range_start, range_end):
        for window_index in range(index - half_filter_size, index + half_filter_size):
            if window_index < 0:
                bisect.insort(values_window_x, 0)
                bisect.insort(values_window_y, 0)
                bisect.insort(values_window_z, 0)
                continue
            if window_index >= len(result):
                bisect.insort(values_window_x, 0)
                bisect.insort(values_window_y, 0)
                bisect.insort(values_window_z, 0)
                continue
            bisect.insort(values_window_x, array_data[window_index].x)
            bisect.insort(values_window_y, array_data[window_index].y)
            bisect.insort(values_window_y, array_data[window_index].z)

        result.append(Vec3(values_window_x[len(values_window_x)//2],
                           values_window_y[len(values_window_y)//2],
                           values_window_z[len(values_window_z)//2]))
        values_window_x.clear()
        values_window_y.clear()
        values_window_z.clear()

    return result
