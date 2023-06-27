from .common import NUMERICAL_FORMAT_4F as _4F
from collections import namedtuple
from .matrix4 import Matrix4
from .vector3 import Vector3
import math


class Quaternion(namedtuple('Quaternion', 'ew, ex, ey, ez')):
    """
    immutable Quaternion
    """
    __slots__ = ()

    def __new__(cls, ew: float = 0.0, ex: float = 0.0, ey: float = 0.0, ez: float = 0.0):
        return super().__new__(cls, float(ew), float(ex), float(ey), float(ez))

    def conj(self):
        return Quaternion(self.ew, -self.ex, -self.ey, -self.ez)

    def magnitude_sqr(self):
        return sum(x * x for x in self)

    def magnitude(self):
        return math.sqrt(self.magnitude_sqr())

    def normalized(self):
        try:
            n2 = 1.0 / self.magnitude()
            return Quaternion(*(x * n2 for x in self))
        except ZeroDivisionError as _:
            return Quaternion()

    def reciprocal(self):
        try:
            n2 = 1.0 / self.magnitude_sqr()
            return Quaternion(*(x * n2 for x in self.conj()))
        except ZeroDivisionError as _:
            return Quaternion()

    def invert(self):
        try:
            n2 = 1.0 / self.magnitude()
            return Quaternion(*(x * n2 for x in self.conj()))
        except ZeroDivisionError as _:
            return Quaternion()

    def __str__(self):
        return f"{{\"ew\": {self.ew:{_4F}}, \"ex\": {self.ex:{_4F}}, \"ey\": {self.ey:{_4F}}, \"ez\": {self.ez:{_4F}}}}"

    def __neg__(self):
        return Quaternion(-self.ew, -self.ex, -self.ey, -self.ez)

    def __add__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(*(s + o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(*(s + other for s in self))
        raise RuntimeError(f"Quaternion::Add::wrong argument type {type(other)}")

    __iadd__ = __add__

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(*(s - o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(*(s - other for s in self))
        raise RuntimeError(f"Quaternion::Sub::wrong argument type {type(other)}")

    def __rsub__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(*(o - s for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(*(other - s for s in self))
        raise RuntimeError(f"Quaternion::Sub::wrong argument type {type(other)}")

    __isub__ = __sub__

    def __mul__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(self[0] * other[0] - self[1] * other[1] - self[2] * other[2] - self[3] * other[3],
                              self[0] * other[1] + self[1] * other[0] - self[2] * other[3] + self[3] * other[2],
                              self[0] * other[2] + self[1] * other[3] + self[2] * other[0] - self[3] * other[1],
                              self[0] * other[3] - self[1] * other[2] + self[2] * other[1] + self[3] * other[0])
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(*(s * other for s in self))

        raise RuntimeError(f"Quaternion::Mul::wrong argument type {type(other)}")

    def __rmul__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(other[0] * self[0] - other[1] * self[1] - other[2] * self[2] - other[3] * self[3],
                              other[0] * self[1] + other[1] * self[0] - other[2] * self[3] + other[3] * self[2],
                              other[0] * self[2] + other[1] * self[3] + other[2] * self[0] - other[3] * self[1],
                              other[0] * self[3] - other[1] * self[2] + other[2] * self[1] + other[3] * self[0])
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(*(s * other for s in self))
        raise RuntimeError(f"Quaternion::Mul::wrong argument type {type(other)}")

    __imul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Quaternion):
            return self.__mul__(other.reciprocal())
        if isinstance(other, int) or isinstance(other, float):
            return Quaternion(*(s / other for s in self))

    def __rtruediv__(self, other):
        return other * self.reciprocal()

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
    def from_euler_angles(cls, roll, pitch, yaw):
        # работает
        cr: float = math.cos(roll * 0.5)
        sr: float = math.sin(roll * 0.5)
        cp: float = math.cos(pitch * 0.5)
        sp: float = math.sin(pitch * 0.5)
        cy: float = math.cos(yaw * 0.5)
        sy: float = math.sin(yaw * 0.5)

        return cls(cr * cp * cy + sr * sp * sy,
                   sr * cp * cy - cr * sp * sy,
                   cr * sp * cy + sr * cp * sy,
                   cr * cp * sy - sr * sp * cy)

    @classmethod
    def from_axis_and_angle(cls, axis: Vector3, angle: float):
        angle *= 0.5
        return cls(           math.cos(angle),
                   -axis[1] * math.sin(angle),
                   -axis[2] * math.sin(angle),
                   -axis[3] * math.sin(angle))

    @classmethod
    def from_rotation_matrix(cls, rm: Matrix4):
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


if __name__ == "__main__":
    """
    Задача:
    Вектор (0, 1, 0)
    Кватернион из углов 45, 35, 25 градусов
    Повернуть вектор кватернионом и сделать обратное преобразование
    Задача работает нормально
    """
    deg_2_rad = math.pi / 180.0
    rad_2_deg = 180.0 / math.pi
    q_1: Quaternion = Quaternion.from_euler_angles(45 * deg_2_rad, 35 * deg_2_rad, 25 * deg_2_rad)
    v = Vector3(0, 1, 0)
    v_ = q_1.rotate(v)

    print(f"v_rot    : {v_}")  # v_rot    : (0.34618861305875415, 0.8122618069191612, -0.46945095719241614)
    print(f"v_inv_rot: {q_1.invert().rotate(v)}")  # v_inv_rot: (1e-17, 1.0000000000000004, 0.0)
    angles = Quaternion.to_euler_angles(q_1)
    print(f"roll: {angles[0] * rad_2_deg}, pitch: {angles[1] * rad_2_deg}, yaw: {angles[2] * rad_2_deg}")  # (45,35,25)
    """
    Задача:
    Есть направление вектора eY и eZ. Построить ортонормированный базис, сохраняя направление eY
    Задача работает нормально
    """
    y_dir = Vector3(7.07, 7.07, 0)  # пусть это начальное ускорение в состоянии покоя
    z_dir = Vector3(0.0, 0.0, 1.0)
    q: Quaternion = Quaternion.from_euler_angles(0, 0, -45 * deg_2_rad)
    rm = q.to_rotation_matrix()  # совпадает с матрицей поворота на 45 градусов по оси Z
    print("quaternion to rot m")
    print(rm)
    basis = Matrix4.build_basis(y_dir, z_dir)  # строим базис для такой системы (это функция точно верная)
    # (орты базиса - столбцы матрицы поворота)
    start_q = Quaternion.from_rotation_matrix(basis)
    start_angles = Quaternion.to_euler_angles(start_q)  # quaternion_to_euler - работает корректно, см. задачу выше

    q_rot = Quaternion.from_euler_angles(start_angles[0], start_angles[1], start_angles[2])

    qrm = q.to_rotation_matrix()

    print("rot m from vectors")
    print(basis)

    print("rot m from quaternion")
    print(qrm)
    # последние две матрицы должны совпасть

    # g_calib = quaternion_rot(accel_0, (q_rot))

    # g_calib = (ex[0] * y_dir[0] + ex[1] * y_dir[1] + ex[2] * y_dir[2],
    #            ey[0] * y_dir[0] + ey[1] * y_dir[1] + ey[2] * y_dir[2],
    #            ez[0] * y_dir[0] + ez[1] * y_dir[1] + ez[2] * y_dir[2])
    # 
    # print(g_calib)