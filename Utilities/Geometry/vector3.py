from .common import NUMERICAL_FORMAT_4F as _4F
from collections import namedtuple
import math


class Vector3(namedtuple('Vector3', 'x, y, z')):
    """
    immutable vector 3d
    """
    __slots__ = ()

    def __new__(cls, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        return super().__new__(cls, float(x), float(y), float(z))

    def __str__(self):
        return f"{{\"x\": {self.x:{_4F}}, \"y\": {self.y:{_4F}}, \"z\": {self.z:{_4F}}}}"

    def __neg__(self):
        return Vector3(*(val for val in self))

    def __abs__(self):
        return Vector3(abs(self.x), abs(self.y), abs(self.z))

    def __add__(self, other):
        if isinstance(other, Vector3):
            return Vector3(*(s + o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector3(*(s + other for s in self))
        raise RuntimeError(f"Vector3::Add::wrong argument type {type(other)}")

    __iadd__ = __add__

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Vector3):
            return Vector3(*(s - o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector3(*(s - other for s in self))
        raise RuntimeError(f"Vector3::Sub::wrong argument type {type(other)}")

    def __rsub__(self, other):
        if isinstance(other, Vector3):
            return Vector3(*(o - s for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector3(*(other - s for s in self))
        raise RuntimeError(f"Vector3::Sub::wrong argument type {type(other)}")

    __isub__ = __sub__

    def __mul__(self, other):
        if isinstance(other, Vector3):
            return Vector3(*(s * o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector3(*(s * other for s in self))
        raise RuntimeError(f"Vector3::Mul::wrong argument type {type(other)}")

    __imul__ = __mul__
                 
    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Vector3):
            return Vector3(*(s / o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector3(*(s / other for s in self))
        raise RuntimeError(f"Vector3::Div::wrong argument type {type(other)}")

    def __rtruediv__(self, other):
        if isinstance(other, Vector3):
            return Vector3(*(o / s for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector3(*(other / s for s in self))
        raise RuntimeError(f"Vector3::Div::wrong argument type {type(other)}")

    __div__, __rdiv__ = __truediv__, __rtruediv__

    def magnitude_sqr(self):
        return sum(x * x for x in self)

    def magnitude(self):
        return math.sqrt(self.magnitude_sqr())

    def normalized(self):
        try:
            n = 1.0 / self.magnitude()
            return Vector3(*(x * n for x in self))
        except ZeroDivisionError as _:
            return Vector3()

    @staticmethod
    def dot(a, b) -> float:
        return sum(ai * bi for ai, bi in zip(a, b))

    @classmethod
    def cross(cls, a, b):
        return cls(a.z * b.y - a.y * b.z, a.x * b.z - a.z * b.x, a.y * b.x - a.x * b.y)

    @classmethod
    def max(cls, a, b):
        return cls(max(a.x, b.x), max(a.y, b.y), max(a.z, b.z))

    @classmethod
    def min(cls, a, b):
        return cls(min(a.x, b.x), min(a.y, b.y), min(a.z, b.z))

    @property
    def zxy(self):
        return Vector3(self.z, self.x, self.y)

    @property
    def zyx(self):
        return Vector3(self.z, self.y, self.x)
