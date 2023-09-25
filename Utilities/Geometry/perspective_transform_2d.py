from .vector3 import Vector3
from .matrix3 import Matrix3
from .vector2 import Vector2
from typing import List
import numpy as np
import math


class PerspectiveTransform2d:
    __slots__ = "_t_m", "_i_t_m"

    def __init__(self, matrix: Matrix3 = None):
        if matrix is None:
            self._t_m: Matrix3 = Matrix3(1.0, 0.0, 0.0,
                                         0.0, 1.0, 0.0,
                                         0.0, 0.0, 1.0)
            self._i_t_m: Matrix3 = Matrix3(1.0, 0.0, 0.0,
                                           0.0, 1.0, 0.0,
                                           0.0, 0.0, 1.0)
            return
        assert isinstance(matrix, Matrix3)
        self._t_m: Matrix3 = matrix
        self._i_t_m: Matrix3 = matrix.invert()

    def __str__(self) -> str:
        return f"{{\n" \
               f"\"transform\"    :\n{self.transform_matrix},\n" \
               f"\"inv_transform\":\n{self.inv_transform_matrix}\n" \
               f"}}"

    def _update_invert_transform(self):
        self._i_t_m = self._t_m.invert()

    @property
    def transform_matrix(self) -> Matrix3:
        return self._t_m

    @property
    def inv_transform_matrix(self) -> Matrix3:
        return self._i_t_m

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
        self._update_invert_transform()

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
        self._update_invert_transform()

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
        self._update_invert_transform()

    @property
    def right(self) -> Vector2:
        return Vector2(self._t_m.m00, self._t_m.m10) / self.scale_x

    @right.setter
    def right(self, value: Vector2) -> None:
        assert isinstance(value, Vector2)
        self._t_m = Matrix3(value.x,       self._t_m.m01, self._t_m.m02,
                            value.y,       self._t_m.m11, self._t_m.m12,
                            self._t_m.m20, self._t_m.m21, self._t_m.m22)
        self._update_invert_transform()

    @property
    def up(self) -> Vector2:
        return Vector2(self._t_m.m01, self._t_m.m11) / self.scale_y

    @up.setter
    def up(self, value: Vector2) -> None:
        assert isinstance(value, Vector2)
        self._t_m = Matrix3(self._t_m.m00, value.x,       self._t_m.m02,
                            self._t_m.m10, value.y,       self._t_m.m12,
                            self._t_m.m20, self._t_m.m21, self._t_m.m22)
        self._update_invert_transform()

    @property
    def center_x(self) -> float:
        return self._t_m.m02

    @center_x.setter
    def center_x(self, value: float) -> None:
        assert isinstance(value, float)
        self._t_m = Matrix3(self._t_m.m00, self._t_m.m01, value,
                            self._t_m.m10, self._t_m.m11, self._t_m.m12,
                            self._t_m.m20, self._t_m.m21, self._t_m.m22)
        self._update_invert_transform()

    @property
    def center_y(self) -> float:
        return self._t_m.m12

    @center_y.setter
    def center_y(self, value: float) -> None:
        assert isinstance(value, float)
        self._t_m = Matrix3(self._t_m.m00, self._t_m.m01, self._t_m.m02,
                            self._t_m.m10, self._t_m.m11, value,
                            self._t_m.m20, self._t_m.m21, self._t_m.m22)
        self._update_invert_transform()

    @property
    def center(self) -> Vector2:
        return Vector2(self.center_x, self.center_y)

    @center.setter
    def center(self, value: Vector2) -> None:
        assert isinstance(value, Vector2)
        self._t_m = Matrix3(self._t_m.m00, self._t_m.m01, value.x,
                            self._t_m.m10, self._t_m.m11, value.y,
                            self._t_m.m20, self._t_m.m21, self._t_m.m22)
        self._update_invert_transform()

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
        self._update_invert_transform()

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
        self._update_invert_transform()

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
        self._update_invert_transform()

    # @staticmethod
    # def _transform_pt(transform_matrix: Matrix3, point: Vector2) -> Vector2:
    #     p = transform_matrix * Vector3(point.x, point.y, 1.0)
    #     return Vector2(p.x / p.z, p.y / p.z)

    def transform_point(self, point: Vector2) -> Vector2:
        assert isinstance(point, Vector2)
        return Matrix3.perspective_multiply(self.transform_matrix, point)

    def transform_points(self, points: List[Vector2]) -> List[Vector2]:
        return [self.transform_point(p) for p in points]

    def inv_transform_point(self, point: Vector2) -> Vector2:
        assert isinstance(point, Vector2)
        return Matrix3.perspective_multiply(self.inv_transform_matrix, point)

    def inv_transform_points(self, points: List[Vector2]) -> List[Vector2]:
        return [self.inv_transform_point(p) for p in points]

    @classmethod
    def from_four_points(cls, *args):
        return cls(Matrix3.perspective_transform_from_four_points(*args))

    @classmethod
    def from_eight_points(cls, *args):
        return cls(Matrix3.perspective_transform_from_eight_points(*args))
