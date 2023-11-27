from .common import NUMERICAL_FORMAT_4F as _4F, DEG_TO_RAD, NUMERICAL_ACCURACY, indent
from dataclasses import dataclass
from .vector3 import Vector3
from .vector2 import Vector2
from typing import Tuple
import numpy as np
import math


@dataclass
class Matrix3:
    """
    mutable Matrix 3d
    """

    __slots__ = ('_m00', '_m01', '_m02',
                 '_m10', '_m11', '_m12',
                 '_m20', '_m21', '_m22')

    # row 0 getters
    @property
    def m00(self) -> float:
        return self._m00

    @property
    def m01(self) -> float:
        return self._m01

    @property
    def m02(self) -> float:
        return self._m02

    # row 1 getters
    @property
    def m10(self) -> float:
        return self._m10

    @property
    def m11(self) -> float:
        return self._m11

    @property
    def m12(self) -> float:
        return self._m12

    # row 2 getters
    @property
    def m20(self) -> float:
        return self._m20

    @property
    def m21(self) -> float:
        return self._m21

    @property
    def m22(self) -> float:
        return self._m22

    # row 0 getters
    @m00.setter
    def m00(self, value: float) -> None:
        self._m00 = float(value)

    @m01.setter
    def m01(self, value: float) -> None:
        self._m01 = float(value)

    @m02.setter
    def m02(self, value: float) -> None:
        self._m02 = float(value)

    # row 1 getters
    @m10.setter
    def m10(self, value: float) -> None:
        self._m10 = float(value)

    @m11.setter
    def m11(self, value: float) -> None:
        self._m11 = float(value)

    @m12.setter
    def m12(self, value: float) -> None:
        self._m12 = float(value)

    # row 2 getters
    @m20.setter
    def m20(self, value: float) -> None:
        self._m20 = float(value)

    @m21.setter
    def m21(self, value: float) -> None:
        self._m21 = float(value)

    @m22.setter
    def m22(self, value: float) -> None:
        self._m22 = float(value)

    def __init__(self, *args):
        assert len(args) == 9
        self._m00 = args[0]
        self._m01 = args[1]
        self._m02 = args[2]

        self._m10 = args[3]
        self._m11 = args[4]
        self._m12 = args[5]

        self._m20 = args[6]
        self._m21 = args[7]
        self._m22 = args[8]

    def __iter__(self):
        yield self._m00
        yield self._m01
        yield self._m02

        yield self._m10
        yield self._m11
        yield self._m12

        yield self._m20
        yield self._m21
        yield self._m22

    def __eq__(self, other):
        if not isinstance(other, Matrix3):
            return False
        return not any(v1 != v2 for v1, v2 in zip(self, other))

    @classmethod
    def identity(cls):
        return cls(1.0, 0.0, 0.0,
                   0.0, 1.0, 0.0,
                   0.0, 0.0, 1.0)

    @classmethod
    def zeros(cls):
        return cls(0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0)

    @classmethod
    def rotate_x(cls, angle: float, angle_in_rad: bool = True):
        if not angle_in_rad:
            angle *= DEG_TO_RAD
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return cls(1.0, 0.0, 0.0,
                   0.0, cos_a, -sin_a,
                   0.0, sin_a, cos_a)

    @classmethod
    def rotate_y(cls, angle: float, angle_in_rad: bool = True):
        if not angle_in_rad:
            angle *= DEG_TO_RAD
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return cls(cos_a, 0.0, sin_a,
                   0.0, 1.0, 0.0,
                   -sin_a, 0.0, cos_a)

    @classmethod
    def rotate_z(cls, angle: float, angle_in_rad: bool = True):
        if not angle_in_rad:
            angle *= DEG_TO_RAD
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return cls(cos_a, -sin_a, 0.0,
                   sin_a, cos_a, 0.0,
                   0.0, 0.0, 1.0)

    @classmethod
    def rotate_xyz(cls, angle_x: float, angle_y: float, angle_z: float, angle_in_rad: bool = True):
        return cls.rotate_x(angle_x, angle_in_rad) * \
               cls.rotate_y(angle_y, angle_in_rad) * \
               cls.rotate_z(angle_z, angle_in_rad)

    @classmethod
    def rotate_zyx(cls, angle_x: float, angle_y: float, angle_z: float, angle_in_rad: bool = True):
        return cls.rotate_z(angle_z, angle_in_rad) * \
               cls.rotate_y(angle_y, angle_in_rad) * \
               cls.rotate_x(angle_x, angle_in_rad)

    @classmethod
    def build_basis(cls, ey: Vector3, ez: Vector3 = None):
        assert isinstance(ey, Vector2)
        if ez is None:
            ez = Vector3(0.0, 0.0, 1.0)
        assert isinstance(ez, Vector2)
        ey = ey.normalized
        ez = ez.normalized
        ex = Vector3.cross(ez, ey).normalize()
        ez = Vector3.cross(ey, ex).normalize()

        return cls(ex.x, ey.x, ez.x,
                   ex.y, ey.y, ez.y,
                   ex.z, ey.z, ez.z)

    @classmethod
    def from_np_array(cls, array: np.ndarray):
        assert isinstance(array, np.ndarray)
        assert array.size == 9
        return cls(*array.flat)

    @classmethod
    def translate(cls, position: Vector2):
        assert isinstance(position, Vector2)
        return cls(1.0, 0.0, position.x,
                   0.0, 1.0, position.y,
                   0.0, 0.0, 1.0)

    @classmethod
    def build_transform(cls, right: Vector3, up: Vector3, front: Vector3):
        """
        -- НЕ ПРОВЕРЯЕТ ОРТОГОНАЛЬНОСТЬ front, up, right !!!
        :param front:
        :param up:
        :param right:
        :return:
        """
        return cls(right.x, up.x, front.x,
                   right.y, up.y, front.y,
                   right.z, up.z, front.z)

    def to_euler_angles(self) -> Vector3:
        """
        :return: углы поворота по осям
        """
        if math.fabs(self.m20 + 1.0) < NUMERICAL_ACCURACY:
            return Vector3(0.0, math.pi * 0.5, math.atan2(self.m01, self.m02))

        if math.fabs(self.m20 - 1.0) < NUMERICAL_ACCURACY:
            return Vector3(0.0, -math.pi * 0.5, math.atan2(-self.m01, -self.m02))

        x1 = -math.asin(self.m20)
        inv_cos_x1 = 1.0 / math.cos(x1)
        x2 = math.pi + x1
        inv_cos_x2 = 1.0 / math.cos(x1)

        y1 = math.atan2(self.m21 * inv_cos_x1, self.m22 * inv_cos_x1)
        y2 = math.atan2(self.m21 * inv_cos_x2, self.m22 * inv_cos_x2)
        z1 = math.atan2(self.m10 * inv_cos_x1, self.m00 * inv_cos_x1)
        z2 = math.atan2(self.m10 * inv_cos_x2, self.m00 * inv_cos_x2)
        if (abs(x1) + abs(y1) + abs(z1)) <= (abs(x2) + abs(y2) + abs(z2)):
            return Vector3(y1, x1, z1)
        return Vector3(y2, x2, z2)

    @classmethod
    def from_euler_angles(cls, roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0, angles_in_rad: bool = True):
        """
        fill the matrix from Euler angles in radians
        """
        assert all(isinstance(v, float) for v in (roll, pitch, yaw))
        if angles_in_rad:
            cp = math.cos(pitch)
            sp = math.sin(pitch)
            sr = math.sin(roll)
            cr = math.cos(roll)
            sy = math.sin(yaw)
            cy = math.cos(yaw)
        else:
            cp = math.cos(pitch * DEG_TO_RAD)
            sp = math.sin(pitch * DEG_TO_RAD)
            sr = math.sin(roll * DEG_TO_RAD)
            cr = math.cos(roll * DEG_TO_RAD)
            sy = math.sin(yaw * DEG_TO_RAD)
            cy = math.cos(yaw * DEG_TO_RAD)

        return cls(cp * cy, (sr * sp * cy) - (cr * sy), (cr * sp * cy) + (sr * sy),
                   cp * sy, (sr * sp * sy) + (cr * cy), (cr * sp * sy) - (sr * cy),
                   -sp, sr * cp, cr * cp)

    # def to_euler_321(self) -> Vector3:
    #     """
    #     find Euler angles (321 convention) for the matrix
    #     """
    #     if self.c.x >= 1.0:
    #         pitch = math.pi
    #     elif self.c.x <= -1.0:
    #         pitch = -math.pi
    #     else:
    #         pitch = -math.asin(self.m02)
    #     roll = math.atan2(self.m12, self.m22)
    #     yaw = math.atan2(self.m01, self.m00)
    #     return Vector3(roll, pitch, yaw)

    @property
    def right(self) -> Vector3:
        return Vector3(self.m00, self.m10, self.m20)

    @property
    def up(self) -> Vector3:
        return Vector3(self.m01, self.m11, self.m21)

    @property
    def front(self) -> Vector3:
        return Vector3(self.m02, self.m12, self.m22)

    def transpose(self):
        self.m01, self.m10 = self.m10, self.m01
        self.m02, self.m20 = self.m20, self.m02
        self.m21, self.m12 = self.m12, self.m21
        return self

    @property
    def transposed(self):
        return Matrix3.__copy__(self).transpose()

    @property
    def right_up_front(self) -> Tuple[Vector3, Vector3, Vector3]:
        return self.right, self.up, self.front

    def invert(self):
        det: float = (self.m00 * (self.m11 * self.m22 - self.m21 * self.m12) -
                      self.m01 * (self.m10 * self.m22 - self.m12 * self.m20) +
                      self.m02 * (self.m10 * self.m21 - self.m11 * self.m20))
        if abs(det) < NUMERICAL_ACCURACY:
            raise ArithmeticError("Mat3 :: singular matrix")
        det = 1.0 / det

        _m00 = self.m00
        _m01 = self.m10
        _m02 = self.m20
        _m10 = self.m01
        _m11 = self.m11
        _m12 = self.m21
        _m20 = self.m02
        _m21 = self.m12
        _m22 = self.m22

        self.m00 = (_m11 * _m22 - _m21 * _m12) * det
        self.m10 = (_m02 * _m21 - _m01 * _m22) * det
        self.m20 = (_m01 * _m12 - _m02 * _m11) * det
        self.m01 = (_m12 * _m20 - _m10 * _m22) * det
        self.m11 = (_m00 * _m22 - _m02 * _m20) * det
        self.m21 = (_m10 * _m02 - _m00 * _m12) * det
        self.m02 = (_m10 * _m21 - _m20 * _m11) * det
        self.m12 = (_m20 * _m01 - _m00 * _m21) * det
        self.m22 = (_m00 * _m11 - _m10 * _m01) * det
        return self

    @property
    def inverted(self):
        return self.__copy__().invert()

    def __str__(self) -> str:
        return f"\t\t{{\n" \
               f"\t\t\t\"m00\": {self.m00:{_4F}}, \"m01\": {self.m01:{_4F}}, \"m02\": {self.m02:{_4F}},\n" \
               f"\t\t\t\"m10\": {self.m10:{_4F}}, \"m11\": {self.m11:{_4F}}, \"m12\": {self.m12:{_4F}},\n" \
               f"\t\t\t\"m20\": {self.m20:{_4F}}, \"m21\": {self.m21:{_4F}}, \"m22\": {self.m22:{_4F}}\n" \
               f"\t\t}}"

    def __copy__(self):
        return Matrix3(*(val for val in self))

    def __neg__(self):
        return self.__mul__(-1.0)

    def __add__(self, other):
        if isinstance(other, Matrix3):
            return Matrix3(*(s + o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Matrix3(*(s + other for s in self))
        raise RuntimeError(f"Matrix3::Add::wrong argument type {type(other)}")

    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Matrix3):
            for attr, value in zip(Matrix3.__slots__, other):
                self.__setattr__(attr, self.__getattribute__(attr) + value)
            return self
        if isinstance(other, int) or isinstance(other, float):
            for attr in Matrix3.__slots__:
                self.__setattr__(attr, self.__getattribute__(attr) + other)
        raise RuntimeError(f"Matrix3::Add::wrong argument type {type(other)}")

    def __sub__(self, other):
        if isinstance(other, Matrix3):
            return Matrix3(*(s - o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Matrix3(*(s - other for s in self))
        raise RuntimeError(f"Matrix3::Sub::wrong argument type {type(other)}")

    def __rsub__(self, other):
        if isinstance(other, Matrix3):
            return Matrix3(*(o - s for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Matrix3(*(other - s for s in self))
        raise RuntimeError(f"Matrix3::Sub::wrong argument type {type(other)}")

    def __isub__(self, other):
        if isinstance(other, Matrix3):
            for attr, value in zip(Matrix3.__slots__, other):
                self.__setattr__(attr, self.__getattribute__(attr) - value)
            return self
        if isinstance(other, int) or isinstance(other, float):
            for attr in Matrix3.__slots__:
                self.__setattr__(attr, self.__getattribute__(attr) - other)
        raise RuntimeError(f"Matrix3::Add::wrong argument type {type(other)}")

    def __mul__(self, other):
        if isinstance(other, Matrix3):
            return Matrix3(self.m00 * other.m00 + self.m01 * other.m10 + self.m02 * other.m20,
                           self.m00 * other.m01 + self.m01 * other.m11 + self.m02 * other.m21,
                           self.m00 * other.m02 + self.m01 * other.m12 + self.m02 * other.m22,
                           self.m10 * other.m00 + self.m11 * other.m10 + self.m12 * other.m20,
                           self.m10 * other.m01 + self.m11 * other.m11 + self.m12 * other.m21,
                           self.m10 * other.m02 + self.m11 * other.m12 + self.m12 * other.m22,
                           self.m20 * other.m00 + self.m21 * other.m10 + self.m22 * other.m20,
                           self.m20 * other.m01 + self.m21 * other.m11 + self.m22 * other.m21,
                           self.m20 * other.m02 + self.m21 * other.m12 + self.m22 * other.m22)
        if isinstance(other, Vector3):
            return Vector3(self.m00 * other.x + self.m01 * other.y + self.m02 * other.z,
                           self.m10 * other.x + self.m11 * other.y + self.m12 * other.z,
                           self.m20 * other.x + self.m21 * other.y + self.m22 * other.z)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix3(*(other * s for s in self))
        raise RuntimeError(f"Matrix3::Mul::wrong argument type {type(other)}")

    def __rmul__(self, other):
        if isinstance(other, Matrix3):
            return Matrix3(other.m00 * self.m00 + other.m01 * self.m10 + other.m02 * self.m20,
                           other.m00 * self.m01 + other.m01 * self.m11 + other.m02 * self.m21,
                           other.m00 * self.m02 + other.m01 * self.m12 + other.m02 * self.m22,
                           other.m10 * self.m00 + other.m11 * self.m10 + other.m12 * self.m20,
                           other.m10 * self.m01 + other.m11 * self.m11 + other.m12 * self.m21,
                           other.m10 * self.m02 + other.m11 * self.m12 + other.m12 * self.m22,
                           other.m20 * self.m00 + other.m21 * self.m10 + other.m22 * self.m20,
                           other.m20 * self.m01 + other.m21 * self.m11 + other.m22 * self.m21,
                           other.m20 * self.m02 + other.m21 * self.m12 + other.m22 * self.m22)
        if isinstance(other, Vector3):
            return Vector3(self.m00 * other.x + self.m01 * other.x + self.m02 * other.x,
                           self.m10 * other.y + self.m11 * other.y + self.m12 * other.y,
                           self.m20 * other.z + self.m21 * other.z + self.m22 * other.z)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix3(*(other * s for s in self))
        raise RuntimeError(f"Matrix3::Mul::wrong argument type {type(other)}")

    def __imul__(self, other):
        if isinstance(other, Matrix3):
            _m00 = self.m00
            _m01 = self.m01
            _m02 = self.m02
            _m10 = self.m10
            _m11 = self.m11
            _m12 = self.m12
            _m20 = self.m20
            _m21 = self.m21
            _m22 = self.m22

            self.m00 = _m00 * other.m00 + _m01 * other.m10 + _m02 * other.m20
            self.m01 = _m00 * other.m01 + _m01 * other.m11 + _m02 * other.m21
            self.m02 = _m00 * other.m02 + _m01 * other.m12 + _m02 * other.m22
            self.m10 = _m10 * other.m00 + _m11 * other.m10 + _m12 * other.m20
            self.m11 = _m10 * other.m01 + _m11 * other.m11 + _m12 * other.m21
            self.m12 = _m10 * other.m02 + _m11 * other.m12 + _m12 * other.m22
            self.m20 = _m20 * other.m00 + _m21 * other.m10 + _m22 * other.m20
            self.m21 = _m20 * other.m01 + _m21 * other.m11 + _m22 * other.m21
            self.m22 = _m20 * other.m02 + _m21 * other.m12 + _m22 * other.m22
            return self
        if isinstance(other, int) or isinstance(other, float):
            for attr in Matrix3.__slots__:
                self.__setattr__(attr, self.__getattribute__(attr) * other)
            return self
        raise RuntimeError(f"Matrix3::Mul::wrong argument type {type(other)}")

    def __truediv__(self, other):
        if isinstance(other, Matrix3):
            return Matrix3.__mul__(self, other.inverted)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix3(*(s / other for s in self))
        raise RuntimeError(f"Matrix3::TrueDiv::wrong argument type {type(other)}")

    def __rtruediv__(self, other):
        if isinstance(other, Matrix3):
            return Matrix3.__mul__(self.inverted, other)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix3(*(other / s for s in self))
        raise RuntimeError(f"Matrix3::TrueDiv::wrong argument type {type(other)}")

    def __idiv__(self, other):
        if isinstance(other, Matrix3):
            return Matrix3.__imul__(self, other.inverted)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix3.__imul__(self, 1.0 / other)
        raise RuntimeError(f"Matrix3::IDiv::wrong argument type {type(other)}")

    def multiply_by_point(self, point: Vector2) -> Vector2:
        assert isinstance(point, Vector2)
        return Vector2(self.m00 * point.x + self.m01 * point.y + self.m02,
                       self.m10 * point.x + self.m11 * point.y + self.m12)

    def multiply_by_direction(self, point: Vector2) -> Vector2:
        assert isinstance(point, Vector2)
        return Vector2(self.m00 * point.x + self.m01 * point.y,
                       self.m10 * point.x + self.m11 * point.y)

    def to_np_array(self) -> np.ndarray:
        return np.array(self).reshape((3, 3))

    def perspective_multiply(self,  point: Vector2) -> Vector2:
        assert isinstance(point, Vector2)
        p = self * Vector3(point.x, point.y, 1.0)
        return Vector2(p.x / p.z, p.y / p.z)

    @classmethod
    def perspective_transform_from_four_points(cls, *args):
        assert (all(isinstance(item, Vector2) for item in args) and len(args) == 4)
        ur, dr, dl, ul = args
        matrix = ( 1.0,  1.0, 1.0,  0.0,  0.0, 0.0, -ur.x, -ur.x,
                   0.0,  0.0, 0.0,  1.0,  1.0, 1.0, -ur.y, -ur.y,
                   1.0, -1.0, 1.0,  0.0,  0.0, 0.0, -dr.x,  dr.x,
                   0.0,  0.0, 0.0,  1.0, -1.0, 1.0, -dr.y,  dr.y,
                  -1.0, -1.0, 1.0,  0.0,  0.0, 0.0,  dl.x,  dl.x,
                   0.0,  0.0, 0.0, -1.0, -1.0, 1.0,  dl.y,  dl.y,
                  -1.0,  1.0, 1.0,  0.0,  0.0, 0.0,  ul.x, -ul.x,
                   0.0,  0.0, 0.0, -1.0,  1.0, 1.0,  ul.y, -ul.y)
        b = np.array((ur.x, ur.y, dr.x, dr.y, dl.x, dl.y, ul.x, ul.y))
        matrix = np.array(matrix).reshape((8, 8))
        return cls(*(np.linalg.inv(matrix) @ b).flat, 1.0)

    @classmethod
    def perspective_transform_from_eight_points(cls, *args):
        assert (all(isinstance(item, Vector2) for item in args) and len(args) == 8)
        ur_1, dr_1, dl_1, ul_1, ur_2, dr_2, dl_2, ul_2 = args
        # m00 | m01 | m02 | m10 | m11 | m12 |     m20    |     m21    |
        # c_x | c_y |  1  |  0  |  0  |  0  | -p_x * c_x | -p_x * c_y |
        #  0  |  0  |  0  | c_x | c_y |  1  | -p_y * c_x | -p_y * c_y |
        matrix = (ur_2.x,  ur_2.y, 1.0,  0.0,     0.0,    0.0, -ur_1.x * ur_2.x, -ur_1.x * ur_2.y,
                  0.0,     0.0,    0.0,  ur_2.x,  ur_2.y, 1.0, -ur_1.y * ur_2.x, -ur_1.y * ur_2.y,
                  dr_2.x,  dr_2.y, 1.0,  0.0,     0.0,    0.0, -dr_1.x * dr_2.x, -dr_1.x * dr_2.y,
                  0.0,     0.0,    0.0,  dr_2.x,  dr_2.y, 1.0, -dr_1.y * dr_2.x, -dr_1.y * dr_2.y,
                  dl_2.x,  dl_2.y, 1.0,  0.0,     0.0,    0.0, -dl_1.x * dl_2.x, -dl_1.x * dl_2.y,
                  0.0,     0.0,    0.0,  dl_2.x,  dl_2.y, 1.0, -dl_1.y * dl_2.x, -dl_1.y * dl_2.y,
                  ul_2.x,  ul_2.y, 1.0,  0.0,     0.0,    0.0, -ul_1.x * ul_2.x, -ul_1.x * ul_2.y,
                  0.0,     0.0,    0.0,  ul_2.x,  ul_2.y, 1.0, -ul_1.y * ul_2.x, -ul_1.y * ul_2.y)
        b = np.array((ur_1.x, ur_1.y, dr_1.x, dr_1.y, dl_1.x, dl_1.y, ul_1.x, ul_1.y))
        matrix = np.array(matrix).reshape((8, 8))
        return cls(*(np.linalg.inv(matrix) @ b).flat, 1.0)


def matrix_3_test():
    m1 = Matrix3(1, 2, 3,
                 5, 6, 7,
                 9, 1, 9)
    m2 = Matrix3(1, 2, 3,
                 5, 6, 7,
                 9, 1, 9)
    # m2.m00 = 1.1234
    print(f"Matrix3 test")
    print(f"m1:\n{m1}")
    print(f"m2:\n{m2}")
    print(f"m1.transposed =\n{m2.transposed}")
    print(f"m1.inverted   =\n{m2.inverted}")
    print(f" m1 + m2  =\n {m1 + m2}\n")
    print(f" m1 - m2  =\n {m1 - m2}\n")
    print(f" m1 / m2  =\n {m1 / m2}\n")
    print(f" m1 * m2  =\n {m1 * m2}\n")
    print()
    m1 += m2
    print(f" m1 += m2 =\n{m1}\n")
    m1 -= m2
    print(f" m1 -= m2 =\n{m1}\n")
    m1 /= m2
    print(f" m1 /= m2 =\n{m1}\n")
    m1 *= m2
    print(f" m1 *= m2 =\n{m1}\n")
    print()
