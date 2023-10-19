from .common import NUMERICAL_FORMAT_4F as _4F, DEG_TO_RAD, NUMERICAL_ACCURACY
from dataclasses import dataclass
from .vector4 import Vector4
from .vector3 import Vector3
from typing import Tuple
import numpy as np
import math

_M00 = '_m00'
_M01 = '_m01'
_M02 = '_m02'
_M03 = '_m03'
_M10 = '_m10'
_M11 = '_m11'
_M12 = '_m12'
_M13 = '_m13'
_M20 = '_m20'
_M21 = '_m21'
_M22 = '_m22'
_M23 = '_m23'
_M30 = '_m30'
_M31 = '_m31'
_M32 = '_m32'
_M33 = '_m33'


@dataclass
class Matrix4:
    """
    mutable Matrix 4d
    """

    __slots__ = (_M00, _M01, _M02, _M03,
                 _M10, _M11, _M12, _M13,
                 _M20, _M21, _M22, _M23,
                 _M30, _M31, _M32, _M33)

    # row 0 getters
    @property
    def m00(self) -> float:
        return self.__getattribute__(_M00)

    @property
    def m01(self) -> float:
        return self.__getattribute__(_M01)

    @property
    def m02(self) -> float:
        return self.__getattribute__(_M02)

    @property
    def m03(self) -> float:
        return self.__getattribute__(_M03)

    # row 1 getters
    @property
    def m10(self) -> float:
        return self.__getattribute__(_M10)

    @property
    def m11(self) -> float:
        return self.__getattribute__(_M11)

    @property
    def m12(self) -> float:
        return self.__getattribute__(_M12)

    @property
    def m13(self) -> float:
        return self.__getattribute__(_M13)

    # row 2 getters
    @property
    def m20(self) -> float:
        return self.__getattribute__(_M20)

    @property
    def m21(self) -> float:
        return self.__getattribute__(_M21)

    @property
    def m22(self) -> float:
        return self.__getattribute__(_M22)

    @property
    def m23(self) -> float:
        return self.__getattribute__(_M23)

    # row 3 getters
    @property
    def m30(self) -> float:
        return self.__getattribute__(_M30)

    @property
    def m31(self) -> float:
        return self.__getattribute__(_M31)

    @property
    def m32(self) -> float:
        return self.__getattribute__(_M32)

    @property
    def m33(self) -> float:
        return self.__getattribute__(_M33)

    # row 0 getters
    @m00.setter
    def m00(self, value: float) -> None:
        self.__setattr__(_M00, float(value))

    @m01.setter
    def m01(self, value: float) -> None:
        self.__setattr__(_M01, float(value))

    @m02.setter
    def m02(self, value: float) -> None:
        self.__setattr__(_M02, float(value))

    @m03.setter
    def m03(self, value: float) -> None:
        self.__setattr__(_M03, float(value))

    # row 1 getters
    @m10.setter
    def m10(self, value: float) -> None:
        self.__setattr__(_M10, float(value))

    @m11.setter
    def m11(self, value: float) -> None:
        self.__setattr__(_M11, float(value))

    @m12.setter
    def m12(self, value: float) -> None:
        self.__setattr__(_M12, float(value))

    @m13.setter
    def m13(self, value: float) -> None:
        self.__setattr__(_M13, float(value))

    # row 2 getters
    @m20.setter
    def m20(self, value: float) -> None:
        self.__setattr__(_M20, float(value))

    @m21.setter
    def m21(self, value: float) -> None:
        self.__setattr__(_M21, float(value))

    @m22.setter
    def m22(self, value: float) -> None:
        self.__setattr__(_M22, float(value))

    @m23.setter
    def m23(self, value: float) -> None:
        self.__setattr__(_M23, float(value))

    # row 3 getters
    @m30.setter
    def m30(self, value: float) -> None:
        self.__setattr__(_M30, float(value))

    @m31.setter
    def m31(self, value: float) -> None:
        self.__setattr__(_M31, float(value))

    @m32.setter
    def m32(self, value: float) -> None:
        self.__setattr__(_M32, float(value))

    @m33.setter
    def m33(self, value: float) -> None:
        self.__setattr__(_M33, float(value))

    def __init__(self, *args):
        assert len(args) == 16
        for attr, val in zip(Matrix4.__slots__, args):
            self.__setattr__(attr, float(val))

    def __iter__(self):
        for attr in Matrix4.__slots__:
            yield self.__getattribute__(attr)

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
    def look_at(cls, target: Vector3, eye: Vector3, up: Vector3 = None):
        """
        :param target: цель на которую смотрим
        :param eye: положение глаза в пространстве
        :param up: вектор вверх
        :return: матрица взгляда
        """
        assert isinstance(target, Vector3)
        assert isinstance(eye, Vector3)
        if up is None:
            up = Vector3(0.0, 1.0, 0.0)
        assert isinstance(up, Vector3)

        z_axis = (target - eye).normalize()  # The "forward" vector.
        x_axis = Vector3.cross(up, z_axis).normalize()  # The "right" vector.
        y_axis = Vector3.cross(z_axis, x_axis).normalize()  # The "up" vector.

        return cls(x_axis.x, y_axis.x, z_axis.x, 0.0,
                   x_axis.y, y_axis.y, z_axis.y, 0.0,
                   x_axis.z, y_axis.z, z_axis.z, 0.0,
                   Vector3.dot(x_axis, -eye), Vector3.dot(y_axis, -eye), Vector3.dot(z_axis, -eye), 1.0)

    @classmethod
    def transform_look_at(cls, target: Vector3, eye: Vector3, up: Vector3 = None):
        """
        :param target: цель на которую смотрим
        :param eye: положение глаза в пространстве
        :param up: вектор вверх
        :return: матрица взгляда
        """
        assert isinstance(target, Vector3)
        assert isinstance(eye, Vector3)
        if up is None:
            up = Vector3(0.0, 1.0, 0.0)
        assert isinstance(up, Vector3)

        z_axis = (target - eye).normalize()  # The "forward" vector.
        x_axis = Vector3.cross(up, z_axis).normalize()  # The "right" vector.
        y_axis = Vector3.cross(x_axis, z_axis).normalize()  # The "up" vector.

        return cls(x_axis.x, y_axis.x, z_axis.x, eye.x,
                   x_axis.y, y_axis.y, z_axis.y, eye.y,
                   x_axis.z, y_axis.z, z_axis.z, eye.z,
                   0.0, 0.0, 0.0, 1.0)

    @classmethod
    def build_perspective_projection_matrix(cls, fov: float = 70.0, aspect: float = 1.0, z_near: float = 0.01, z_far: float = 1000):
        """
        :param fov: угол обзора
        :param aspect: соотношение сторон
        :param z_near: ближняя плоскость отсечения
        :param z_far: дальняя плоскость отсечения
        :return: матрица перспективной проекции
        """
        scale = max(1.0 / math.tan(fov * 0.5 * math.pi / 180.0), 0.01)
        depth_scale = z_far / (z_far - z_near)
        # z remapped in range of [0,1]
        return cls(scale * aspect, 0.0,   0.0,                   0.0,
                   0.0,            scale, 0.0,                   0.0,
                   0.0,            0.0,   -depth_scale,          -1,
                   0.0,            0.0,   -depth_scale * z_near, 0.0)

    @classmethod
    def build_ortho_projection_matrix(cls,
                                      bottom: float, top: float,
                                      left: float, right: float,
                                      near: float, far: float):
        return cls(2.0 / (right - left), 0.0,                  0.0,                0.0,
                   0.0,                  2.0 / (top - bottom), 0.0,                0.0,
                   0.0,                  0.0,                 -2.0 / (far - near), 0.0,
                   (right + left) / (left - right), (top + bottom) / (bottom - top), (far + near) / (near - far), 1.0)

    @classmethod
    def rotate_x(cls, angle: float, angle_in_rad: bool = False):
        if not angle_in_rad:
            angle *= DEG_TO_RAD
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return cls(1.0, 0.0, 0.0, 0.0,
                   0.0, cos_a, -sin_a, 0.0,
                   0.0, sin_a, cos_a, 0.0,
                   0.0, 0.0, 0.0, 1.0)

    @classmethod
    def rotate_y(cls, angle: float, angle_in_rad: bool = False):
        if not angle_in_rad:
            angle *= DEG_TO_RAD
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return cls(cos_a, 0.0, sin_a, 0.0,
                   0.0, 1.0, 0.0, 0.0,
                   -sin_a, 0.0, cos_a, 0.0,
                   0.0, 0.0, 0.0, 1.0)

    @classmethod
    def rotate_z(cls, angle: float, angle_in_rad: bool = False):
        if not angle_in_rad:
            angle *= DEG_TO_RAD
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return cls(cos_a, -sin_a, 0.0, 0.0,
                   sin_a, cos_a, 0.0, 0.0,
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

        ey = ey.normalized
        ez = ez.normalized
        ex = Vector3.cross(ez, ey).normalize()
        ez = Vector3.cross(ey, ex).normalize()

        return cls(ex.x, ey.x, ez.x, 0.0,
                   ex.y, ey.y, ez.y, 0.0,
                   ex.z, ey.z, ez.z, 0.0,
                   0.0, 0.0, 0.0, 1.0)

    @classmethod
    def from_np_array(cls, array: np.ndarray):
        assert isinstance(array, np.ndarray)
        assert array.size == 16
        return cls(*array.flat)

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
            return cls(right.x, up.x, front.x, 0.0,
                       right.y, up.y, front.y, 0.0,
                       right.z, up.z, front.z, 0.0,
                       0.0, 0.0, 0.0, 1.0)

        return cls(right.x, up.x, front.x, origin.x,
                   right.y, up.y, front.y, origin.y,
                   right.z, up.z, front.z, origin.z,
                   0.0, 0.0, 0.0, 1.0)

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

    @property
    def origin(self) -> Vector3:
        return Vector3(self.m03, self.m13, self.m23)

    @property
    def right_up_front(self) -> Tuple[Vector3, Vector3, Vector3]:
        return self.right, self.up, self.front

    def transpose(self):
        self.m01, self.m10 = self.m10, self.m01
        self.m02, self.m20 = self.m20, self.m02
        self.m03, self.m30 = self.m30, self.m03
        self.m21, self.m12 = self.m12, self.m21
        self.m31, self.m13 = self.m13, self.m31
        self.m32, self.m23 = self.m23, self.m32
        return self

    @property
    def transposed(self):
        return self.__copy__().transpose()

    @property
    def determinant(self) -> float:
        a2323: float = self.m22 * self.m33 - self.m23 * self.m32
        a1323: float = self.m21 * self.m33 - self.m23 * self.m31
        a1223: float = self.m21 * self.m32 - self.m22 * self.m31
        a0323: float = self.m20 * self.m33 - self.m23 * self.m30
        a0223: float = self.m20 * self.m32 - self.m22 * self.m30
        a0123: float = self.m20 * self.m31 - self.m21 * self.m30
        return self.m00 * (self.m11 * a2323 - self.m12 * a1323 + self.m13 * a1223) \
             - self.m01 * (self.m10 * a2323 - self.m12 * a0323 + self.m13 * a0223) \
             + self.m02 * (self.m10 * a1323 - self.m11 * a0323 + self.m13 * a0123) \
             - self.m03 * (self.m10 * a1223 - self.m11 * a0223 + self.m12 * a0123)

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

        if abs(det) < NUMERICAL_ACCURACY:
            raise ArithmeticError("Matrix4:: Invert :: singular matrix")

        det = 1.0 / det

        _m00 = self._m00
        _m01 = self._m01
        _m02 = self._m02
        _m03 = self._m03

        _m10 = self._m10
        _m11 = self._m11
        _m12 = self._m12
        _m13 = self._m13

        _m20 = self._m20
        _m21 = self._m21
        _m22 = self._m22
        _m23 = self._m23

        _m30 = self._m30
        _m31 = self._m31
        _m32 = self._m32
        _m33 = self._m33

        self.m00 = det *  (_m11 * a2323 - _m12 * a1323 + _m13 * a1223)
        self.m01 = det * -(_m01 * a2323 - _m02 * a1323 + _m03 * a1223)
        self.m02 = det *  (_m01 * a2313 - _m02 * a1313 + _m03 * a1213)
        self.m03 = det * -(_m01 * a2312 - _m02 * a1312 + _m03 * a1212)
        self.m10 = det * -(_m10 * a2323 - _m12 * a0323 + _m13 * a0223)
        self.m11 = det *  (_m00 * a2323 - _m02 * a0323 + _m03 * a0223)
        self.m12 = det * -(_m00 * a2313 - _m02 * a0313 + _m03 * a0213)
        self.m13 = det *  (_m00 * a2312 - _m02 * a0312 + _m03 * a0212)
        self.m20 = det *  (_m10 * a1323 - _m11 * a0323 + _m13 * a0123)
        self.m21 = det * -(_m00 * a1323 - _m01 * a0323 + _m03 * a0123)
        self.m22 = det *  (_m00 * a1313 - _m01 * a0313 + _m03 * a0113)
        self.m23 = det * -(_m00 * a1312 - _m01 * a0312 + _m03 * a0112)
        self.m30 = det * -(_m10 * a1223 - _m11 * a0223 + _m12 * a0123)
        self.m31 = det *  (_m00 * a1223 - _m01 * a0223 + _m02 * a0123)
        self.m32 = det * -(_m00 * a1213 - _m01 * a0213 + _m02 * a0113)
        self.m33 = det *  (_m00 * a1212 - _m01 * a0212 + _m02 * a0112)
        return self

    @property
    def inverted(self):
        return self.__copy__().invert()

    def __eq__(self, other):
        if not isinstance(other, Matrix4):
            return False
        return not any(v1 != v2 for v1, v2 in zip(self, other))

    def __str__(self):
        return "" \
               f"{{\n\t\"m00\": {self.m00:{_4F}}, \"m01\": {self.m01:{_4F}}, \"m02\": {self.m02:{_4F}}, \"m03\": {self.m03:{_4F}},\n" \
               f"\t\"m10\": {self.m10:{_4F}}, \"m11\": {self.m11:{_4F}}, \"m12\": {self.m12:{_4F}}, \"m13\": {self.m13:{_4F}},\n" \
               f"\t\"m20\": {self.m20:{_4F}}, \"m21\": {self.m21:{_4F}}, \"m22\": {self.m22:{_4F}}, \"m23\": {self.m23:{_4F}},\n" \
               f"\t\"m30\": {self.m30:{_4F}}, \"m31\": {self.m31:{_4F}}, \"m32\": {self.m32:{_4F}}, \"m33\": {self.m33:{_4F}}\n}}"

    def __copy__(self):
        return Matrix4(*(val for val in self))

    def __neg__(self):
        return self.__mul__(-1.0)

    def __add__(self, other):
        if isinstance(other, Matrix4):
            return Matrix4(*(s + o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Matrix4(*(s + other for s in self))
        raise RuntimeError(f"Matrix4::Add::wrong argument type {type(other)}")

    def __iadd__(self, other):
        if isinstance(other, Matrix4):
            for attr, value in zip(Matrix4.__slots__, other):
                self.__setattr__(attr, self.__getattribute__(attr) + value)
            return self
        if isinstance(other, int) or isinstance(other, float):
            for attr in Matrix4.__slots__:
                self.__setattr__(attr, self.__getattribute__(attr) + other)
        raise RuntimeError(f"Matrix4::Add::wrong argument type {type(other)}")

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

    def __isub__(self, other):
        if isinstance(other, Matrix4):
            for attr, value in zip(Matrix4.__slots__, other):
                self.__setattr__(attr, self.__getattribute__(attr) - value)
            return self
        if isinstance(other, int) or isinstance(other, float):
            for attr in Matrix4.__slots__:
                self.__setattr__(attr, self.__getattribute__(attr) - other)
        raise RuntimeError(f"Matrix4::ISub::wrong argument type {type(other)}")

    def __mul__(self, other):
        if isinstance(other, Matrix4):
            return Matrix4(self.m00 * other.m00 + self.m01 * other.m10 + self.m02 * other.m20 + self.m03 * other.m30,
                           self.m00 * other.m01 + self.m01 * other.m11 + self.m02 * other.m21 + self.m03 * other.m31,
                           self.m00 * other.m02 + self.m01 * other.m12 + self.m02 * other.m22 + self.m03 * other.m32,
                           self.m00 * other.m03 + self.m01 * other.m13 + self.m02 * other.m23 + self.m03 * other.m33,
                           self.m10 * other.m00 + self.m11 * other.m10 + self.m12 * other.m20 + self.m13 * other.m30,
                           self.m10 * other.m01 + self.m11 * other.m11 + self.m12 * other.m21 + self.m13 * other.m31,
                           self.m10 * other.m02 + self.m11 * other.m12 + self.m12 * other.m22 + self.m13 * other.m32,
                           self.m10 * other.m03 + self.m11 * other.m13 + self.m12 * other.m23 + self.m13 * other.m33,
                           self.m20 * other.m00 + self.m21 * other.m10 + self.m22 * other.m20 + self.m23 * other.m30,
                           self.m20 * other.m01 + self.m21 * other.m11 + self.m22 * other.m21 + self.m23 * other.m31,
                           self.m20 * other.m02 + self.m21 * other.m12 + self.m22 * other.m22 + self.m23 * other.m32,
                           self.m20 * other.m03 + self.m21 * other.m13 + self.m22 * other.m23 + self.m23 * other.m33,
                           self.m30 * other.m00 + self.m31 * other.m10 + self.m32 * other.m20 + self.m33 * other.m30,
                           self.m30 * other.m01 + self.m31 * other.m11 + self.m32 * other.m21 + self.m33 * other.m31,
                           self.m30 * other.m02 + self.m31 * other.m12 + self.m32 * other.m22 + self.m33 * other.m32,
                           self.m30 * other.m03 + self.m31 * other.m13 + self.m32 * other.m23 + self.m33 * other.m33)
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
            return Matrix4(other.m00 * self.m00 + other.m01 * self.m10 + other.m02 * self.m20 + other.m03 * self.m30,
                           other.m00 * self.m01 + other.m01 * self.m11 + other.m02 * self.m21 + other.m03 * self.m31,
                           other.m00 * self.m02 + other.m01 * self.m12 + other.m02 * self.m22 + other.m03 * self.m32,
                           other.m00 * self.m03 + other.m01 * self.m13 + other.m02 * self.m23 + other.m03 * self.m33,
                           other.m10 * self.m00 + other.m11 * self.m10 + other.m12 * self.m20 + other.m13 * self.m30,
                           other.m10 * self.m01 + other.m11 * self.m11 + other.m12 * self.m21 + other.m13 * self.m31,
                           other.m10 * self.m02 + other.m11 * self.m12 + other.m12 * self.m22 + other.m13 * self.m32,
                           other.m10 * self.m03 + other.m11 * self.m13 + other.m12 * self.m23 + other.m13 * self.m33,
                           other.m20 * self.m00 + other.m21 * self.m10 + other.m22 * self.m20 + other.m23 * self.m30,
                           other.m20 * self.m01 + other.m21 * self.m11 + other.m22 * self.m21 + other.m23 * self.m31,
                           other.m20 * self.m02 + other.m21 * self.m12 + other.m22 * self.m22 + other.m23 * self.m32,
                           other.m20 * self.m03 + other.m21 * self.m13 + other.m22 * self.m23 + other.m23 * self.m33,
                           other.m30 * self.m00 + other.m31 * self.m10 + other.m32 * self.m20 + other.m33 * self.m30,
                           other.m30 * self.m01 + other.m31 * self.m11 + other.m32 * self.m21 + other.m33 * self.m31,
                           other.m30 * self.m02 + other.m31 * self.m12 + other.m32 * self.m22 + other.m33 * self.m32,
                           other.m30 * self.m03 + other.m31 * self.m13 + other.m32 * self.m23 + other.m33 * self.m33)
        if isinstance(other, Vector4):
            return Vector4(self.m00 * other.x + self.m01 * other.x + self.m02 * other.x + self.m03 * other.x,
                           self.m10 * other.y + self.m11 * other.y + self.m12 * other.y + self.m13 * other.y,
                           self.m20 * other.z + self.m21 * other.z + self.m22 * other.z + self.m23 * other.z,
                           self.m30 * other.w + self.m31 * other.w + self.m32 * other.w + self.m33 * other.w)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix4(*(other * s for s in self))
        raise RuntimeError(f"Matrix4::Mul::wrong argument type {type(other)}")

    def __imul__(self, other):
        if isinstance(other, Matrix4):
            _m00 = self.m00
            _m01 = self.m01
            _m02 = self.m02
            _m03 = self.m03
            _m10 = self.m10
            _m11 = self.m11
            _m12 = self.m12
            _m13 = self.m13
            _m20 = self.m20
            _m21 = self.m21
            _m22 = self.m22
            _m23 = self.m23
            _m30 = self.m30
            _m31 = self.m31
            _m32 = self.m32
            _m33 = self.m33
            self._m00 = _m00 * other.m00 + _m01 * other.m10 + _m02 * other.m20 + _m03 * other.m30
            self._m01 = _m00 * other.m01 + _m01 * other.m11 + _m02 * other.m21 + _m03 * other.m31
            self._m02 = _m00 * other.m02 + _m01 * other.m12 + _m02 * other.m22 + _m03 * other.m32
            self._m03 = _m00 * other.m03 + _m01 * other.m13 + _m02 * other.m23 + _m03 * other.m33
            self._m10 = _m10 * other.m00 + _m11 * other.m10 + _m12 * other.m20 + _m13 * other.m30
            self._m11 = _m10 * other.m01 + _m11 * other.m11 + _m12 * other.m21 + _m13 * other.m31
            self._m12 = _m10 * other.m02 + _m11 * other.m12 + _m12 * other.m22 + _m13 * other.m32
            self._m13 = _m10 * other.m03 + _m11 * other.m13 + _m12 * other.m23 + _m13 * other.m33
            self._m20 = _m20 * other.m00 + _m21 * other.m10 + _m22 * other.m20 + _m23 * other.m30
            self._m21 = _m20 * other.m01 + _m21 * other.m11 + _m22 * other.m21 + _m23 * other.m31
            self._m22 = _m20 * other.m02 + _m21 * other.m12 + _m22 * other.m22 + _m23 * other.m32
            self._m23 = _m20 * other.m03 + _m21 * other.m13 + _m22 * other.m23 + _m23 * other.m33
            self._m30 = _m30 * other.m00 + _m31 * other.m10 + _m32 * other.m20 + _m33 * other.m30
            self._m31 = _m30 * other.m01 + _m31 * other.m11 + _m32 * other.m21 + _m33 * other.m31
            self._m32 = _m30 * other.m02 + _m31 * other.m12 + _m32 * other.m22 + _m33 * other.m32
            self._m33 = _m30 * other.m03 + _m31 * other.m13 + _m32 * other.m23 + _m33 * other.m33
            return self
        if isinstance(other, int) or isinstance(other, float):
            for attr in Matrix4.__slots__:
                self.__setattr__(attr, self.__getattribute__(attr) * other)
            return self
        raise RuntimeError(f"Matrix4::IMul::wrong argument type {type(other)}")

    def __truediv__(self, other):
        if isinstance(other, Matrix4):
            return Matrix4.__mul__(self, other.inverted)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix4(*(s / other for s in self))
        raise RuntimeError(f"Matrix4::TrueDiv::wrong argument type {type(other)}")

    def __rtruediv__(self, other):
        if isinstance(other, Matrix4):
            return Matrix4.__mul__(self.inverted, other)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix4(*(other / s for s in self))
        raise RuntimeError(f"Matrix4::TrueDiv::wrong argument type {type(other)}")

    def __idiv__(self, other):
        if isinstance(other, Matrix4):
            return Matrix4.__imul__(self, other.inverted)
        if isinstance(other, int) or isinstance(other, float):
            return Matrix4.__imul__(self, 1.0 / other)
        raise RuntimeError(f"Matrix4::TrueDiv::wrong argument type {type(other)}")

    def multiply_by_point(self, point: Vector3) -> Vector3:
        assert isinstance(point, Vector3)
        return Vector3(self.m00 * point.x + self.m01 * point.y + self.m02 * point.z + self.m03,
                       self.m10 * point.x + self.m11 * point.y + self.m12 * point.z + self.m13,
                       self.m20 * point.x + self.m21 * point.y + self.m22 * point.z + self.m23)

    def multiply_by_direction(self, point: Vector3) -> Vector3:
        assert isinstance(point, Vector3)
        return Vector3(self.m00 * point.x + self.m01 * point.y + self.m02 * point.z,
                       self.m10 * point.x + self.m11 * point.y + self.m12 * point.z,
                       self.m20 * point.x + self.m21 * point.y + self.m22 * point.z)

    def to_np_array(self) -> np.ndarray:
        return np.array(self).reshape((4, 4))


def matrix_4_test():
    m1 = Matrix4(1,   2,  3,  4,
                 5,   6,  7,  8,
                 9,  1, 11, 12,
                 13, 14, 0, 16)
    m2 = Matrix4(1,   2,  3,  4,
                 5,   6,  7,  8,
                 9,  1, 11, 12,
                 13, 14, 0, 16)
    print(f"Matrix4 test")
    print()
    print(m2)
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


# if __name__ == "__main__":
#     matrix_4_test()
#