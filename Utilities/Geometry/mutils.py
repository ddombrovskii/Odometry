from numpy.linalg import LinAlgError
from typing import Tuple
import numpy as np


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
    sum_x = x.sum()
    sum_y = y.sum()
    sum_xy = (x * y).sum()
    sum_xx = (x * x).sum()
    n = x.size
    k = (sum_xy - sum_x * sum_y / n) / (sum_xx - sum_x * sum_x / n)
    return k, (sum_y - k * sum_x) / n


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
    a_m = np.zeros((order, order,), dtype=float)
    c_m = np.zeros((order,), dtype=float)
    _x_row = None
    for row in range(order):
        _x_col = None
        _x_row = np.ones_like(x) if _x_row is None else _x_row * x
        c_m[row] = (_x_row * y).sum()
        for col in range(row + 1):
            _x_col = np.ones_like(x) if _x_col is None else _x_col * x
            a_m[row, col] = (_x_col * _x_row).sum()
            a_m[col, row] = a_m[row, col]
    try:
        return np.linalg.inv(a_m) @ c_m
    except LinAlgError as err:
        print(err.args)
        result = np.zeros((order,), dtype=float)
        result[0], result[1] = linear_regression(x, y)
        return result


def poly_fit(x: np.ndarray, x_points: np.ndarray, y_points: np.ndarray, order: int = 16) -> np.ndarray:
    return polynom(x, poly_regression(x_points, y_points, order))


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
    s_rows, s_cols = data_rows.shape

    hessian = np.zeros((s_cols, s_cols,), dtype=float)

    grad = np.zeros((s_cols,), dtype=float)

    x_0 = np.zeros((s_cols,), dtype=float)

    s_cols -= 1

    for row in range(s_cols):
        x_0[row] = 1.0
        for col in range(row + 1):
            hessian[row, col] = np.dot(data_rows[:, row], data_rows[:, col])
            hessian[col, row] = hessian[row, col]

    for i in range(s_cols + 1):
        hessian[i, s_cols] = (data_rows[:, i]).sum()
        hessian[s_cols, i] = hessian[i, s_cols]

    hessian[s_cols, s_cols] = data_rows.shape[0]

    for row in range(s_cols):
        grad[row] = hessian[row, 0: s_cols].sum() - np.dot(data_rows[:, s_cols], data_rows[:, row])

    grad[s_cols] = hessian[s_cols, 0: s_cols].sum() - data_rows[:, s_cols].sum()

    return x_0 - np.linalg.inv(hessian) @ grad


def quadratic_regression_2d(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
    b = (x * x, x * y, y * y, x, y, np.array([1.0]))
    a_m = np.zeros((6, 6), dtype=float)
    b_c = np.zeros((6,), dtype=float)
    for row in range(6):
        b_c[row] = (b[row] * z).sum()
        for col in range(row + 1):
            a_m[row][col] = (b[row] * b[col]).sum()
            a_m[col][row] = a_m[row][col]
    a_m[5][5] = x.size  # костыль, который я не придумал как убрать
    return np.linalg.inv(a_m) @ b_c
