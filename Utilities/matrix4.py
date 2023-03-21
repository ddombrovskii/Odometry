# from accelerometer_core.Utilities.vector4 import Vector4
# from accelerometer_core.Utilities.vector3 import Vector3

from collections import namedtuple
from .vector4 import Vector4
from .vector3 import Vector3
from typing import Tuple
import math


class Matrix4(namedtuple('Matrix4', 'm00, m01, m02, m03,'
                                    'm10, m11, m12, m13,'
                                    'm20, m21, m22, m23,'
                                    'm30, m31, m32, m33')):
    """
    immutable Matrix 4d
    """

    def __new__(cls, m00: float = 0.0, m01: float = 0.0, m02: float = 0.0, m03: float = 0.0,
                m10: float = 0.0, m11: float = 0.0, m12: float = 0.0, m13: float = 0.0,
                m20: float = 0.0, m21: float = 0.0, m22: float = 0.0, m23: float = 0.0,
                m30: float = 0.0, m31: float = 0.0, m32: float = 0.0, m33: float = 0.0):
        return super().__new__(cls,
                               float(m00), float(m01), float(m02), float(m03),
                               float(m10), float(m11), float(m12), float(m13),
                               float(m20), float(m21), float(m22), float(m23),
                               float(m30), float(m31), float(m32), float(m33))

    @classmethod
    def identity(cls):
        return cls(1.0, 0.0, 0.0, 0.0,
                   0.0, 1.0, 0.0, 0.0,
                   0.0, 0.0, 1.0, 0.0,
                   0.0, 0.0, 0.0, 1.0)

    @classmethod
    def zeros(cls):
        return cls(0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0)

    @classmethod
    def look_at(cls, target: Vector3, eye: Vector3, up: Vector3 = Vector3(0, 1, 0)):
        """
        :param target: цель на которую смотрим
        :param eye: положение глаза в пространстве
        :param up: вектор вверх
        :return: матрица взгляда
        """
        zaxis = target - eye  # The "forward" vector.
        zaxis.normalize()
        xaxis = Vector3.cross(up, zaxis)  # The "right" vector.
        xaxis.normalize()
        yaxis = Vector3.cross(zaxis, xaxis)  # The "up" vector.

        return cls(xaxis.x, -yaxis.x, zaxis.x, eye.x,
                   -xaxis.y, -yaxis.y, zaxis.y, eye.y,
                   xaxis.z, -yaxis.z, zaxis.z, eye.z,
                   0.0, 0.0, 0.0, 1.0)

    @classmethod
    def build_projection_matrix(cls, fov: float = 70, aspect: float = 1, z_near: float = 0.01, z_far: float = 1000):
        """
        :param fov: угол обзора
        :param aspect: соотношение сторон
        :param z_near: ближняя плоскость отсечения
        :param z_far: дальняя плоскость отсечения
        :return: матрица перспективной проекции
        """
        scale = 1.0 / math.tan(fov * 0.5 * math.pi / 180)
        #  scale * aspect  # scale the x coordinates of the projected point
        #  scale  # scale the y coordinates of the projected point
        #  z_far / (z_near - z_far)  # used to remap z to [0,1]
        #  z_far * z_near / (z_near - z_far)  # used to remap z [0,1]
        #  -1  # set w = -z
        #  0
        return cls(scale * aspect, 0.0,   0.0,                               0.0,
                   0.0,            scale, 0.0,                               0.0,
                   0.0, 0.0,              z_far / (z_near - z_far),         -1.0,
                   0.0, 0.0,              z_far * z_near / (z_near - z_far), 0.0)

    @classmethod
    def rotate_x(cls, angle: float, angle_in_rad: bool = True):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        if not angle_in_rad:
            angle *= (math.pi / 180.0)
        return cls(1.0, 0.0, 0.0, 0.0,
                   0.0, cos_a, -sin_a, 0.0,
                   0.0, sin_a, cos_a, 0.0,
                   0.0, 0.0, 0.0, 1.0)

    @classmethod
    def rotate_y(cls, angle: float, angle_in_rad: bool = True):
        if not angle_in_rad:
            angle *= (math.pi / 180.0)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return cls(cos_a, 0.0, sin_a, 0.0,
                   0.0, 1.0, 0.0, 0.0,
                   -sin_a, 0.0, cos_a, 0.0,
                   0.0, 0.0, 0.0, 1.0)

    @classmethod
    def rotate_z(cls, angle: float, angle_in_rad: bool = True):
        if not angle_in_rad:
            angle *= (math.pi / 180.0)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return cls(cos_a, -sin_a, 0.0, 0.0,
                   sin_a,  cos_a, 0.0, 0.0,
                   0.0, 0.0, 1.0, 0.0,
                   0.0, 0.0, 0.0, 1.0)

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

        return cls(ex[0], ey[0], ez[0], 0.0,
                   ex[1], ey[1], ez[1], 0.0,
                   ex[2], ey[2], ez[2], 0.0,
                   0.0, 0.0, 0.0, 1.0)

    @classmethod
    def build_transform(cls, right: Vector3, up: Vector3, front: Vector3, origin: Vector3 = None):
        """
        -- НЕ ПРОВЕРЯЕТ ОРТОГОНАЛЬНОСТЬ front, up, right !!!
        :param front:
        :param up:
        :param right:
        :param origin:
        :return:
        """
        if origin is None:
            return cls(right[0], up[0], front[0], 0.0,
                       right[1], up[1], front[1], 0.0,
                       right[2], up[2], front[2], 0.0,
                       0.0, 0.0, 0.0, 1.0)
  
        return cls(right[0], up[0], front[0], origin[0],
                   right[1], up[1], front[1], origin[1],
                   right[2], up[2], front[2], origin[2],
                   0.0, 0.0, 0.0, 1.0)

    def to_euler_angles(self) -> Vector3:
        """
        :return: углы поворота по осям
        """
        if math.fabs(self.m20 + 1) < 1e-6:
            return Vector3(0.0, math.pi * 0.5, math.atan2(self.m01, self.m02))

        if math.fabs(self.m20 - 1) < 1e-6:
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

    @property
    def origin(self) -> Vector3:
        return Vector3(self.m03, self.m13, self.m23)

    @property
    def right_up_front(self) -> Tuple[Vector3, Vector3, Vector3]:
        return self.right, self.up, self.front

    def transpose(self):
        return Matrix4(self.m00, self.m10, self.m20, self.m30,
                       self.m01, self.m11, self.m21, self.m31,
                       self.m02, self.m12, self.m22, self.m32,
                       self.m03, self.m13, self.m23, self.m33)

    def invert(self):
        a2323: float = self.m22 * self.m33 - self.m23 * self.m32
        a1323: float = self.m21 * self.m33 - self.m23 * self.m31
        a1223: float = self.m21 * self.m32 - self.m22 * self.m31
        a0323: float = self.m20 * self.m33 - self.m23 * self.m30
        a0223: float = self.m20 * self.m32 - self.m22 * self.m30
        a0123: float = self.m20 * self.m31 - self.m21 * self.m30
        a2313: float = self.m12 * self.m33 - self.m13 * self.m32
        a1313: float = self.m11 * self.m33 - self.m13 * self.m31
        a1213: float = self.m11 * self.m32 - self.m12 * self.m31
        a2312: float = self.m12 * self.m23 - self.m13 * self.m22
        a1312: float = self.m11 * self.m23 - self.m13 * self.m21
        a1212: float = self.m11 * self.m22 - self.m12 * self.m21
        a0313: float = self.m10 * self.m33 - self.m13 * self.m30
        a0213: float = self.m10 * self.m32 - self.m12 * self.m30
        a0312: float = self.m10 * self.m23 - self.m13 * self.m20
        a0212: float = self.m10 * self.m22 - self.m12 * self.m20
        a0113: float = self.m10 * self.m31 - self.m11 * self.m30
        a0112: float = self.m10 * self.m21 - self.m11 * self.m20

        det: float = self.m00 * (self.m11 * a2323 - self.m12 * a1323 + self.m13 * a1223) \
                     - self.m01 * (self.m10 * a2323 - self.m12 * a0323 + self.m13 * a0223) \
                     + self.m02 * (self.m10 * a1323 - self.m11 * a0323 + self.m13 * a0123) \
                     - self.m03 * (self.m10 * a1223 - self.m11 * a0223 + self.m12 * a0123)

        if abs(det) < 1e-12:
            raise ArithmeticError("Matrix4:: Invert :: singular matrix")

        det = 1.0 / det

        return Matrix4(det * (self.m11 * a2323 - self.m12 * a1323 + self.m13 * a1223),
                       det * -(self.m01 * a2323 - self.m02 * a1323 + self.m03 * a1223),
                       det * (self.m01 * a2313 - self.m02 * a1313 + self.m03 * a1213),
                       det * -(self.m01 * a2312 - self.m02 * a1312 + self.m03 * a1212),
                       det * -(self.m10 * a2323 - self.m12 * a0323 + self.m13 * a0223),
                       det * (self.m00 * a2323 - self.m02 * a0323 + self.m03 * a0223),
                       det * -(self.m00 * a2313 - self.m02 * a0313 + self.m03 * a0213),
                       det * (self.m00 * a2312 - self.m02 * a0312 + self.m03 * a0212),
                       det * (self.m10 * a1323 - self.m11 * a0323 + self.m13 * a0123),
                       det * -(self.m00 * a1323 - self.m01 * a0323 + self.m03 * a0123),
                       det * (self.m00 * a1313 - self.m01 * a0313 + self.m03 * a0113),
                       det * -(self.m00 * a1312 - self.m01 * a0312 + self.m03 * a0112),
                       det * -(self.m10 * a1223 - self.m11 * a0223 + self.m12 * a0123),
                       det * (self.m00 * a1223 - self.m01 * a0223 + self.m02 * a0123),
                       det * -(self.m00 * a1213 - self.m01 * a0213 + self.m02 * a0113),
                       det * (self.m00 * a1212 - self.m01 * a0212 + self.m02 * a0112))

    def __str__(self):
        return "" \
               f"{{\n\t\"m00\": {self.m00:20}, \"m01\": {self.m01:20}, \"m02\": {self.m02:20}, \"m03\": {self.m03:20},\n" \
               f"\t\"m10\": {self.m10:20}, \"m11\": {self.m11:20}, \"m12\": {self.m12:20}, \"m13\": {self.m13:20},\n" \
               f"\t\"m20\": {self.m20:20}, \"m21\": {self.m21:20}, \"m22\": {self.m22:20}, \"m23\": {self.m23:20},\n" \
               f"\t\"m30\": {self.m30:20}, \"m31\": {self.m31:20}, \"m32\": {self.m32:20}, \"m33\": {self.m33:20}\n}}"

    def __neg__(self):
        return Matrix4(*(-val for val in self))

    def __add__(self, other):
        if isinstance(other, Matrix4):
            return Matrix4(*(s + o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Matrix4(*(s + other for s in self))
        raise RuntimeError(f"Matrix4::Add::wrong argument type {type(other)}")

    __iadd__ = __add__

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Matrix4):
            return Matrix4(*(s - o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Matrix4(*(s - other for s in self))
        raise RuntimeError(f"Matrix4::Sub::wrong argument type {type(other)}")

    def __rsub__(self, other):
        if isinstance(other, Matrix4):
            return Matrix4(*(o - s for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Matrix4(*(other - s for s in self))
        raise RuntimeError(f"Matrix4::Sub::wrong argument type {type(other)}")

    __isub__ = __sub__

    def __mul__(self, other):
        if isinstance(other, Matrix4):
            return Matrix4(self[0] * other[0] + self[1] * other[4] + self[2] * other[8] + self[3] * other[12],
                           self[0] * other[1] + self[1] * other[5] + self[2] * other[9] + self[3] * other[13],
                           self[0] * other[2] + self[1] * other[6] + self[2] * other[10] + self[3] * other[14],
                           self[0] * other[3] + self[1] * other[7] + self[2] * other[11] + self[3] * other[15],
                           self[4] * other[0] + self[5] * other[4] + self[6] * other[8] + self[7] * other[12],
                           self[4] * other[1] + self[5] * other[5] + self[6] * other[9] + self[7] * other[13],
                           self[4] * other[2] + self[5] * other[6] + self[6] * other[10] + self[7] * other[14],
                           self[4] * other[3] + self[5] * other[7] + self[6] * other[11] + self[7] * other[15],
                           self[8] * other[0] + self[9] * other[4] + self[10] * other[8] + self[11] * other[12],
                           self[8] * other[1] + self[9] * other[5] + self[10] * other[9] + self[11] * other[13],
                           self[8] * other[2] + self[9] * other[6] + self[10] * other[10] + self[11] * other[14],
                           self[8] * other[3] + self[9] * other[7] + self[10] * other[11] + self[11] * other[15],
                           self[12] * other[0] + self[13] * other[4] + self[14] * other[8] + self[15] * other[12],
                           self[12] * other[1] + self[13] * other[5] + self[14] * other[9] + self[15] * other[13],
                           self[12] * other[2] + self[13] * other[6] + self[14] * other[10] + self[15] * other[14],
                           self[12] * other[3] + self[13] * other[7] + self[14] * other[11] + self[15] * other[15])
        if isinstance(other, Vector4):
            return Vector4(self.m00 * other.x + self.m01 * other.y + self.m02 * other.z + self.m03 * other.w,
                           self.m10 * other.x + self.m11 * other.y + self.m12 * other.z + self.m13 * other.w,
                           self.m20 * other.x + self.m21 * other.y + self.m22 * other.z + self.m23 * other.w,
                           self.m30 * other.x + self.m31 * other.y + self.m32 * other.z + self.m33 * other.w)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix4(*(other * s for s in self))
        raise RuntimeError(f"Matrix4::Mul::wrong argument type {type(other)}")

    def __rmul__(self, other):
        if isinstance(other, Matrix4):
            return Matrix4(other[0] * self[0] + other[1] * self[4] + other[2] * self[8] + other[3] * self[12],
                           other[0] * self[1] + other[1] * self[5] + other[2] * self[9] + other[3] * self[13],
                           other[0] * self[2] + other[1] * self[6] + other[2] * self[10] + other[3] * self[14],
                           other[0] * self[3] + other[1] * self[7] + other[2] * self[11] + other[3] * self[15],
                           other[4] * self[0] + other[5] * self[4] + other[6] * self[8] + other[7] * self[12],
                           other[4] * self[1] + other[5] * self[5] + other[6] * self[9] + other[7] * self[13],
                           other[4] * self[2] + other[5] * self[6] + other[6] * self[10] + other[7] * self[14],
                           other[4] * self[3] + other[5] * self[7] + other[6] * self[11] + other[7] * self[15],
                           other[8] * self[0] + other[9] * self[4] + other[10] * self[8] + other[11] * self[12],
                           other[8] * self[1] + other[9] * self[5] + other[10] * self[9] + other[11] * self[13],
                           other[8] * self[2] + other[9] * self[6] + other[10] * self[10] + other[11] * self[14],
                           other[8] * self[3] + other[9] * self[7] + other[10] * self[11] + other[11] * self[15],
                           other[12] * self[0] + other[13] * self[4] + other[14] * self[8] + other[15] * self[12],
                           other[12] * self[1] + other[13] * self[5] + other[14] * self[9] + other[15] * self[13],
                           other[12] * self[2] + other[13] * self[6] + other[14] * self[10] + other[15] * self[14],
                           other[12] * self[3] + other[13] * self[7] + other[14] * self[11] + other[15] * self[15])
        if isinstance(other, Vector4):
            return Vector4(self.m00 * other.x + self.m01 * other.x + self.m02 * other.x + self.m03 * other.x,
                           self.m10 * other.y + self.m11 * other.y + self.m12 * other.y + self.m13 * other.y,
                           self.m20 * other.z + self.m21 * other.z + self.m22 * other.z + self.m23 * other.z,
                           self.m30 * other.w + self.m31 * other.w + self.m32 * other.w + self.m33 * other.w)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix4(*(other * s for s in self))
        raise RuntimeError(f"Matrix4::Mul::wrong argument type {type(other)}")

    def __imul__(self, other):
        return Matrix4.__mul__(self, other)

    def __truediv__(self, other):
        if isinstance(other, Matrix4):
            return Matrix4.__mul__(self, other.invert())
        if isinstance(other, int) or isinstance(other, float):
            return Matrix4(*(s / other for s in self))
        raise RuntimeError(f"Matrix4::TrueDiv::wrong argument type {type(other)}")

    def __rtruediv__(self, other):
        if isinstance(other, Matrix4):
            return Matrix4.__mul__(self.invert(), other)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix4(*(other / s for s in self))
        raise RuntimeError(f"Matrix4::TrueDiv::wrong argument type {type(other)}")
