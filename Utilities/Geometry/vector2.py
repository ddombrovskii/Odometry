from .common import NUMERICAL_FORMAT_4F as _4F, NUMERICAL_ACCURACY
from collections import namedtuple
import math


class Vector2(namedtuple('Vector2', 'x, y')):
    """
    immutable vector 3d
    """
    __slots__ = ()

    def __new__(cls, x: float = 0.0, y: float = 0.0):
        return super().__new__(cls, float(x), float(y))

    def __str__(self):
        return f"{{\"x\": {self.x:{_4F}}, \"y\": {self.y:{_4F}}}}"

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
        try:
            n = 1.0 / self.magnitude()
            return Vector2(*(x * n for x in self))
        except ZeroDivisionError as _:
            return Vector2()

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

    @classmethod
    def normal(cls, v):
        """
        :param v:
        :return: возвращает единичный вектор перпендикулярный заданному.
        """
        if v.x == 0.0:
            return cls(1.0 if v.y >= 0.0 else -1.0, 0.0)
        if v.y == 0.0:
            return cls(0, -1.0 if v.y >= 0.0 else 1.0)
        sign: float = 1.0 if v.x / v.y >= 0.0 else -1.0
        dx: float = 1.0 / v.x
        dy: float = -1.0 / v.y
        sign /= math.sqrt(dx * dx + dy * dy)
        return cls(dx * sign, dy * sign)

    @staticmethod
    def overlay(a1, a2, b1, b2):
        da_db = abs(a2 - a1) + abs(b2 - b1)
        dc = abs((a1 + a2) - (b2 + b1))
        if dc.x > da_db.x:
            return False
        if dc.y > da_db.y:
            return False
        return True

    @classmethod
    def intersect_lines(cls, pt1, pt2, pt3, pt4):
        """
        Определяет точку пересечения двух линий, проходящих через точки pt1, pt2 и pt3, pt4 для первой и второй\n
        соответственно.\n
        :param pt1: вектор - пара (x, y), первая точка первой линии.
        :param pt2: вектор - пара (x, y), вторая точка первой линии.
        :param pt3: вектор - пара (x, y), первая точка второй линии.
        :param pt4: вектор - пара (x, y), вторая точка второй линии.
        :return: переселись или нет, вектор - пара (x, y).
        """
        da = cls(pt2.x - pt1.x, pt2.y - pt1.y)
        db = cls(pt4.x - pt3.x, pt4.y - pt3.y)
        det = Vector2.cross(da, db)
        if abs(det) < 1e-5:
            # if Vector2.overlay(pt1, pt2, pt3, pt4):
            #     return sum((pt1, pt2, pt3, pt4)) * 0.25
            return None
        det = 1.0 / det
        x = Vector2.cross(pt1, da)
        y = Vector2.cross(pt3, db)
        return cls((y * da.x - x * db.x) * det, (y * da.y - x * db.y) * det)
