from .common import NUMERICAL_FORMAT_4F as _4F, NUMERICAL_ACCURACY
from dataclasses import dataclass
import numpy as np
import math


_X = '_x'
_Y = '_y'


@dataclass
class Vector2:
    """
    mutable vector 4d
    """
    __slots__ = (_X, _Y)

    @property
    def x(self) -> float:
        return self.__getattribute__(_X)

    @property
    def y(self) -> float:
        return self.__getattribute__(_Y)

    @x.setter
    def x(self, value: float) -> None:
        self.__setattr__(_X, float(value))

    @y.setter
    def y(self, value: float) -> None:
        self.__setattr__(_Y, float(value))

    def __init__(self, *args):
        assert len(args) == 2
        for attr, val in zip(Vector2.__slots__, args):
            self.__setattr__(attr, float(val))

    def __iter__(self):
        for attr in Vector2.__slots__:
            yield self.__getattribute__(attr)

    def __eq__(self, other):
        if not isinstance(other, Vector2):
            return False
        return not any(v1 != v2 for v1, v2 in zip(self, other))

    def __str__(self):
        return f"{{\"x\": {self.x:{_4F}}, \"y\": {self.y:{_4F}}}}"

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __abs__(self):
        return Vector2(abs(self.x), abs(self.y))

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(self.x + other, self.y + other)
        raise RuntimeError(f"Vector2::Add::wrong argument type {type(other)}")

    def __iadd__(self, other):
        if isinstance(other, Vector2):
            self.x += other.x
            self.y += other.y
            return self
        if isinstance(other, int) or isinstance(other, float):
            self.x += other
            self.y += other
            return self
        raise RuntimeError(f"Vector2::IAdd::wrong argument type {type(other)}")

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(self.x - other, self.y - other)
        raise RuntimeError(f"Vector2::Sub::wrong argument type {type(other)}")

    def __isub__(self, other):
        if isinstance(other, Vector2):
            self.x -= other.x
            self.y -= other.y
            return self
        if isinstance(other, int) or isinstance(other, float):
            self.x -= other
            self.y -= other
            return self
        raise RuntimeError(f"Vector2::ISub::wrong argument type {type(other)}")

    def __rsub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(other.x - self.x, other.y - self.y)
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(other - self.x, other - self.y)
        raise RuntimeError(f"Vector2::RSub::wrong argument type {type(other)}")

    def __mul__(self, other):
        if isinstance(other, Vector2):
            return Vector2(other.x * self.x, other.y * self.y)
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(other * self.x, other * self.y)
        raise RuntimeError(f"Vector3::Mul::wrong argument type {type(other)}")

    def __imul__(self, other):
        if isinstance(other, Vector2):
            self.x *= other.x
            self.y *= other.y
            return self
        if isinstance(other, int) or isinstance(other, float):
            self.x *= other
            self.y *= other
            return self
        raise RuntimeError(f"Vector2::IMul::wrong argument type {type(other)}")

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x / other.x, self.y / other.y)
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(self.x / other, self.y / other)
        raise RuntimeError(f"Vector2::Div::wrong argument type {type(other)}")

    def __idiv__(self, other):
        if isinstance(other, Vector2):
            self.x /= other.x
            self.y /= other.y
            return self
        if isinstance(other, int) or isinstance(other, float):
            self.x /= other
            self.y /= other
            return self
        raise RuntimeError(f"Vector2::IDiv::wrong argument type {type(other)}")

    def __rtruediv__(self, other):
        if isinstance(other, Vector2):
            return Vector2(other.x / self.x, other.y / self.y)
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(other / self.x, other / self.y)
        raise RuntimeError(f"Vector2::RDiv::wrong argument type {type(other)}")

    __div__, __rdiv__ = __truediv__, __rtruediv__

    @property
    def magnitude_sqr(self) -> float:
        return self.x * self.x + self.y * self.y

    @property
    def magnitude(self) -> float:
        return math.sqrt(self.magnitude_sqr)

    @property
    def normalized(self):
        try:
            return self / self.magnitude
        except ZeroDivisionError as _:
            return Vector2()

    def normalize(self):
        try:
            return Vector2.__imul__(self, 1.0 / self.magnitude)
        except ZeroDivisionError as _:
            return self

    @staticmethod
    def dot(a, b) -> float:
        assert isinstance(a, Vector2)
        assert isinstance(b, Vector2)
        return sum(ai * bi for ai, bi in zip(a, b))

    @staticmethod
    def cross(a, b) -> float:
        assert isinstance(a, Vector2)
        assert isinstance(b, Vector2)
        return a.x * b.y - a.y * b.x

    @classmethod
    def max(cls, a, b):
        assert isinstance(a, Vector2)
        assert isinstance(b, Vector2)
        return cls(max(a.x, b.x), max(a.y, b.y))

    @classmethod
    def min(cls, a, b):
        assert isinstance(a, Vector2)
        assert isinstance(b, Vector2)
        return cls(min(a.x, b.x), min(a.y, b.y))

    @classmethod
    def normal(cls, v):
        assert isinstance(v, Vector2)
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
        assert all(isinstance(v, Vector2) for v in (a1, a2, b1, b2))
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
        assert all(isinstance(v, Vector2) for v in ( pt1, pt2, pt3, pt4))
        da = cls(pt2.x - pt1.x, pt2.y - pt1.y)
        db = cls(pt4.x - pt3.x, pt4.y - pt3.y)
        det = Vector2.cross(da, db)
        if abs(det) < NUMERICAL_ACCURACY:
            # if Vector2.overlay(pt1, pt2, pt3, pt4):
            #     return sum((pt1, pt2, pt3, pt4)) * 0.25
            return None
        det = 1.0 / det
        x = Vector2.cross(pt1, da)
        y = Vector2.cross(pt3, db)
        return cls((y * da.x - x * db.x) * det, (y * da.y - x * db.y) * det)

    @classmethod
    def from_np_array(cls, array: np.ndarray):
        assert isinstance(array, np.ndarray)
        assert array.size == 2
        return cls(*array.flat)

    def to_np_array(self) -> np.ndarray:
        return np.array(tuple(self))


def vector_2_test():
    v1 = Vector2(1, 1)
    v2 = Vector2(2, 2)
    print(f"Vector2 test")
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
    print(f"[v1, v2] = {Vector2.cross(v1, v2)}")
    print(f"(v1, v2) = {Vector2.dot(v1, v2)}")
    print(f"v1.magnitude     = {v1.magnitude}")
    print(f"v1.magnitude_sqr = {v1.magnitude_sqr}")
    print(f"v2.magnitude     = {v2.magnitude}")
    print(f"v2.magnitude_sqr = {v2.magnitude_sqr}")
    print(f"v2.nparray       = {v2.to_np_array()}")
    print()


# if __name__ == "__main__":
#     vector_2_test()

