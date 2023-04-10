from collections import namedtuple
import math


class Vector2(namedtuple('Vector2', 'x, y')):
    """
    immutable vector 3d
    """
    __slots__ = ()

    def __new__(cls, x=0.0, y=0.0, z=0.0):
        return super().__new__(cls, float(x), float(y))

    def __str__(self):
        return f"{{\"x\": {self.x}, \"y\": {self.y}}}"

    def __neg__(self):
        return Vector2(*(val for val in self))

    def __abs__(self):
        return Vector2(abs(self.x), abs(self.y))

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(*(s + o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(*(s + other for s in self))
        raise RuntimeError(f"Vector2::Add::wrong argument type {type(other)}")

    __iadd__ = __add__

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(*(s - o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(*(s - other for s in self))
        raise RuntimeError(f"Vector2::Sub::wrong argument type {type(other)}")

    def __rsub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(*(o - s for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(*(other - s for s in self))
        raise RuntimeError(f"Vector2::Sub::wrong argument type {type(other)}")

    __isub__ = __sub__

    def __mul__(self, other):
        if isinstance(other, Vector2):
            return Vector2(*(s * o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(*(s * other for s in self))
        raise RuntimeError(f"Vector3::Mul::wrong argument type {type(other)}")

    __imul__ = __mul__

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Vector2):
            return Vector2(*(s / o for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(*(s / other for s in self))
        raise RuntimeError(f"Vector2::Div::wrong argument type {type(other)}")

    def __rtruediv__(self, other):
        if isinstance(other, Vector2):
            return Vector2(*(o / s for s, o in zip(self, other)))
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(*(other / s for s in self))
        raise RuntimeError(f"Vector2::Div::wrong argument type {type(other)}")

    __div__, __rdiv__ = __truediv__, __rtruediv__

    def magnitude_sqr(self):
        return sum(x * x for x in self)

    def magnitude(self):
        return math.sqrt(self.magnitude_sqr())

    def normalized(self):
        n = 1.0 / self.magnitude()
        return Vector2(*(x * n for x in self))

    @staticmethod
    def dot(a, b) -> float:
        return sum(ai * bi for ai, bi in zip(a, b))

    @staticmethod
    def cross(a, b) -> float:
        return a.x * b.y - a.y * b.x

    @classmethod
    def max(cls, a, b):
        return cls(max(a.x, b.x), max(a.y, b.y))

    @classmethod
    def min(cls, a, b):
        return cls(min(a.x, b.x), min(a.y, b.y))
