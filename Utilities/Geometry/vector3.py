from .common import NUMERICAL_FORMAT_4F as _4F
from dataclasses import dataclass
import numpy as np
import math


@dataclass
class Vector3:
    """
    mutable vector 3d
    """
    __slots__ = ('_x', '_y', '_z')

    def __iter__(self):
        yield self._x
        yield self._y
        yield self._z

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def z(self) -> float:
        return self._z

    @x.setter
    def x(self, value: float) -> None:
        self._x = float(value)

    @y.setter
    def y(self, value: float) -> None:
        self._y = float(value)

    @z.setter
    def z(self, value: float) -> None:
        self._z = float(value)

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"{{\"x\": {self.x:{_4F}}, \"y\": {self.y:{_4F}}, \"z\": {self.z:{_4F}}}}"

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    def __abs__(self):
        return Vector3(abs(self.x), abs(self.y), abs(self.z))

    def __add__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        if isinstance(other, int) or isinstance(other, float):
            return Vector3(self.x + other, self.y + other, self.z + other)
        raise RuntimeError(f"Vector3::Add::wrong argument type {type(other)}")

    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Vector3):
            self._x += other.x
            self._y += other.y
            self._z += other.z
            return self
        if isinstance(other, int) or isinstance(other, float):
            self._x += other
            self._y += other
            self._z += other
            return self
        raise RuntimeError(f"Vector3::IAdd::wrong argument type {type(other)}")

    def __sub__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        if isinstance(other, int) or isinstance(other, float):
            return Vector3(self.x - other, self.y - other, self.z - other)
        raise RuntimeError(f"Vector3::Sub::wrong argument type {type(other)}")

    def __rsub__(self, other):
        if isinstance(other, Vector3):
            return Vector3(other.x - self.x, other.y - self.y, other.z - self.z)
        if isinstance(other, int) or isinstance(other, float):
            return Vector3(other - self.x, other - self.y, other - self.z)
        raise RuntimeError(f"Vector3::RSub::wrong argument type {type(other)}")

    def __isub__(self, other):
        if isinstance(other, Vector3):
            self._x -= other.x
            self._y -= other.y
            self._z -= other.z
            return self
        if isinstance(other, int) or isinstance(other, float):
            self._x -= other
            self._y -= other
            self._z -= other
            return self
        raise RuntimeError(f"Vector3::ISub::wrong argument type {type(other)}")

    def __mul__(self, other):
        if isinstance(other, Vector3):
            return Vector3(other.x * self.x, other.y * self.y, other.z * self.z)
        if isinstance(other, int) or isinstance(other, float):
            return Vector3(other * self.x, other * self.y, other * self.z)
        raise RuntimeError(f"Vector3::Mul::wrong argument type {type(other)}")

    def __imul__(self, other):
        if isinstance(other, Vector3):
            self._x *= other.x
            self._y *= other.y
            self._z *= other.z
            return self
        if isinstance(other, int) or isinstance(other, float):
            self._x *= other
            self._y *= other
            self._z *= other
            return self
        raise RuntimeError(f"Vector3::IMul::wrong argument type {type(other)}")
                 
    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x / other.x, self.y / other.y, self.z / other.z)
        if isinstance(other, int) or isinstance(other, float):
            return Vector3(self.x / other, self.y / other, self.z / other)
        raise RuntimeError(f"Vector3::Div::wrong argument type {type(other)}")

    def __rtruediv__(self, other):
        if isinstance(other, Vector3):
            return Vector3(other.x / self.x, other.y / self.y, other.z / self.z)
        if isinstance(other, int) or isinstance(other, float):
            return Vector3(other / self.x, other / self.y, other / self.z)
        raise RuntimeError(f"Vector3::RDiv::wrong argument type {type(other)}")

    def __idiv__(self, other):
        if isinstance(other, Vector3):
            self._x /= other.x
            self._y /= other.y
            self._z /= other.z
            return self
        if isinstance(other, int) or isinstance(other, float):
            self._x /= other
            self._y /= other
            self._z /= other
            return self
        raise RuntimeError(f"Vector3::IDiv::wrong argument type {type(other)}")

    __div__, __rdiv__ = __truediv__, __rtruediv__

    @property
    def magnitude_sqr(self):
        return sum(x * x for x in self)

    @property
    def magnitude(self):
        return math.sqrt(self.magnitude_sqr)

    @property
    def normalized(self):
        try:
            return self / self.magnitude
        except ZeroDivisionError as _:
            return Vector3()

    def normalize(self):
        try:
            return self.__imul__(1.0 / self.magnitude)
        except ZeroDivisionError as _:
            return self

    @staticmethod
    def dot(a, b) -> float:
        assert isinstance(a, Vector3)
        assert isinstance(b, Vector3)
        return sum(ai * bi for ai, bi in zip(a, b))

    @classmethod
    def cross(cls, a, b):
        assert isinstance(a, Vector3)
        assert isinstance(b, Vector3)
        return cls(a.z * b.y - a.y * b.z, a.x * b.z - a.z * b.x, a.y * b.x - a.x * b.y)

    @classmethod
    def max(cls, a, b):
        assert isinstance(a, Vector3)
        assert isinstance(b, Vector3)
        return cls(max(a.x, b.x), max(a.y, b.y), max(a.z, b.z))

    @classmethod
    def min(cls, a, b):
        assert isinstance(a, Vector3)
        assert isinstance(b, Vector3)
        return cls(min(a.x, b.x), min(a.y, b.y), min(a.z, b.z))

    @property
    def zxy(self):
        return Vector3(self.z, self.x, self.y)

    @property
    def zyx(self):
        return Vector3(self.z, self.y, self.x)

    @classmethod
    def from_np_array(cls, array: np.ndarray):
        assert isinstance(array, np.ndarray)
        assert array.size == 3
        return cls(*array.flat)

    def to_np_array(self) -> np.ndarray:
        return np.array(tuple(self))


def vector_3_test():
    v1 = Vector3(1, 1, 1)
    v2 = Vector3(2, 2, 2)
    print(f"Vector3 test")
    print(f"v1 = {v1}")
    print(f"v2 = {v2}")
    print(f"v1 + v2 = {v1 + v2}")
    print(f"v1 - v2 = {v1 - v2}")
    print(f"v1 / v2 = {v1 / v2}")
    print(f"v1 * v2 = {v1 * v2}")
    print()
    print(f"v1 = {v1}")
    print(f"v2 = {v2}")
    v1 += v2
    print(f"v1 += v2  = {v1}")
    v1 -= v2
    print(f"v1 -= v2  = {v1}")
    v1 /= v2
    print(f"v1 /= v2  = {v1}")
    v1 *= v2
    print(f"v1 *= v2  = {v1}")
    print()
    print(f"v1 = {v1.normalize()}")
    print(f"v2 = {v2}")
    # print(f"n_v2 = {Vector2.normal(v1)}")
    print(f"[v1, v2] = {Vector3.cross(v1, v2)}")
    print(f"(v1, v2) = {Vector3.dot(v1, v2)}")
    print(f"v1.magnitude     = {v1.magnitude}")
    print(f"v1.magnitude_sqr = {v1.magnitude_sqr}")
    print(f"v2.magnitude     = {v2.magnitude}")
    print(f"v2.magnitude_sqr = {v2.magnitude_sqr}")
    print(f"v2.nparray       = {v2.to_np_array()}")
    print()
# if __name__ == "__main__":
#     vector_3_test()
