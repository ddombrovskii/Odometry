from typing import Union

from matplotlib import pyplot as plt

from .transform_2d import Transform2d
from .vector2 import Vector2
from .common import *


class BoundingRect:
    __slots__ = "_max", "_min"

    def __init__(self):
        self._max: Vector2 = Vector2(NUMERICAL_MIN_VALUE, NUMERICAL_MIN_VALUE)
        self._min: Vector2 = Vector2(NUMERICAL_MAX_VALUE, NUMERICAL_MAX_VALUE)

    def __str__(self):
        return f"{{\n" \
               f"\t\"min\": {self.min},\n" \
               f"\t\"max\": {self.max}" \
               f"\n}}"

    def reset(self):
        self._max: Vector2 = Vector2(-1e12, -1e12)
        self._min: Vector2 = Vector2( 1e12, 1e12)

    @property
    def points(self):
        c = self.center
        s = self.size
        yield Vector2(c.x - s.x * 0.5, c.y + s.y * 0.5)
        yield Vector2(c.x - s.x * 0.5, c.y - s.y * 0.5)
        yield Vector2(c.x + s.x * 0.5, c.y - s.y * 0.5)
        yield Vector2(c.x + s.x * 0.5, c.y + s.y * 0.5)
        yield Vector2(c.x - s.x * 0.5, c.y + s.y * 0.5)

    def encapsulate(self, v: Vector2) -> None:
        if v.x > self._max.x:
            self._max.x = v.x
        if v.y > self._max.y:
            self._max.y = v.y
        if v.x < self._min.x:
            self._min.x = v.x
        if v.y < self._min.y:
            self._min.y = v.y

    def transform_bbox(self, transform: Transform2d):
        bounds = BoundingRect()
        for pt in self.points:
            bounds.encapsulate(transform.transform_vect(pt))
        return bounds

    def inv_transform_bbox(self, transform: Transform2d):
        bounds = BoundingRect()
        for pt in self.points:
            bounds.encapsulate(transform.inv_transform_vect(pt))
        return bounds

    @property
    def min(self) -> Vector2:
        return self._min

    @property
    def max(self) -> Vector2:
        return self._max

    @property
    def size(self) -> Vector2:
        return self._max - self._min

    @size.setter
    def size(self, value: Union[float, Vector2]) -> None:
        c = self.center
        self._min = c - value * 0.5
        self._max = c + value * 0.5

    @property
    def area(self) -> float:
        return (self.max.x - self.min.x) * (self.max.y - self.min.y)

    @property
    def center(self) -> Vector2:
        return (self._max + self._min) * 0.5

    @center.setter
    def center(self, value: Union[float, Vector2]) -> None:
        s = self.size * 0.5
        self._min = value - s
        self._max = value + s

    def distance(self, point: Vector2):
        orig = self.center
        size = self.size

        x_l = point.x - (orig.x - size.x * 0.5)
        x_r = point.x - (orig.x + size.x * 0.5)

        y_l = point.y - (orig.y - size.y * 0.5)
        y_r = point.y - (orig.y + size.y * 0.5)

        return max(max(abs(y_l), abs(y_r)) - size.y, max(abs(x_l), abs(x_r)) - size.x)

    @classmethod
    def form_center_and_size(cls, position: Vector2, size: Union[float, Vector2]) -> 'BoundingRect':
        br = BoundingRect()
        br.encapsulate(Vector2(position.x - size * 0.5, position.y - size * 0.5))
        br.encapsulate(Vector2(position.x + size * 0.5, position.y + size * 0.5))
        return br

    def draw(self, axes=None, color='k'):
        pts = tuple(self.points)
        x = tuple(v.x for v in pts)
        y = tuple(v.y for v in pts)
        axes = plt.gca() if axes is None else axes
        axes.plot(x, y, color)
        axes.axis('equal')
