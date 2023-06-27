from .common import NUMERICAL_FORMAT_4F as _4F
from collections import namedtuple
import math


class Vector4(namedtuple('Vector4', 'x, y, z w')):
    """
    immutable vector 3d
    """
    __slots__ = ()

    def __new__(cls, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 0.0):
        return super().__new__(cls, float(x), float(y), float(z), float(w))

    def __str__(self):
        return f"{{\"x\": {self.x:{_4F}}, \"y\": {self.y:{_4F}}, \"z\": {self.z}, \"w\": {self.w:{_4F}}}}"

    def __neg__(self):
        return Vector4(*(val for val in self))

    def __abs__(self):
        return Vector4(abs(self.x), abs(self.y), abs(self.z), abs(self.w))

    def __add__(self, other):
        if isinstance(other, Vector4):
            return Vector4(*(s + o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(*(s + other for s in self))
        raise RuntimeError(f"Vector4::Add::wrong argument type {type(other)}")

    __iadd__ = __add__

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Vector4):
            return Vector4(*(s - o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(*(s - other for s in self))
        raise RuntimeError(f"Vector4::Sub::wrong argument type {type(other)}")

    def __rsub__(self, other):
        if isinstance(other, Vector4):
            return Vector4(*(o - s for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(*(other - s for s in self))
        raise RuntimeError(f"Vector4::Sub::wrong argument type {type(other)}")

    __isub__ = __sub__

    def __mul__(self, other):
        if isinstance(other, Vector4):
            return Vector4(*(s * o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(*(s * other for s in self))
        raise RuntimeError(f"Vector4::Mul::wrong argument type {type(other)}")

    __imul__ = __mul__
                 
    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Vector4):
            return Vector4(*(s / o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(*(s / other for s in self))
        raise RuntimeError(f"Vector4::Div::wrong argument type {type(other)}")

    def __rtruediv__(self, other):
        if isinstance(other, Vector4):
            return Vector4(*(o / s for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(*(other / s for s in self))
        raise RuntimeError(f"Vector4::Div::wrong argument type {type(other)}")

    __div__, __rdiv__ = __truediv__, __rtruediv__

    def magnitude_sqr(self):
        return sum(x * x for x in self)

    def magnitude(self):
        return math.sqrt(self.magnitude_sqr())

    def normalized(self):
        try:
            n = 1.0 / self.magnitude()
            return Vector4(*(x * n for x in self))
        except ZeroDivisionError as _:
            return Vector4()

    @staticmethod
    def dot(a, b) -> float:
        return sum(ai * bi for ai, bi in zip(a, b))

    @classmethod
    def max(cls, a, b):
        return cls(max(a.x, b.x), max(a.y, b.y), max(a.z, b.z), max(a.w, b.w))

    @classmethod
    def min(cls, a, b):
        return cls(min(a.x, b.x), min(a.y, b.y), min(a.z, b.z), min(a.w, b.w))