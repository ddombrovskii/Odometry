from .common import NUMERICAL_FORMAT_4F as _4F, DEG_TO_RAD
from dataclasses import dataclass
from .matrix4 import Matrix4
from .vector3 import Vector3
import numpy as np
import math


_EW = '_ew'
_EX = '_ex'
_EY = '_ey'
_EZ = '_ez'


@dataclass
class Quaternion:
    """
    immutable Quaternion
    """
    __slots__ = (_EW, _EX, _EY, _EZ)

    @property
    def ex(self) -> float:
        return self.__getattribute__(_EX)

    @property
    def ey(self) -> float:
        return self.__getattribute__(_EY)

    @property
    def ez(self) -> float:
        return self.__getattribute__(_EZ)

    @property
    def ew(self) -> float:
        return self.__getattribute__(_EW)

    @ex.setter
    def ex(self, value: float) -> None:
        self.__setattr__(_EX, float(value))

    @ey.setter
    def ey(self, value: float) -> None:
        self.__setattr__(_EY, float(value))

    @ez.setter
    def ez(self, value: float) -> None:
        self.__setattr__(_EZ, float(value))

    @ew.setter
    def ew(self, value: float) -> None:
        self.__setattr__(_EW, float(value))

    def __init__(self, *args):
        assert len(args) == 4
        for attr, val in zip(Quaternion.__slots__, args):
            self.__setattr__(attr, float(val))

    def __iter__(self):
        for attr in Quaternion.__slots__:
            yield self.__getattribute__(attr)

    def conj(self):
        self.ex *= -1
        self.ey *= -1
        self.ez *= -1
        return self

    @property
    def conjugated(self):
        return Quaternion(self.ew, -self.ex, -self.ey, -self.ez)

    @property
    def magnitude_sqr(self):
        return sum(x * x for x in self)

    @property
    def magnitude(self):
        return math.sqrt(self.magnitude_sqr)

    def normalize(self):
        """
        self normalize
        """
        try:
            n2 = 1.0 / self.magnitude
            self.ew *= n2
            self.ex *= n2
            self.ey *= n2
            self.ez *= n2
            return self
        except ZeroDivisionError as _:
            return self

    @property
    def normalized(self):
        """
        normalized copy
        """
        try:
            n2 = 1.0 / self.magnitude
            return Quaternion(n2 * self.ew, n2 * self.ex, n2 * self.ey, n2 * self.ez)
        except ZeroDivisionError as _:
            return Quaternion()

    def reciprocal(self):
        try:
            n2 = 1.0 / self.magnitude_sqr
            return Quaternion(n2 * self.ew, -n2 * self.ex, -n2 * self.ey, -n2 * self.ez)
        except ZeroDivisionError as _:
            return Quaternion()

    def invert(self):
        try:
            n2 = 1.0 / self.magnitude
            self.ew *= n2
            self.ex *= -n2
            self.ey *= -n2
            self.ez *= -n2
            return self
        except ZeroDivisionError as _:
            return self

    @property
    def inverted(self):
        try:
            n2 = 1.0 / self.magnitude
            return Quaternion(n2 * self.ew, -n2 * self.ex, -n2 * self.ey, -n2 * self.ez)
        except ZeroDivisionError as _:
            return Quaternion()

    def __str__(self):
        return f"{{\"ew\": {self.ew:{_4F}}, \"ex\": {self.ex:{_4F}}, \"ey\": {self.ey:{_4F}}, \"ez\": {self.ez:{_4F}}}}"

    def __neg__(self):
        return Quaternion(-self.ew, -self.ex, -self.ey, -self.ez)

    def __add__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(self.ex + other.ex, self.ey + other.ey, self.ez + other.ez, self.ew + other.ew)
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(self.ex + other, self.ey + other, self.ez + other, self.ew + other)
        raise RuntimeError(f"Quaternion::Add::wrong argument type {type(other)}")

    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Quaternion):
            self.ex += other.ex
            self.ey += other.ey
            self.ez += other.ez
            self.ew += other.ew
            return self
        if isinstance(other, int) or isinstance(other, float):
            self.ex += other
            self.ey += other
            self.ez += other
            self.ew += other
            return self
        raise RuntimeError(f"Quaternion::IAdd::wrong argument type {type(other)}")

    def __sub__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(self.ex - other.ex, self.ey - other.ey, self.ez - other.ez, self.ew - other.ew)
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(self.ex - other, self.ey - other, self.ez - other, self.ew - other)
        raise RuntimeError(f"Quaternion::Sub::wrong argument type {type(other)}")

    def __rsub__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(other.ex - self.ex, other.ey - self.ey, other.ez - self.ez, other.ew - self.ew)
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(other - self.ex, other - self.ey, other - self.ez, other - self.ew)
        raise RuntimeError(f"Quaternion::RSub::wrong argument type {type(other)}")

    def __isub__(self, other):
        if isinstance(other, Quaternion):
            self.ex -= other.ex
            self.ey -= other.ey
            self.ez -= other.ez
            self.ew -= other.ew
            return self
        if isinstance(other, int) or isinstance(other, float):
            self.ex -= other
            self.ey -= other
            self.ez -= other
            self.ew -= other
            return self
        raise RuntimeError(f"Quaternion::ISub::wrong argument type {type(other)}")

    def __mul__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(self.ew * other.ew - self.ex * other.ex - self.ey * other.ey - self.ez * other.ez,
                              self.ew * other.ex + self.ex * other.ew - self.ey * other.ez + self.ez * other.ey,
                              self.ew * other.ey + self.ex * other.ez + self.ey * other.ew - self.ez * other.ex,
                              self.ew * other.ez - self.ex * other.ey + self.ey * other.ex + self.ez * other.ew)
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(other * self.ex, other * self.ey, other * self.ez, other * self.ew)
        raise RuntimeError(f"Quaternion::Mul::wrong argument type {type(other)}")

    def __rmul__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(other.ew * self.ew - other.ex * self.ex - other.ey * self.ey - other.ez * self.ez,
                              other.ew * self.ex + other.ex * self.ew - other.ey * self.ez + other.ez * self.ey,
                              other.ew * self.ey + other.ex * self.ez + other.ey * self.ew - other.ez * self.ex,
                              other.ew * self.ez - other.ex * self.ey + other.ey * self.ex + other.ez * self.ew)
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(other * self.ex, other * self.ey, other * self.ez, other * self.ew)
        raise RuntimeError(f"Quaternion::Mul::wrong argument type {type(other)}")

    def __imul__(self, other):
        if isinstance(other, Quaternion):
            ew = self.ew
            ex = self.ex
            ey = self.ey
            ez = self.ez
            self.ew = ew * other.ew - ex * other.ex - ey * other.ey - ez * other.ez
            self.ex = ew * other.ex + ex * other.ew - ey * other.ez + ez * other.ey
            self.ey = ew * other.ey + ex * other.ez + ey * other.ew - ez * other.ex
            self.ez = ew * other.ez - ex * other.ey + ey * other.ex + ez * other.ew
            return self
        if isinstance(other, int) or isinstance(other, float):
            self.ex *= other
            self.ey *= other
            self.ez *= other
            self.ew *= other
            return self
        raise RuntimeError(f"Quaternion::Mul::wrong argument type {type(other)}")

    def __truediv__(self, other):
        if isinstance(other, Quaternion):
            return self.__mul__(other.reciprocal())
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(self.ex / other, self.ey / other, self.ez / other, self.ew / other)

    def __rtruediv__(self, other):
        if isinstance(other, Quaternion):
            return other.__mul__(self.reciprocal())
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(other / self.ex, other / self.ey, other / self.ez, other / self.ew)

    def __idiv__(self, other):
        if isinstance(other, Quaternion):
            return self.__imul__(other.reciprocal())
        if isinstance(other, int) or isinstance(other, float):
            return self.__imul__(1.0 / other)
        raise RuntimeError(f"Quaternion::Mul::wrong argument type {type(other)}")

    __div__, __rdiv__ = __truediv__, __rtruediv__

    def to_euler_angles(self) -> Vector3:
        # работает
        ax = math.atan2(2.0 * (self.ew * self.ex + self.ey * self.ez), 1.0 -
                        2.0 * (self.ex * self.ex + self.ey * self.ey))
        ay = math.asin (2.0 * (self.ew * self.ey - self.ez * self.ex))
        az = math.atan2(2.0 * (self.ew * self.ez + self.ex * self.ey), 1.0 -
                        2.0 * (self.ey * self.ey + self.ez * self.ez))
        return Vector3(ax, ay, az)

    def rotate(self, vector: Vector3) -> Vector3:
        assert isinstance(vector, Vector3)
        return Vector3(*(((self * Quaternion(0.0, vector.x, vector.y, vector.z)) * self.invert())[1:]))

    def to_rotation_matrix(self) -> Matrix4:
        xx = self.ex * self.ex * 2.0
        xy = self.ex * self.ey * 2.0
        xz = self.ex * self.ez * 2.0

        yy = self.ey * self.ey * 2.0
        yz = self.ey * self.ez * 2.0
        zz = self.ez * self.ez * 2.0

        wx = self.ew * self.ex * 2.0
        wy = self.ew * self.ey * 2.0
        wz = self.ew * self.ez * 2.0
        return Matrix4(1.0 - (yy + zz), xy + wz, xz - wy, 0.0,
                       xy - wz, 1.0 - (xx + zz), yz + wx, 0.0,
                       xz + wy, yz - wx, 1.0 - (xx + yy), 0.0,
                       0.0, 0.0, 0.0, 1.0)

    @classmethod
    def from_euler_angles(cls, roll: float, pitch: float, yaw: float, in_radians: bool = True):
        # работает
        assert all(isinstance(arg, int) or isinstance(arg, float) for arg in (roll, pitch, yaw))
        if in_radians:
            cr: float = math.cos(roll * 0.5)
            sr: float = math.sin(roll * 0.5)
            cp: float = math.cos(pitch * 0.5)
            sp: float = math.sin(pitch * 0.5)
            cy: float = math.cos(yaw * 0.5)
            sy: float = math.sin(yaw * 0.5)
        else:
            cr: float = math.cos(DEG_TO_RAD * roll * 0.5)
            sr: float = math.sin(DEG_TO_RAD * roll * 0.5)
            cp: float = math.cos(DEG_TO_RAD * pitch * 0.5)
            sp: float = math.sin(DEG_TO_RAD * pitch * 0.5)
            cy: float = math.cos(DEG_TO_RAD * yaw * 0.5)
            sy: float = math.sin(DEG_TO_RAD * yaw * 0.5)

        return cls(cr * cp * cy + sr * sp * sy,
                   sr * cp * cy - cr * sp * sy,
                   cr * sp * cy + sr * cp * sy,
                   cr * cp * sy - sr * sp * cy)

    @classmethod
    def from_axis_and_angle(cls, axis: Vector3, angle: float):
        assert isinstance(axis, Vector3)
        assert isinstance(angle, float) or isinstance(angle, int)
        angle *= 0.5
        return cls(math.cos(angle),
                   -axis.x * math.sin(angle),
                   -axis.y * math.sin(angle),
                   -axis.z * math.sin(angle))

    @classmethod
    def from_rotation_matrix(cls, rm: Matrix4):
        assert isinstance(rm, Matrix4)
        qw = math.sqrt(max(0.0, 1.0 + rm.m00 + rm.m11 + rm.m22)) * 0.5
        qx = math.sqrt(max(0.0, 1.0 + rm.m00 - rm.m11 - rm.m22)) * 0.5
        qy = math.sqrt(max(0.0, 1.0 - rm.m00 + rm.m11 - rm.m22)) * 0.5
        qz = math.sqrt(max(0.0, 1.0 - rm.m00 - rm.m11 + rm.m22)) * 0.5

        qx = math.copysign(qx, rm.m21 - rm.m12)
        qy = math.copysign(qy, rm.m02 - rm.m20)
        qz = math.copysign(qz, rm.m10 - rm.m01)
        try:
            norm = 1.0 / math.sqrt(sum(v ** 2 for v in (qw, qx, qy, qz)))
            return cls(qw * norm, qx * norm, qy * norm, qz * norm)
        except ZeroDivisionError as _:
            return cls()

    @staticmethod
    def dot(a, b) -> float:
        assert isinstance(a, Quaternion)
        assert isinstance(b, Quaternion)
        return sum(ai * bi for ai, bi in zip(a, b))

    @classmethod
    def max(cls, a, b):
        assert isinstance(a, Quaternion)
        assert isinstance(b, Quaternion)
        return cls(max(a.ew, b.ew),
                   max(a.ex, b.ex),
                   max(a.ey, b.ey),
                   max(a.ez, b.ez))

    @classmethod
    def min(cls, a, b):
        assert isinstance(a, Quaternion)
        assert isinstance(b, Quaternion)
        return cls(min(a.ew, b.ew),
                   min(a.ex, b.ex),
                   min(a.ey, b.ey),
                   min(a.ez, b.ez))

    @classmethod
    def from_np_array(cls, array: np.ndarray):
        assert isinstance(array, np.ndarray)
        assert array.size == 4
        return cls(*array.flat)

    def to_np_array(self) -> np.ndarray:
        return np.array(tuple(self))


def quaternion_4_test():
    v1 = Quaternion(1, 1, 1, 1)
    v2 = Quaternion(2, 2, 2, 2)
    print(f"Quaternion test")
    print()
    print(f"{v1} + {v2}  = {v1 + v2}")
    print(f"{v1} - {v2}  = {v1 - v2}")
    print(f"{v1} / {v2}  = {v1 / v2}")
    print(f"{v1} * {v2}  = {v1 * v2}")
    print()
    v1_ = Quaternion(1, 1)
    v2_ = Quaternion(2, 2)
    v1 += v2
    print(f"{v1_} += {v2_}  = {v1}")
    v1 -= v2
    print(f"{v1_} -= {v2_}  = {v1}")
    v1 /= v2
    print(f"{v1_} /= {v2_}  = {v1}")
    v1 *= v2
    print(f"{v1_} *= {v2_}  = {v1}")
    print()
    print(f"({v1}, {v2}) = {Quaternion.dot(v1, v2)}")
    print(f" {v1}.magnitude     = {v1.magnitude}")
    print(f" {v1}.magnitude_sqr = {v1.magnitude_sqr}")
    print(f" {v2}.magnitude     = {v2.magnitude}")
    print(f" {v2}.magnitude_sqr = {v2.magnitude_sqr}")
    print(f" {v2}.nparray       = {v2.to_np_array()}")
    print()


if __name__ == "__main__":
    quaternion_4_test()


# if __name__ == "__main__":
#     """
#     Задача:
#     Вектор (0, 1, 0)
#     Кватернион из углов 45, 35, 25 градусов
#     Повернуть вектор кватернионом и сделать обратное преобразование
#     Задача работает нормально
#     """
#     deg_2_rad = math.pi / 180.0
#     rad_2_deg = 180.0 / math.pi
#     q_1: Quaternion = Quaternion.from_euler_angles(45 * deg_2_rad, 35 * deg_2_rad, 25 * deg_2_rad)
#     v = Vector3(0, 1, 0)
#     v_ = q_1.rotate(v)
#
#     print(f"v_rot    : {v_}")  # v_rot    : (0.34618861305875415, 0.8122618069191612, -0.46945095719241614)
#     print(f"v_inv_rot: {q_1.invert().rotate(v)}")  # v_inv_rot: (1e-17, 1.0000000000000004, 0.0)
#     angles = Quaternion.to_euler_angles(q_1)
#     print(f"roll: {angles[0] * rad_2_deg}, pitch: {angles[1] * rad_2_deg}, yaw: {angles[2] * rad_2_deg}")  # (45,35,25)
#     """
#     Задача:
#     Есть направление вектора eY и eZ. Построить ортонормированный базис, сохраняя направление eY
#     Задача работает нормально
#     """
#     y_dir = Vector3(7.07, 7.07, 0)  # пусть это начальное ускорение в состоянии покоя
#     z_dir = Vector3(0.0, 0.0, 1.0)
#     q: Quaternion = Quaternion.from_euler_angles(0, 0, -45 * deg_2_rad)
#     rm = q.to_rotation_matrix()  # совпадает с матрицей поворота на 45 градусов по оси Z
#     print("quaternion to rot m")
#     print(rm)
#     basis = Matrix4.build_basis(y_dir, z_dir)  # строим базис для такой системы (это функция точно верная)
#     # (орты базиса - столбцы матрицы поворота)
#     start_q = Quaternion.from_rotation_matrix(basis)
#     start_angles = Quaternion.to_euler_angles(start_q)  # quaternion_to_euler - работает корректно, см. задачу выше
#
#     q_rot = Quaternion.from_euler_angles(start_angles[0], start_angles[1], start_angles[2])
#
#     qrm = q.to_rotation_matrix()
#
#     print("rot m from vectors")
#     print(basis)
#
#     print("rot m from quaternion")
#     print(qrm)
#     # последние две матрицы должны совпасть
#
#     # g_calib = quaternion_rot(accel_0, (q_rot))
#
#     # g_calib = (ex[0] * y_dir[0] + ex[1] * y_dir[1] + ex[2] * y_dir[2],
#     #            ey[0] * y_dir[0] + ey[1] * y_dir[1] + ey[2] * y_dir[2],
#     #            ez[0] * y_dir[0] + ez[1] * y_dir[1] + ez[2] * y_dir[2])
#     #
#     # print(g_calib)
