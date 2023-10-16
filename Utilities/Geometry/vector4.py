from .common import NUMERICAL_FORMAT_4F as _4F
from dataclasses import dataclass
import numpy as np
import math


@dataclass
class Vector4:
    """
    mutable vector 4d
    """
    __slots__ = ('_x', '_y', '_z', '_w')

    def __iter__(self):
        yield self._x
        yield self._y
        yield self._z
        yield self._w

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def z(self) -> float:
        return self._z

    @property
    def w(self) -> float:
        return self._w

    @x.setter
    def x(self, value: float) -> None:
        self._x = float(value)

    @y.setter
    def y(self, value: float) -> None:
        self._y = float(value)

    @z.setter
    def z(self, value: float) -> None:
        self._z = float(value)

    @w.setter
    def w(self, value: float) -> None:
        self._w = float(value)

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0,  w: float = 0.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __str__(self):
        return f"{{\"x\": {self.x:{_4F}}, \"y\": {self.y:{_4F}}, \"z\": {self.z:{_4F}}, \"w\": {self.w:{_4F}}}}"

    def __neg__(self):
        return Vector4(-self.x, -self.y, -self.z, -self.w)

    def __abs__(self):
        return Vector4(abs(self.x), abs(self.y), abs(self.z), abs(self.w))

    def __add__(self, other):
        if isinstance(other, Vector4):
            return Vector4(self.x + other.x,
                           self.y + other.y,
                           self.z + other.z,
                           self.w + other.w)
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(self.x + other,
                           self.y + other,
                           self.z + other,
                           self.w + other)
        raise RuntimeError(f"Vector4::Add::wrong argument type {type(other)}")

    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Vector4):
            self._x += other.x
            self._y += other.y
            self._z += other.z
            self._w += other.w
            return self
        if isinstance(other, int) or isinstance(other, float):
            self._x += other
            self._y += other
            self._z += other
            self._w += other
            return self
        raise RuntimeError(f"Vector4::IAdd::wrong argument type {type(other)}")

    def __sub__(self, other):
        if isinstance(other, Vector4):
            return Vector4(self.x - other.x,
                           self.y - other.y,
                           self.z - other.z,
                           self.w - other.w)
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(self.x - other,
                           self.y - other,
                           self.z - other,
                           self.w - other)
        raise RuntimeError(f"Vector4::Sub::wrong argument type {type(other)}")

    def __rsub__(self, other):
        if isinstance(other, Vector4):
            return Vector4(other.x - self.x,
                           other.y - self.y,
                           other.z - self.z,
                           other.w - self.w)
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(other - self.x,
                           other - self.y,
                           other - self.z,
                           other - self.w)
        raise RuntimeError(f"Vector4::RSub::wrong argument type {type(other)}")

    def __isub__(self, other):
        if isinstance(other, Vector4):
            self._x -= other.x
            self._y -= other.y
            self._z -= other.z
            self._w -= other.w
            return self
        if isinstance(other, int) or isinstance(other, float):
            self._x -= other
            self._y -= other
            self._z -= other
            self._w -= other
            return self
        raise RuntimeError(f"Vector4::ISub::wrong argument type {type(other)}")

    def __mul__(self, other):
        if isinstance(other, Vector4):
            return Vector4(self.x * other.x,
                           self.y * other.y,
                           self.z * other.z,
                           self.w * other.w)
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(self.x * other,
                           self.y * other,
                           self.z * other,
                           self.w * other)
        raise RuntimeError(f"Vector4::Mul::wrong argument type {type(other)}")

    def __imul__(self, other):
        if isinstance(other, Vector4):
            self._x *= other.x
            self._y *= other.y
            self._z *= other.z
            self._w *= other.w
            return self
        if isinstance(other, int) or isinstance(other, float):
            self._x *= other
            self._y *= other
            self._z *= other
            self._w *= other
            return self
        raise RuntimeError(f"Vector4::IMul::wrong argument type {type(other)}")
                 
    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Vector4):
            return Vector4(self.x / other.x,
                           self.y / other.y,
                           self.z / other.z,
                           self.w / other.w)
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(self.x / other,
                           self.y / other,
                           self.z / other,
                           self.w / other)
        raise RuntimeError(f"Vector4::Div::wrong argument type {type(other)}")

    def __rtruediv__(self, other):
        if isinstance(other, Vector4):
            return Vector4(other.x / self.x,
                           other.y / self.y,
                           other.z / self.z,
                           other.w / self.w)
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(other / self.x,
                           other / self.y,
                           other / self.z,
                           other / self.w)
        raise RuntimeError(f"Vector4::RDiv::wrong argument type {type(other)}")

    def __idiv__(self, other):
        if isinstance(other, Vector4):
            self._x /= other.x
            self._y /= other.y
            self._z /= other.z
            self._w /= other.z
            return self
        if isinstance(other, int) or isinstance(other, float):
            self._x /= other
            self._y /= other
            self._z /= other
            self._w /= other
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
            return Vector4()

    def normalize(self):
        try:
            return Vector4.__imul__(self, 1.0 / self.magnitude)
        except ZeroDivisionError as _:
            return self

    @staticmethod
    def dot(a, b) -> float:
        assert isinstance(a, Vector4)
        assert isinstance(b, Vector4)
        return sum(ai * bi for ai, bi in zip(a, b))

    @classmethod
    def max(cls, a, b):
        assert isinstance(a, Vector4)
        assert isinstance(b, Vector4)
        return cls(max(a.x, b.x), max(a.y, b.y), max(a.z, b.z), max(a.w, b.w))

    @classmethod
    def min(cls, a, b):
        assert isinstance(a, Vector4)
        assert isinstance(b, Vector4)
        return cls(min(a.x, b.x), min(a.y, b.y), min(a.z, b.z), min(a.w, b.w))

    @classmethod
    def from_np_array(cls, array: np.ndarray):
        assert isinstance(array, np.ndarray)
        assert array.size == 4
        return cls(*array.flat)

    def to_np_array(self) -> np.ndarray:
        return np.array(tuple(self))


def vector_4_test():
    v1 = Vector4(1, 1, 1, 1)
    v2 = Vector4(2, 2, 2, 2)
    print(f"Vector4 test")
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
    print(f"v1 = {v1}")
    print(f"v2 = {v2}")
    # print(f"n_v2 = {Vector2.normal(v1)}")
    # print(f"[v1, v2] = {Vector4.cross(v1, v2)}")
    print(f"(v1, v2) = {Vector4.dot(v1, v2)}")
    print(f"v1.magnitude     = {v1.magnitude}")
    print(f"v1.magnitude_sqr = {v1.magnitude_sqr}")
    print(f"v2.magnitude     = {v2.magnitude}")
    print(f"v2.magnitude_sqr = {v2.magnitude_sqr}")
    print(f"v2.nparray       = {v2.to_np_array()}")
    print()

# if __name__ == "__main__":
#     vector_4_test()
