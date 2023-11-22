from .common import NUMERICAL_ACCURACY, fast_math, parallel, parallel_range
from typing import Callable, Tuple, List, Union
from .interpolators import bi_linear_interp_pt
from .vector2 import Vector2
import numpy as np


@fast_math
def _interp(_a: float, _b: float, t) -> float:
    return _a + (_b - _a) * t


@fast_math
def _signum(_a: float) -> float:
    return 1.0 if _a >= 0.0 else -1.0


def _squares_nearest_interp(col, row, dx, dy):
    return (col + dx * 0.5, row),\
           (col + dx, row + dy * 0.5),\
           (col + dx * 0.5, row + dy),\
           (col, row + dy * 0.5)


def _squares_linear_interp(col, row, dx, dy, a_val, b_val, c_val, d_val, threshold):
    d_t = b_val - a_val
    a = (_interp(col, col + dx, _signum(threshold - a_val)), row) if abs(d_t) < NUMERICAL_ACCURACY else \
        (_interp(col, col + dx, (threshold - a_val) / d_t), row)

    d_t = c_val - b_val
    b = (col + dx, _interp(row, row + dy, _signum(threshold - b_val))) if abs(d_t) < NUMERICAL_ACCURACY else\
        (col + dx, _interp(row, row + dy, (threshold - b_val) / d_t))

    d_t = c_val - d_val
    c = (_interp(col, col + dx, _signum(threshold - d_val)), row + dy) if abs(d_t) < NUMERICAL_ACCURACY else \
        (_interp(col, col + dx, (threshold - d_val) / d_t), row + dy)

    d_t = d_val - a_val
    d = (col, _interp(row, row + dy, _signum(threshold - a_val))) if abs(d_t) < NUMERICAL_ACCURACY else \
        (col, _interp(row, row + dy, (threshold - a_val) / d_t))
    return a, b, c, d


@fast_math
def _eval_field_function(field: Callable[[float, float], float], col, row, dx, dy):
    return field(col, row), field(col + dx, row), field(col + dx, row + dy), field(col, row + dy)


@fast_math
def _compute_state(a_val, b_val, c_val, d_val, threshold):
    state = 0
    state += 8 if a_val >= threshold else 0
    state += 4 if b_val >= threshold else 0
    state += 2 if c_val >= threshold else 0
    state += 1 if d_val >= threshold else 0
    return state


_SECTIONS_CONNECTION_ALGORYTHM = {
    1: lambda shape, a, b, c, d: shape.append((c, d)),
    2: lambda shape, a, b, c, d: shape.append((b, c)),
    3: lambda shape, a, b, c, d: shape.append((b, d)),
    4: lambda shape, a, b, c, d: shape.append((a, b)),
    5: lambda shape, a, b, c, d: (shape.append((a, d)), shape.append((b, c))),
    6: lambda shape, a, b, c, d: shape.append((a, c)),
    7: lambda shape, a, b, c, d: shape.append((a, d)),
    8: lambda shape, a, b, c, d: shape.append((a, d)),
    9: lambda shape, a, b, c, d: shape.append((a, c)),
    10: lambda shape, a, b, c, d: (shape.append((a, b)), shape.append((c, d))),
    11: lambda shape, a, b, c, d: shape.append((a, b)),
    12: lambda shape, a, b, c, d: shape.append((b, d)),
    13: lambda shape, a, b, c, d: shape.append((b, c)),
    14: lambda shape, a, b, c, d: shape.append((c, d)),
}


def _array_of_points_wrapper(array: np.ndarray, min_bound: Vector2, max_bound: Vector2):
    return lambda x, y: bi_linear_interp_pt((x - min_bound.x) / (max_bound.x -  min_bound.x),
                                            (y - min_bound.y) / (max_bound.y -  min_bound.y),
                                            array, 1.0, 1.0)


@parallel
def _march_squares_2d(field: Callable[[float, float], float],
                      min_bound: Tuple[float, float], max_bound: Tuple[float, float],
                      march_resolution: Tuple[int, int], threshold: float,
                      interpolate: bool) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:

    rows, cols = max(march_resolution[1], 3), max(march_resolution[0], 3)
    cols_ = cols - 1
    rows_ = cols - 1
    dx = (max_bound[0] - min_bound[0]) / cols_
    dy = (max_bound[1] - min_bound[1]) / rows_
    min_bound_y = min_bound[0]
    min_bound_x = min_bound[1]

    shape: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
    if interpolate:
        for index in parallel_range(cols_ * rows_):
            row_index, col_index = divmod(index, cols_)
            row = row_index * dy + min_bound_y
            col = col_index * dx + min_bound_x
            a_val, b_val, c_val, d_val = _eval_field_function(field, col, row, dx, dy)
            state = _compute_state(a_val, b_val, c_val, d_val, threshold)
            if state not in _SECTIONS_CONNECTION_ALGORYTHM:
                continue
            a, b, c, d = _squares_linear_interp(col, row, dx, dy, a_val, b_val, c_val, d_val, threshold)
            _SECTIONS_CONNECTION_ALGORYTHM[state](shape, a, b, c, d)
        return shape

    for index in parallel_range(cols_ * rows_):
        row_index, col_index = divmod(index, cols_)
        row = row_index * dy + min_bound_y
        col = col_index * dx + min_bound_x
        a_val, b_val, c_val, d_val = _eval_field_function(field, col, row, dx, dy)
        state = _compute_state(a_val, b_val, c_val, d_val, threshold)
        if state not in _SECTIONS_CONNECTION_ALGORYTHM:
            continue
        a, b, c, d = _squares_nearest_interp(col, row, dx, dy)
        _SECTIONS_CONNECTION_ALGORYTHM[state](shape, a, b, c, d)
    return shape


def march_squares_2d(field: Union[Callable[[float, float], float], np.ndarray],
                     min_bound: Vector2 = None,
                     max_bound: Vector2 = None,
                     march_resolution: Tuple[int, int] = None,
                     threshold: float = 0.5,
                     interpolate: bool = True) -> List[Tuple[Vector2, Vector2]]:

    march_resolution = (128, 128) if march_resolution is None else march_resolution
    assert len(march_resolution) == 2 and all(isinstance(v, int) for v in march_resolution)

    min_bound = Vector2(-5.0, -5.0) if min_bound is None else min_bound
    assert isinstance(min_bound, Vector2)

    max_bound = Vector2( 5.0,  5.0) if max_bound is None else max_bound
    assert isinstance(max_bound, Vector2)

    if isinstance(field, np.ndarray):
        field = _array_of_points_wrapper(field, min_bound, max_bound)
        shape = _march_squares_2d(field, tuple(min_bound), tuple(max_bound), march_resolution, threshold, interpolate)
        return [(Vector2(*v[0]), Vector2(*v[1])) for v in shape]
    if isinstance(field, Callable):
        shape = _march_squares_2d(field, tuple(min_bound), tuple(max_bound), march_resolution, threshold, interpolate)
        return [(Vector2(*v[0]), Vector2(*v[1])) for v in shape]
    raise ValueError(f"unsupported field type: {type(field)}")
