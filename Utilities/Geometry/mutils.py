from .common import parallel, parallel_range, fast_math
from numpy.linalg import LinAlgError
from typing import Tuple
from math import sqrt
import numpy as np


@fast_math
def linear_regression(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    """
    Линейная регрессия.\n
    Основные формулы:\n
    yi - xi*k - b = ei\n
    yi - (xi*k + b) = ei\n
    (yi - (xi*k + b))^2 = yi^2 - 2*yi*(xi*k + b) + (xi*k + b)^2 = ei^2\n
    yi^2 - 2*(yi*xi*k + yi*b) + (xi^2 * k^2 + 2 * xi * k * b + b^2) = ei^2\n
    yi^2 - 2*yi*xi*k - 2*yi*b + xi^2 * k^2 + 2 * xi * k * b + b^2 = ei^2\n
    d ei^2 /dk = - 2*yi*xi + 2 * xi^2 * k + 2 * xi * b = 0\n
    d ei^2 /db = - 2*yi + 2 * xi * k + 2 * b = 0\n
    ====================================================================================================================\n
    d ei^2 /dk = (yi - xi * k - b) * xi = 0\n
    d ei^2 /db =  yi - xi * k - b = 0\n
    ====================================================================================================================\n
    Σ(yi - xi * k - b) * xi = 0\n
    Σ yi - xi * k - b = 0\n
    ====================================================================================================================\n
    Σ(yi - xi * k - b) * xi = 0\n
    Σ(yi - xi * k) = n * b\n
    ====================================================================================================================\n
    Σyi - k * Σxi = n * b\n
    Σxi*yi - xi^2 * k - xi*b = 0\n
    Σxi*yi - Σxi^2 * k - Σxi*b = 0\n
    Σxi*yi - Σxi^2 * k - Σxi*(Σyi - k * Σxi) / n = 0\n
    Σxi*yi - Σxi^2 * k - Σxi*Σyi / n + k * (Σxi)^2 / n = 0\n
    Σxi*yi - Σxi*Σyi / n + k * ((Σxi)^2 / n - Σxi^2)  = 0\n
    Σxi*yi - Σxi*Σyi / n = -k * ((Σxi)^2 / n - Σxi^2)\n
    (Σxi*yi - Σxi*Σyi / n) / (Σxi^2 - (Σxi)^2 / n) = k\n
    окончательно:\n
    k = (Σxi*yi - Σxi*Σyi / n) / (Σxi^2 - (Σxi)^2 / n)\n
    b = (Σyi - k * Σxi) /n\n
    :param x: массив значений по x
    :param y: массив значений по y
    :returns: возвращает пару (k, b), которая является решением задачи (Σ(yi -(k * xi + b))^2)->min
    """
    assert x.size == y.size, "linear_regression::error::x.size != y.size"
    sum_x = x.sum()
    sum_y = y.sum()
    sum_xy = (x * y).sum()
    sum_xx = (x * x).sum()
    inv_n = 1.0 / x.size
    k = (sum_xy - sum_x * sum_y * inv_n) / (sum_xx - sum_x * sum_x * inv_n)
    return k, (sum_y - k * sum_x) * inv_n


@fast_math
def bi_linear_regression(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> Tuple[float, float, float]:
    """
    Билинейная регрессия.\n
    Основные формулы:\n
    zi - (yi * ky + xi * kx + b) = ei\n
    zi^2 - 2*zi*(yi * ky + xi * kx + b) + (yi * ky + xi * kx + b)^2 = ei^2\n
    ei^2 = zi^2 - 2*yi*zi*ky - 2*zi*xi*kx - 2*zi*b + ((yi*ky)^2 + 2 * (xi*kx*yi*ky + b*yi*ky) + (xi*kx + b)^2)\n
    ei^2 = zi^2 - 2*yi*zi*ky - 2*zi*xi*kx - 2*zi*b + (yi*ky)^2 + 2*xi*kx*yi*ky + 2*b*yi*ky + (xi*kx + b)^2\n
    ei^2 =\n
    zi^2 - 2*zi*yi*ky - 2*zi*xi*kx - 2*zi*b + (yi*ky)^2 + 2*xi*kx*yi*ky + 2*b*yi*ky + (xi*kx)^2 + 2*xi*kx*b+ b^2\n
    ei^2 =\n
    zi^2 - 2*zi*yi*ky - 2*zi*xi*kx - 2*zi*b + (yi*ky)^2 + 2*xi*kx*yi*ky + 2*b*yi*ky + (xi*kx)^2 + 2*xi*kx*b+ b^2\n
    ei^2 =\n
    zi^2 - 2*zi*yi*ky - 2*zi*xi*kx - 2*zi*b + (yi*ky)^2 + 2*xi*kx*yi*ky + 2*b*yi*ky + (xi*kx)^2 + 2*xi*kx*b + b^2\n
    ====================================================================================================================\n
    d Σei^2 /dkx = Σ-zi*xi + ky*xi*yi + kx*xi^2 + xi*b = 0\n
    d Σei^2 /dky = Σ-zi*yi + ky*yi^2 + kx*xi*yi + b*yi = 0\n
    d Σei^2 /db  = Σ-zi + yi*ky + xi*kx = 0\n
    ====================================================================================================================\n
    d Σei^2 /dkx / dkx = Σ xi^2\n
    d Σei^2 /dkx / dky = Σ xi*yi\n
    d Σei^2 /dkx / db  = Σ xi\n
    ====================================================================================================================\n
    d Σei^2 /dky / dkx = Σ xi*yi\n
    d Σei^2 /dky / dky = Σ yi^2\n
    d Σei^2 /dky / db  = Σ yi\n
    ====================================================================================================================\n
    d Σei^2 /db / dkx = Σ xi\n
    d Σei^2 /db / dky = Σ yi\n
    d Σei^2 /db / db  = n\n
    ====================================================================================================================\n
    Hesse matrix:\n
    || d Σei^2 /dkx / dkx;  d Σei^2 /dkx / dky;  d Σei^2 /dkx / db ||\n
    || d Σei^2 /dky / dkx;  d Σei^2 /dky / dky;  d Σei^2 /dky / db ||\n
    || d Σei^2 /db  / dkx;  d Σei^2 /db  / dky;  d Σei^2 /db  / db ||\n
    ====================================================================================================================\n
    Hesse matrix:\n
                   | Σ xi^2;  Σ xi*yi; Σ xi |\n
    H(kx, ky, b) = | Σ xi*yi; Σ yi^2;  Σ yi |\n
                   | Σ xi;    Σ yi;    n    |\n
    ====================================================================================================================\n
                      | Σ-zi*xi + ky*xi*yi + kx*xi^2 + xi*b |\n
    grad(kx, ky, b) = | Σ-zi*yi + ky*yi^2 + kx*xi*yi + b*yi |\n
                      | Σ-zi + yi*ky + xi*kx                |\n
    ====================================================================================================================\n
    Окончательно решение:\n
    |kx|   |1|\n
    |ky| = |1| -  H(1, 1, 0)^-1 * grad(1, 1, 0)\n
    | b|   |0|\n

    :param x: массив значений по x
    :param y: массив значений по y
    :param z: массив значений по z
    :returns: возвращает тройку (kx, ky, b), которая является решением задачи (Σ(zi - (yi * ky + xi * kx + b))^2)->min
    """
    assert x.size == y.size, "bi_linear_regression::error::x.size != y.size"
    assert x.size == z.size, "bi_linear_regression::error::x.size != z.size"

    sum_x = x.sum()
    sum_y = y.sum()
    sum_z = z.sum()
    sum_xy = (x * y).sum()
    sum_xx = (x * x).sum()
    sum_yy = (y * y).sum()
    sum_zy = (z * y).sum()
    sum_zx = (x * z).sum()

    hess = np.array(((sum_xx, sum_xy, sum_x),
                     (sum_xy, sum_yy, sum_y),
                     (sum_x,  sum_y, x.size)))
    grad =  np.array((sum_xx + sum_xy - sum_zx,
                      sum_xy + sum_yy - sum_zy,
                      sum_x  + sum_y - sum_z))
    try:
        kx, ky, b = np.array((1.0, 1.0, 0.0)) - np.linalg.inv(hess) @ grad
        return kx, ky, b
    except LinAlgError as err:
        print(err.args)
        return 0.0, 0.0, 0.0


@fast_math
def polynom(x: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    :param x: массив значений по x\n
    :param b: массив коэффициентов полинома\n
    :returns: возвращает полином yi = Σxi^j*bj\n
    """
    result = b[0] + b[1] * x
    _x = x.copy()
    for i in range(2, b.size):
        _x *= x
        result += b[i] * _x
    return result


@fast_math
def poly_regression(x: np.ndarray, y: np.ndarray, order: int = 5) -> np.ndarray:
    """
    Полином: y = Σ_j x^j * bj\n
    Отклонение: ei =  yi - Σ_j xi^j * bj\n
    Минимизируем: Σ_i(yi - Σ_j xi^j * bj)^2 -> min\n
    Σ_i(yi - Σ_j xi^j * bj)^2 = Σ_iyi^2 - 2 * yi * Σ_j xi^j * bj +(Σ_j xi^j * bj)^2\n
    условие минимума:\n d/dbj Σ_i ei = d/dbj (Σ_i yi^2 - 2 * yi * Σ_j xi^j * bj +(Σ_j xi^j * bj)^2) = 0\n
    :param x: массив значений по x
    :param y: массив значений по y
    :param order: порядок полинома
    :return: набор коэффициентов bi полинома y = Σx^i*bi
    """
    assert x.size == y.size, "poly_regression::error::x.size != y.size"
    a_m = np.zeros((order, order,), dtype=float)
    c_m = np.zeros((order,), dtype=float)
    _x_row = np.ones_like(x)
    for row in range(order):
        _x_row = _x_row * x if row != 0 else _x_row
        c_m[row] = (_x_row * y).sum()
        _x_col = np.ones_like(x)
        for col in range(row + 1):
            _x_col = _x_col * x if col != 0 else _x_col
            a_m[col, row] = a_m[row, col] = (_x_col * _x_row).sum()
    try:
        return np.linalg.inv(a_m) @ c_m
    except LinAlgError as err:
        print(err.args)
        return np.array(linear_regression(x, y))


@fast_math
def poly_fit(x: np.ndarray, x_points: np.ndarray, y_points: np.ndarray, order: int = 16) -> np.ndarray:
    return polynom(x, poly_regression(x_points, y_points, order))


@fast_math
def n_linear_regression(data_rows: np.ndarray) -> np.ndarray:
    """
    H_ij = Σx_i * x_j, i in [0, rows - 1] , j in [0, rows - 1]
    H_ij = Σx_i, j = rows i in [rows, :]
    H_ij = Σx_j, j in [:, rows], i = rows

           | Σkx * xi^2    + Σky * xi * yi + b * Σxi - Σzi * xi|\n
    grad = | Σkx * xi * yi + Σky * yi^2    + b * Σyi - Σzi * yi|\n
           | Σyi * ky      + Σxi * kx                - Σzi     |\n

    x_0 = [1,...1, 0] =>

           | Σ xi^2    + Σ xi * yi - Σzi * xi|\n
    grad = | Σ xi * yi + Σ yi^2    - Σzi * yi|\n
           | Σxi       + Σ yi      - Σzi     |\n

    :param data_rows:  состоит из строк вида: [x_0,x_1,...,x_n, f(x_0,x_1,...,x_n)]
    :return:
    """
    assert data_rows.ndim == 2, "n_linear_regression::error::data_rows.ndim != 2"
    n_points, n_dimension = data_rows.shape
    assert n_dimension != 1, "n_linear_regression::error::sample dimension is one"
    hess = np.zeros((n_dimension, n_dimension,), dtype=float)
    grad = np.zeros((n_dimension,), dtype=float)
    pt_0 = np.ones((n_dimension,), dtype=float)
    hess[-1, -1] = n_points
    pt_0[-1] = 0.0
    for row in range(n_dimension - 1):
        hess[-1, row] = hess[row, -1] = (data_rows[:, row]).sum()
        for col in range(row + 1):
            hess[col, row] = hess[row, col] = np.dot(data_rows[:, row], data_rows[:, col])

    for row in range(n_dimension - 1):
        grad[row] = hess[row, :-1].sum() - np.dot(data_rows[:, -1], data_rows[:, row])
    grad[-1] = hess[-1, :-1].sum() - data_rows[:, -1].sum()
    try:
        return pt_0 - np.linalg.inv(hess) @ grad
    except LinAlgError as err:
        print(err.args)
        return np.zeros((n_dimension,), dtype=float)


@fast_math
def quadratic_regression_2d(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
    assert x.size == y.size, "quadratic_regression_2d::error::x.size != y.size"
    assert x.size == z.size, "quadratic_regression_2d::error::x.size != z.size"
    b = (x * x, x * y, y * y, x, y, np.array([1.0]))
    n_b = len(b)
    a_m = np.zeros((n_b, n_b), dtype=float)
    b_c = np.zeros((n_b,), dtype=float)
    for row in range(n_b):
        b_c[row] = (b[row] * z).sum()
        for col in range(row + 1):
            a_m[col, row] = a_m[row, col] = (b[row] * b[col]).sum()
    a_m[-1, -1] = x.size
    try:
        return np.linalg.inv(a_m) @ b_c
    except LinAlgError as err:
        print(err.args)
        return np.array(bi_linear_regression(x, y, z))


@fast_math
def second_order_surface(x: np.ndarray, y: np.ndarray, args: np.ndarray) -> np.ndarray:
    assert x.shape == y.shape, "second_order_surface::error::x.shape != y.shape"
    assert args.size == 6, "second_order_surface::error::args.size != 6"
    return sum(ci * argi for ci, argi in zip(args.flat, (x * x, x * y, y * y, x, y, 1.0)))


@fast_math
def quadratic_shape_fit(y: np.ndarray, x: np.ndarray,
                        x_points: np.ndarray,
                        y_points: np.ndarray,
                        z_points: np.ndarray) -> np.ndarray:
    fit_params = quadratic_regression_2d(x_points, y_points, z_points)
    if fit_params.size == 3:
        return fit_params[0] * x + fit_params[1] * y + fit_params[2]
    return second_order_surface(x, y, fit_params)


@fast_math
def _in_range(val: float, x_0: float, x_1: float) -> bool:
    """
    Проверяет вхождение числа в диапазон.\n
    :param val: число
    :param x_0: левая граница диапазона
    :param x_1: правая граница диапазона
    :return:
    """
    if val < x_0:
        return False
    if val > x_1:
        return False
    return True


@fast_math
def square_equation(a: float, b: float, c: float) -> Tuple[bool, float, float]:
    det: float = b * b - 4.0 * a * c
    if det < 0.0:
        return False, 0.0, 0.0
    det = sqrt(det)
    return True, (-b + det) / 2.0 / a, (-b - det) / 2.0 / a


@fast_math
def clamp(val: float, min_: float, max_: float) -> float:
    """
    :param val: значение
    :param min_: минимальная граница
    :param max_: максимальная граница
    :return: возвращает указанное значение val в границах от min до max
    """
    if val < min_:
        return min_
    if val > max_:
        return max_
    return val


@fast_math
def dec_to_rad_pt(x: float, y: float) -> Tuple[float, float]:
    """
    Переводи пару координат из декартовой системы в полярную.\n
    :param x: x - координата.
    :param y: y - координата.
    :return: координаты rho и phi в полярной системе.
    """
    return np.sqrt(x * x + y * y), np.arctan2(y, x)


@fast_math
def rad_to_dec_pt(rho: float, phi: float) -> Tuple[float, float]:
    """
    Переводи пару координат из полярной системы в декартову.\n
    :param rho: rho - радиус.
    :param phi: phi - угол.
    :return:  координаты x и y в декартову системе.
    """
    return rho * np.cos(phi), rho * np.sin(phi)


@parallel
def dec_to_rad(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Переводи пару массивов координат из декартовой системы в полярную.\n
    :param x: x - массив координат.
    :param y: y - массив координат.
    :return: массивы координат rho и phi в полярной системе.
    """
    if x.size != y.size:
        raise ValueError("dec_to_rad :: x.size != y.size")
    if x.ndim != y.ndim:
        raise ValueError("dec_to_rad :: x.ndim != y.ndim")

    if x.ndim == 2:
        rows, cols = x.shape
        if x.ndim == 2:
            for i in parallel_range(rows):
                for j in range(cols):
                    x[i, j], y[i, j] = dec_to_rad_pt(x[i, j], y[i, j])
        return x, y

    if x.ndim == 1:
        for i in parallel_range(x.shape[0]):
            x[i], y[i] = dec_to_rad_pt(x[i], y[i])
        return x, y

    raise ValueError("dec_to_rad :: x and y has to be 1 or 2 dimensional")


@parallel
def rad_to_dec(rho: np.ndarray, phi: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Переводи пару массивов координат из полярной системы в декартову.\n
    :param rho: rho - массив радиусов.
    :param phi: phi - массив углов.
    :return: массивы координат x и y в декартову системе.
    """
    if rho.size != phi.size:
        raise Exception("rad_to_dec :: rho.size != phi.size")

    if rho.ndim != phi.ndim:
        raise Exception("rad_to_dec :: rho.ndim != phi.ndim")

    if rho.ndim == 2:
        rows, cols = rho.shape
        for i in parallel_range(rows):
            for j in range(cols):
                rho[i, j], phi[i, j] = rad_to_dec_pt(rho[i, j], phi[i, j])
        return rho, phi

    if rho.ndim == 1:
        for i in parallel_range(rho.shape[0]):
            rho[i], phi[i] = rad_to_dec_pt(rho[i], phi[i])
        return rho, phi

    raise Exception("rad_to_dec :: rho and phi has to be 1 or 2 dimensional")


@fast_math
def compute_derivatives_2_at_pt(points: np.ndarray, row: int, col: int) -> Tuple[float, float, float]:
    """
    Вычисляет производные по х, по y и по xy. Используется центральный разностный аналог
    :param points: двумерный список узловых точек
    :param row: индекс строки точки из points для которой считаем производные
    :param col: индекс столбца точки из points для которой считаем производные
    :return: (df/dx, df/dy, df/dx/dy)
    """
    if points.ndim != 2:
        raise RuntimeError("compute_derivatives_2_at_pt :: points array has to be 2 dimensional")

    rows, colons = points.shape

    if not _in_range(row, 0, rows - 1):
        return 0.0, 0.0, 0.0

    if not _in_range(col, 0, colons - 1):
        return 0.0, 0.0, 0.0

    row_1 =  min(rows - 1, row + 1)
    row_0 =  max(0, row - 1)

    col_1 = min(colons - 1, col + 1)
    col_0 = max(0, col - 1)

    return (points[row,   col_1] - points[row, col_0]) * 0.5, \
           (points[row_1, col]   - points[row_0, col]) * 0.5, \
           (points[row_1, col_1] - points[row_1, col_0]) * 0.25 - \
           (points[row_0, col_1] - points[row_0, col_0]) * 0.25


@fast_math
def compute_derivatives_at_pt(points: np.ndarray, row: int, col: int) -> Tuple[float, float]:
    """
    Вычисляет производные по х, по y. Используется центральный разностный аналог
    :param points: двумерный список узловых точек.
    :param row: индекс строки точки из points для которой считаем производные.
    :param col: индекс столбца точки из points для которой считаем производные.
    :return: (df/dx, df/dy, df/dx/dy)
    """
    if points.ndim != 2:
        raise RuntimeError("compute_derivatives_at_pt :: points array has to be 2 dimensional")

    rows, colons = points.shape

    if not _in_range(row, 0, rows - 1):
        return 0.0, 0.0

    if not _in_range(col, 0, colons - 1):
        return 0.0, 0.0

    row_1 =  min(rows - 1, row + 1)
    row_0 =  max(0, row - 1)

    col_1 = min(colons - 1, col + 1)
    col_0 = max(0, col - 1)

    return (points[row, col_1] - points[row, col_0]) * 0.5, \
           (points[row_1, col] - points[row_0, col]) * 0.5


@parallel
def compute_derivatives_2(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Вычисляет производные по х, по y и по xy. Используется центральный разностный аналог
    :param points: двумерный список узловых точек
    :return: (df/dx, df/dy, df/dx/dy), каждый элемент np.ndarray
    """
    if points.ndim != 2:
        raise RuntimeError("compute_derivatives_2 :: points array has to be 2 dimensional")

    rows, colons = points.shape

    points_dx = np.zeros_like(points)
    points_dy = np.zeros_like(points)
    points_dxy = np.zeros_like(points)

    for i in parallel_range(points.size):
        row_, col_ = divmod(i, colons)

        row_1 = min(rows - 1, row_ + 1)
        row_0 = max(0, row_ - 1)

        col_1 = min(colons - 1, col_ + 1)
        col_0 = max(0, col_ - 1)

        points_dx[row_, col_] = (points[row_, col_1] - points[row_, col_0]) * 0.5

        points_dy[row_, col_] = (points[row_1, col_] - points[row_0, col_]) * 0.5

        dx_1 = (points[row_1, col_1] -
                points[row_1, col_0]) * 0.25
        dx_2 = (points[row_0, col_1] -
                points[row_0, col_0]) * 0.25
        points_dxy[row_, col_] = (dx_2 - dx_1)

    return points_dx, points_dy, points_dxy


@parallel
def compute_derivatives(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Вычисляет производные по х, по y и по xy. Используется центральный разностный аналог
    :param points: двумерный список узловых точек
    :return: (df/dx, df/dy), каждый элемент np.ndarray
    """
    if points.ndim != 2:
        raise RuntimeError("compute_derivatives_2 :: points array has to be 2 dimensional")

    rows, colons = points.shape

    points_dx = np.zeros_like(points)
    points_dy = np.zeros_like(points)

    for i in parallel_range(points.size):
        row_, col_ = divmod(i, colons)

        row_1 = min(rows - 1, row_ + 1)
        row_0 = max(0, row_ - 1)

        col_1 = min(colons - 1, col_ + 1)
        col_0 = max(0, col_ - 1)

        points_dx[row_, col_] = (points[row_, col_1] - points[row_, col_0]) * 0.5

        points_dy[row_, col_] = (points[row_1, col_] - points[row_0, col_]) * 0.5

    return points_dx, points_dy


@parallel
def compute_normals(points: np.ndarray) -> np.ndarray:
    if points.ndim != 2:
        raise RuntimeError("compute_derivatives_2 :: points array has to be 2 dimensional")

    rows, cols = points.shape

    points_n = np.zeros((rows, cols, 3,), dtype=float)

    for i in parallel_range(points.size):
        row_, col_ = divmod(i, cols)

        row_1 = min(rows - 1, row_ + 1)
        row_0 = max(0, row_ - 1)

        col_1 = min(cols - 1, col_ + 1)
        col_0 = max(0, col_ - 1)

        _dx = (points[row_, col_1] - points[row_, col_0]) * 0.5

        _dy = (points[row_1, col_] - points[row_0, col_]) * 0.5

        _rho = np.sqrt(1.0 + _dx * _dx + _dy * _dy)

        points_n[row_, col_, 0] = _dx / _rho

        points_n[row_, col_, 1] = _dy / _rho

        points_n[row_, col_, 2] = 1.0 / _rho

    return points_n
