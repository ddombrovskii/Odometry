# from accelerometer_core.Utilities.vector3 import Vector3
from .common import NUMERICAL_FORMAT_4F as _4F, DEG_TO_RAD, NUMERICAL_ACCURACY
from collections import namedtuple
from .vector3 import Vector3
from typing import Tuple
import math


class Matrix3(namedtuple('Matrix3', 'm00, m01, m02,'
                                    'm10, m11, m12,'
                                    'm20, m21, m22')):
    """
    immutable Matrix 4d
    """
    def __new__(cls,
                m00: float = 0.0, m01: float = 0.0, m02: float = 0.0,
                m10: float = 0.0, m11: float = 0.0, m12: float = 0.0,
                m20: float = 0.0, m21: float = 0.0, m22: float = 0.0):
        return super().__new__(cls,
                               float(m00), float(m01), float(m02),
                               float(m10), float(m11), float(m12),
                               float(m20), float(m21), float(m22))

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
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        if not angle_in_rad:
            angle *= DEG_TO_RAD
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
        if ez is None:
            ez = Vector3(0.0, 0.0, 1.0)

        ey = ey.normalized()
        ez = ez.normalized()
        ex = Vector3.cross(ez, ey).normalized()
        ez = Vector3.cross(ey, ex).normalized()

        return cls(ex[0], ey[0], ez[0],
                   ex[1], ey[1], ez[1],
                   ex[2], ey[2], ez[2])

    @classmethod
    def build_transform(cls, right: Vector3, up: Vector3, front: Vector3):
        """
        -- НЕ ПРОВЕРЯЕТ ОРТОГОНАЛЬНОСТЬ front, up, right !!!
        :param front:
        :param up:
        :param right:
        :return:
        """
        return cls(right[0], up[0], front[0],
                   right[1], up[1], front[1],
                   right[2], up[2], front[2])

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
        return Matrix3(self.m00, self.m10, self.m20,
                       self.m01, self.m11, self.m21,
                       self.m02, self.m12, self.m22)

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

        return Matrix3((self.m11 * self.m22 - self.m21 * self.m12) * det,
                       (self.m02 * self.m21 - self.m01 * self.m22) * det,
                       (self.m01 * self.m12 - self.m02 * self.m11) * det,
                       (self.m12 * self.m20 - self.m10 * self.m22) * det,
                       (self.m00 * self.m22 - self.m02 * self.m20) * det,
                       (self.m10 * self.m02 - self.m00 * self.m12) * det,
                       (self.m10 * self.m21 - self.m20 * self.m11) * det,
                       (self.m20 * self.m01 - self.m00 * self.m21) * det,
                       (self.m00 * self.m11 - self.m10 * self.m01) * det)

    def __str__(self) -> str:
        return f"{{\n\t\"m00\": {self.m00:{_4F}}, \"m01\": {self.m01:{_4F}}, \"m02\": {self.m02:{_4F}},\n" \
               f"\t\"m10\": {self.m10:{_4F}}, \"m11\": {self.m11:{_4F}}, \"m12\": {self.m12:{_4F}},\n" \
               f"\t\"m20\": {self.m20:{_4F}}, \"m21\": {self.m21:{_4F}}, \"m22\": {self.m22:{_4F}}\n}}\n"

    def __neg__(self):
        return Matrix3(*(-val for val in self))

    def __add__(self, other):
        if isinstance(other, Matrix3):
            return Matrix3(*(s + o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Matrix3(*(s + other for s in self))
        raise RuntimeError(f"Matrix3::Add::wrong argument type {type(other)}")

    __iadd__ = __add__

    __radd__ = __add__

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

    __isub__ = __sub__

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
        return Matrix3.__mul__(self, other)

    def __truediv__(self, other):
        if isinstance(other, Matrix3):
            return Matrix3.__mul__(self, other.invert())
        if isinstance(other, int) or isinstance(other, float):
            return Matrix3(*(s / other for s in self))
        raise RuntimeError(f"Matrix3::TrueDiv::wrong argument type {type(other)}")

    def __rtruediv__(self, other):
        if isinstance(other, Matrix3):
            return Matrix3.__mul__(self.invert(), other)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix3(*(other / s for s in self))
        raise RuntimeError(f"Matrix3::TrueDiv::wrong argument type {type(other)}")
