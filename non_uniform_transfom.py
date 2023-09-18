import math

from Utilities.Geometry import Matrix3, Vector3, Vector2
from matplotlib import pyplot as plt
import numpy as np
# система уравнений для определения параметров матрицы искажения:
# пусть у нас есть 4 точки на поверхности земли. Координаты каждой из этих точек соответствуют
# координатам пересечения лучей совпадающих с рёбрами пирамиды видимости камеры
# {p_x, p_y} - координаты мира
# {c_x, c_y} - координаты камеры, которые представляются собой попарный набор из следующих значений:
# {1.0, 1.0} | {1.0, -1.0} | {-1.0, -1.0} | {-1.0, 1.0}
# Система уравнений буде состоять из четырёх пар вида:
# p_x = m00 * c_x + m01 * c_y - p_x * c_x * m20 - p_x * c_y * m21 + m02
# p_y = m10 * c_x + m11 * c_y - p_y * c_x * m20 - p_y * c_y * m21 + m12
# итого система уравнений состоит из блоков вида:
# m00 | m01 | m02 | m10 | m11 | m12 |     m20    |     m21    |
# c_x | c_y |  1  |  0  |  0  |  0  | -p_x * c_x | -p_x * c_y |
#  0  |  0  |  0  | c_x | c_y |  1  | -p_y * c_x | -p_y * c_y |
# окончательно:
#  m00 | m01 | m02 | m10 | m11 | m12 |  m20 |  m21 |

#  1.0 | 1.0 | 1.0 |  0  |  0  |  0  | -p_x | -p_x |
#   0  |  0  |  0  | 1.0 | 1.0 | 1.0 | -p_y | -p_y |

#  1.0 |-1.0 | 1.0 |  0  |  0  |  0  | -p_x |  p_x |
#   0  |  0  |  0  | 1.0 |-1.0 | 1.0 | -p_y |  p_y |

# -1.0 |-1.0 | 1.0 |  0  |  0  |  0  |  p_x |  p_x |
#   0  |  0  |  0  |-1.0 |-1.0 | 1.0 |  p_y |  p_y |

# -1.0 | 1.0 | 1.0 |  0  |  0  |  0  |  p_x | -p_x |
#   0  |  0  |  0  |-1.0 | 1.0 | 1.0 |  p_y | -p_y |


def build_matrix_transform_matrix(ur: Vector2, dr: Vector2, dl: Vector2, ul: Vector2):
    """
    param: ur: up right point
    param: dr: down right point
    param: dl: down left point
    param: ul: up left point
    """
    matrix = (1.0,  1.0, 1.0,  0.0,  0.0, 0.0, -ur.x, -ur.x,
              0.0,  0.0, 0.0,  1.0,  1.0, 1.0, -ur.y, -ur.y,
              1.0, -1.0, 1.0,  0.0,  0.0, 0.0, -dr.x,  dr.x,
              0.0,  0.0, 0.0,  1.0, -1.0, 1.0, -dr.y,  dr.y,
             -1.0, -1.0, 1.0,  0.0,  0.0, 0.0,  dl.x,  dl.x,
              0.0,  0.0, 0.0, -1.0, -1.0, 1.0,  dl.y,  dl.y,
             -1.0,  1.0, 1.0,  0.0,  0.0, 0.0,  ul.x, -ul.x,
              0.0,  0.0, 0.0, -1.0,  1.0, 1.0,  ul.y, -ul.y)
    b = np.array((ur.x, ur.y, dr.x, dr.y, dl.x, dl.y, ul.x, ul.y))
    matrix = np.array(matrix).reshape((8, 8))
    return Matrix3(*(np.linalg.inv(matrix) @ b).flat, 1.0)


class PerspectiveTransform2d:
    def __init__(self, matrix: Matrix3 = None):
        if matrix is None:
            self._t_m: Matrix3 = Matrix3(1.0, 0.0, 0.0,
                                         0.0, 1.0, 0.0,
                                         0.0, 0.0, 1.0)
            return
        assert isinstance(matrix, Matrix3)
        self._t_m: Matrix3 = matrix

    @property
    def scale_x(self) -> float:
        return math.sqrt(self._t_m.m00 ** 2 + self._t_m.m10 ** 2)

    @scale_x.setter
    def scale_x(self, value: float) -> None:
        assert isinstance(value, float)
        assert value != 0.0
        new_scl = value / self.scale_x
        self._t_m = Matrix3(self._t_m.m00 * new_scl, self._t_m.m01, self._t_m.m02,
                            self._t_m.m10 * new_scl, self._t_m.m11, self._t_m.m12,
                            self._t_m.m20,           self._t_m.m21, self._t_m.m22)

    @property
    def scale_y(self) -> float:
        return math.sqrt(self._t_m.m01 ** 2 + self._t_m.m11 ** 2)

    @scale_y.setter
    def scale_y(self, value: float) -> None:
        assert isinstance(value, float)
        assert value != 0.0
        new_scl = value / self.scale_y
        self._t_m = Matrix3(self._t_m.m00, self._t_m.m01 * new_scl, self._t_m.m02,
                            self._t_m.m10, self._t_m.m11 * new_scl, self._t_m.m12,
                            self._t_m.m20, self._t_m.m21,           self._t_m.m22)

    @property
    def scale(self) -> Vector2:
        return Vector2(self.scale_x, self.scale_y)

    @scale.setter
    def scale(self, value: Vector2) -> None:
        assert isinstance(value, Vector2)
        new_scl_x = value.x / self.scale_x
        new_scl_y = value.y / self.scale_y
        self._t_m = Matrix3(self._t_m.m00 * new_scl_x, self._t_m.m01 * new_scl_y, self._t_m.m02,
                            self._t_m.m10 * new_scl_x, self._t_m.m11 * new_scl_y, self._t_m.m12,
                            self._t_m.m20,             self._t_m.m21,             self._t_m.m22)

    @property
    def right(self) -> Vector2:
        return Vector2(self._t_m.m00, self._t_m.m10) / self.scale_x

    @right.setter
    def right(self, value: Vector2) -> None:
        assert isinstance(value, Vector2)
        self._t_m = Matrix3(value.x,       self._t_m.m01, self._t_m.m02,
                            value.y,       self._t_m.m11, self._t_m.m12,
                            self._t_m.m20, self._t_m.m21, self._t_m.m22)

    @property
    def up(self) -> Vector2:
        return Vector2(self._t_m.m01, self._t_m.m11) / self.scale_y

    @up.setter
    def up(self, value: Vector2) -> None:
        assert isinstance(value, Vector2)
        self._t_m = Matrix3(self._t_m.m00, value.x,       self._t_m.m02,
                            self._t_m.m10, value.y,       self._t_m.m12,
                            self._t_m.m20, self._t_m.m21, self._t_m.m22)

    @property
    def center_x(self) -> float:
        return self._t_m.m02

    @center_x.setter
    def center_x(self, value: float) -> None:
        assert isinstance(value, float)
        self._t_m = Matrix3(self._t_m.m00, self._t_m.m01, value,
                            self._t_m.m10, self._t_m.m11, self._t_m.m12,
                            self._t_m.m20, self._t_m.m21, self._t_m.m22)

    @property
    def center_y(self) -> float:
        return self._t_m.m12

    @center_y.setter
    def center_y(self, value: float) -> None:
        assert isinstance(value, float)
        self._t_m = Matrix3(self._t_m.m00, self._t_m.m01, self._t_m.m02,
                            self._t_m.m10, self._t_m.m11, value,
                            self._t_m.m20, self._t_m.m21, self._t_m.m22)

    @property
    def center(self) -> Vector2:
        return Vector2(self.center_x, self.center_y)

    @center.setter
    def center(self, value: Vector2) -> None:
        assert isinstance(value, Vector2)
        self._t_m = Matrix3(self._t_m.m00, self._t_m.m01, value.x,
                            self._t_m.m10, self._t_m.m11, value.y,
                            self._t_m.m20, self._t_m.m21, self._t_m.m22)

    @property
    def expand_x(self) -> float:
        return 1.0 / (1.0 - self._t_m.m20) if self._t_m.m20 > 0 else -1.0 / (1.0 + self._t_m.m20)

    @expand_x.setter
    def expand_x(self, value: float) -> None:
        assert isinstance(value, float)
        self._t_m = Matrix3(self._t_m.m00, self._t_m.m01, self._t_m.m02,
                            self._t_m.m10, self._t_m.m11, self._t_m.m12,
                            (1.0 - 1.0 / value if value > 0 else -1.0 - 1.0 / value),
                            self._t_m.m21, self._t_m.m22)

    @property
    def expand_y(self) -> float:
        return 1.0 / (1.0 - self._t_m.m21) if self._t_m.m21 > 0 else -1.0 / (1.0 + self._t_m.m21)

    @expand_y.setter
    def expand_y(self, value: float) -> None:
        assert isinstance(value, float)
        self._t_m = Matrix3(self._t_m.m00, self._t_m.m01, self._t_m.m02,
                            self._t_m.m10, self._t_m.m11, self._t_m.m12,
                            self._t_m.m20, (1.0 - 1.0 / value if value > 0 else -1.0 - 1.0 / value),
                            self._t_m.m22)

    @property
    def expand(self) -> Vector2:
        return Vector2(self.expand_x, self.expand_y)

    @expand.setter
    def expand(self, value: Vector2) -> None:
        assert isinstance(value, Vector2)
        self._t_m = Matrix3(self._t_m.m00, self._t_m.m01, self._t_m.m02,
                            self._t_m.m10, self._t_m.m11, self._t_m.m12,
                            (1.0 - 1.0 / value.x if value.x > 0 else -1.0 - 1.0 / value.x),
                            (1.0 - 1.0 / value.y if value.y > 0 else -1.0 - 1.0 / value.y),
                            self._t_m.m22)

    @classmethod
    def from_four_points(cls, ur: Vector2, dr: Vector2, dl: Vector2, ul: Vector2):
        assert isinstance(ur, Vector2)
        assert isinstance(dr, Vector2)
        assert isinstance(dl, Vector2)
        assert isinstance(ul, Vector2)
        matrix = (1.0, 1.0, 1.0, 0.0, 0.0, 0.0, -ur.x, -ur.x,
                  0.0, 0.0, 0.0, 1.0, 1.0, 1.0, -ur.y, -ur.y,
                  1.0, -1.0, 1.0, 0.0, 0.0, 0.0, -dr.x, dr.x,
                  0.0, 0.0, 0.0, 1.0, -1.0, 1.0, -dr.y, dr.y,
                  -1.0, -1.0, 1.0, 0.0, 0.0, 0.0, dl.x, dl.x,
                  0.0, 0.0, 0.0, -1.0, -1.0, 1.0, dl.y, dl.y,
                  -1.0, 1.0, 1.0, 0.0, 0.0, 0.0, ul.x, -ul.x,
                  0.0, 0.0, 0.0, -1.0, 1.0, 1.0, ul.y, -ul.y)
        b = np.array((ur.x, ur.y, dr.x, dr.y, dl.x, dl.y, ul.x, ul.y))
        matrix = np.array(matrix).reshape((8, 8))
        return cls(Matrix3(*(np.linalg.inv(matrix) @ b).flat, 1.0))


# transform = Matrix3(1.0,  0.4, -0.120,
#                     0.1,  1.0,   0.50,
#                    -0.25, 0.125, 1.0)

transform = Matrix3(1.0, 0.0, 0.0,
                    0.0, 1.0, 0.0,
                    0.99, 0.0, 1.0)

transform_inv = transform.invert()
print(f"original transform:\n{transform}")
# print()
# print(f"inverse of transform:\n{transform_inv}")

x_points = 13
y_points = 13

# ur = Vector3(1.4629, 1.8286, 1.0)  # (1, 1)
# dr = Vector3(0.768, -0.64, 1.0)  # (1, -1)
# dl = Vector3(-1.3511, -0.5333, 1.0)  # (-1, -1)
# ul = Vector3(-0.5236, 1.0182, 1.0)  # (-1, 1)
points_labels = ('ur', 'dr', 'dl', 'ul')
points = (Vector3(1.4629, 1.8286, 1.0),
          Vector3(0.768, -0.64, 1.0),
          Vector3(-1.3511, -0.5333, 1.0),
          Vector3(-0.5236, 1.0182, 1.0))


tt = build_matrix_transform_matrix(*points)
itt = tt.invert()
print(f"points based transform:\n{tt}")
print(f"invert points based transform:\n{itt}")
for pl, p in zip(points_labels, points):
    p = itt * p
    p /= p.z
    print(f"{pl} : {p}")


positions = [Vector3((row / (y_points - 1)  - 0.5) * 2.0, (col /  (x_points - 1) - 0.5) * 2.0, 1.0)
             for col in range(y_points) for row in range(x_points)]

positions_transformed = [transform * position for position in positions]
positions_transformed = [v / v.z for v in positions_transformed]
# print(positions)
# print(positions_transformed)
positions_inv_transformed = [tt * position for position in positions]
positions_inv_transformed = [v / v.z for v in positions_inv_transformed]
# for p1, p2 in zip(positions, positions_transformed):
#     print(f"{p1}\t{p2}")

x_points = np.array([v.x for v in positions])
y_points = np.array([v.y for v in positions])

x_points_transformed = np.array([v.x for v in positions_transformed])
y_points_transformed = np.array([v.y for v in positions_transformed])

x_points_inv_transformed = np.array([v.x for v in positions_inv_transformed])
y_points_inv_transformed = np.array([v.y for v in positions_inv_transformed])

fig, axs = plt.subplots(1)
axs.plot(x_points, y_points, '*r')
axs.plot(x_points_transformed, y_points_transformed, '.b')
axs.set_aspect('equal', 'box')
# plt.plot(x_points_inv_transformed, y_points_inv_transformed, 'og')
plt.show()

p = (0.8077369, 0.02835679, 0.8077369)

print(sum(pi**2 for pi in p))