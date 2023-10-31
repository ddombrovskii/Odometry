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
    assert x.size == y.size, "fuck yo, Tony!"
    sum_x = x.sum()
    sum_y = y.sum()
    sum_xy = np.dot(x, y)
    sum_xx = np.dot(x, x)
    inv_n = 1.0 / x.size
    k = (sum_xy - sum_x * sum_y * inv_n) / (sum_xx - sum_x * sum_x * inv_n)
    return k, (sum_y - k * sum_x) * inv_n


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
    assert x.size == y.size, "fuck yo, Tony!"
    assert x.size == z.size, "fuck yo, Tony!"

    sum_x = x.sum()
    sum_y = y.sum()
    sum_z = z.sum()
    sum_xy = (x * y).sum()
    sum_xx = (x * x).sum()
    sum_yy = (y * y).sum()
    sum_zy = (z * y).sum()
    sum_zx = (x * z).sum()

    hess = np.array([[sum_xx, sum_xy, sum_x],
                     [sum_xy, sum_yy, sum_y],
                     [sum_x, sum_y, x.size]])
    grad =  np.array([sum_xx + sum_xy - sum_zx,
                      sum_xy + sum_yy - sum_zy,
                      sum_x + sum_y - sum_z])
    try:
        return tuple(np.array([1.0, 1.0, 0.0]) - np.linalg.inv(hess) @ grad)
    except LinAlgError as err:
        print(err.args)
        return 0.0, 0.0, 0.0


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
    assert x.size == y.size, "fuck yo, Tony!"
    a_m = np.zeros((order, order,), dtype=float)
    c_m = np.zeros((order,), dtype=float)
    _x_row = np.ones_like(x)
    for row in range(order):
        _x_row = _x_row * x if row != 0 else _x_row
        c_m[row] = np.dot(_x_row, y)
        _x_col = np.ones_like(x)
        for col in range(row + 1):
            _x_col = _x_col * x if col != 0 else _x_col
            a_m[col, row] = a_m[row, col] = np.dot(_x_col, _x_row)
    try:
        return np.linalg.inv(a_m) @ c_m
    except LinAlgError as err:
        print(err.args)
        return np.array(linear_regression(x, y))


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
    n_points, n_dimension = data_rows.shape
    assert n_dimension != 1, "fuck you, Tony!!!"
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


def quadratic_regression_2d(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
    assert x.size == y.size, "fuck you, Tony!"
    assert x.size == z.size, "fuck you, Tony!"
    b = (x * x, x * y, y * y, x, y, np.array([1.0]))
    a_m = np.zeros((6, 6), dtype=float)
    b_c = np.zeros((6,), dtype=float)
    for row in range(6):
        b_c[row] = np.dot(b[row] * z)
        for col in range(row + 1):
            a_m[col, row] = a_m[row, col] = np.dot(b[row], b[col])
    a_m[-1, -1] = x.size  # костыль, который я не придумал как убрать
    try:
        return np.linalg.inv(a_m) @ b_c
    except LinAlgError as err:
        print(err.args)
        return np.array(bi_linear_regression(x, y, z))


def second_order_surface(x: np.ndarray, y: np.ndarray, args: np.ndarray) -> np.ndarray:
    assert x.shape == y.shape
    assert args.size == 6
    return args[0] * x * x + args[1] * x * y + args[2] * y * y + args[3] * x + args[4] * y + args[5]


def second_order_surface_fit(y: np.ndarray, x: np.ndarray,
                             x_points: np.ndarray,
                             y_points: np.ndarray,
                             z_points: np.ndarray) -> np.ndarray:
    fit_params = quadratic_regression_2d(x_points, y_points, z_points)
    if fit_params.size == 3:
        return fit_params[0] * x + fit_params[1] * y + fit_params[2]
    return second_order_surface(x, y, fit_params)
