from .transform import Transform
from .vector3 import Vector3


class BoundingBox:

    __slots__ = "__max", "__min"

    def __init__(self):
        self.__max: Vector3 = Vector3(-1e12, -1e12, -1e12)
        self.__min: Vector3 = Vector3(1e12, 1e12, 1e12)

    def __str__(self):
        return f"{{\n" \
               f"\t\"min\": {self.min},\n" \
               f"\t\"max\": {self.max}" \
               f"\n}}"

    @property
    def points(self):
        c = self.center
        s = self.size
        yield Vector3(c.x - s.x, c.y + s.y, c.z - s.z)
        yield Vector3(c.x + s.x, c.y - s.y, c.z - s.z)
        yield Vector3(c.x - s.x, c.y - s.y, c.z - s.z)
        yield Vector3(c.x + s.x, c.y + s.y, c.z - s.z)

        yield Vector3(c.x - s.x, c.y + s.y, c.z + s.z)
        yield Vector3(c.x + s.x, c.y - s.y, c.z + s.z)
        yield Vector3(c.x - s.x, c.y - s.y, c.z + s.z)
        yield Vector3(c.x + s.x, c.y + s.y, c.z + s.z)

    def reset(self):
        self.__max: Vector3 = Vector3(-1e12, -1e12, -1e12)
        self.__min: Vector3 = Vector3(1e12, 1e12, 1e12)

    def encapsulate(self, v: Vector3) -> None:
        self.__max = Vector3.max(self.__max, v)
        self.__min = Vector3.min(self.__min, v)

    def transform_bbox(self, transform: Transform):
        bounds = BoundingBox()
        for pt in self.points:
            bounds.encapsulate(transform.transform_vect(pt))
        return bounds

    def inv_transform_bbox(self, transform: Transform):
        bounds = BoundingBox()
        for pt in self.points:
            bounds.encapsulate(transform.inv_transform_vect(pt))
        return bounds

    @property
    def min(self) -> Vector3:
        return self.__min

    @property
    def max(self) -> Vector3:
        return self.__max

    @property
    def size(self) -> Vector3:
        return self.__max - self.__min

    @property
    def center(self) -> Vector3:
        return (self.__max + self.__min) * 0.5
