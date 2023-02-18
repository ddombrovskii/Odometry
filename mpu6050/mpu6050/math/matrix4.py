import math
from collections import namedtuple
from vector3 import Vector3


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
        return super().__new__(cls, float(m00), float(m01), float(m02), float(m03),
                               float(m10), float(m11), float(m12), float(m13),
                               float(m20), float(m21), float(m22), float(m23),
                               float(m30), float(m31), float(m32), float(m33))

    @classmethod
    def rotate_x(cls, angle: float, angle_in_rad: bool = True):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        if not angle_in_rad:
            angle *= (math.pi / 180)
        return cls(1, 0, 0, 0,
                   0, cos_a, -sin_a, 0,
                   0, sin_a, cos_a, 0,
                   0, 0, 0, 1)

    @classmethod
    def rotate_y(cls, angle: float, angle_in_rad: bool = True):
        if not angle_in_rad:
            angle *= (math.pi / 180)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return cls(cos_a, 0, sin_a, 0,
                   0, 1, 0, 0,
                   -sin_a, 0, cos_a, 0,
                   0, 0, 0, 1)

    @classmethod
    def rotate_z(cls, angle: float, angle_in_rad: bool = True):
        if not angle_in_rad:
            angle *= (math.pi / 180)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return cls(cos_a, -sin_a, 0, 0,
                   sin_a, cos_a, 0, 0,
                   0, 0, 1, 0,
                   0, 0, 0, 1)

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
