from collections import namedtuple
from .vector3 import Vector3
from ..Common import Color


class Voxel(namedtuple('Voxel', 'position, size, color')):
    __slots__ = ()

    def __new__(cls, position: Vector3, size: float = 1.0, color: Color = None):
        return super().__new__(cls, position, size, color if color is not None else Color(125, 125, 125))

    def __str__(self):
        return f"\t{{\n" \
               f"\t\t\"min\":   {self.min},\n" \
               f"\t\t\"max\":   {self.max},\n" \
               f"\t\t\"color\": {self.color}" \
               f"\n\t}}"

    @property
    def points(self):
        c = self.center
        s = 0.5 * self.v_size
        yield Vector3(c.x - s.x, c.y + s.y, c.z - s.z)
        yield Vector3(c.x + s.x, c.y - s.y, c.z - s.z)
        yield Vector3(c.x - s.x, c.y - s.y, c.z - s.z)
        yield Vector3(c.x + s.x, c.y + s.y, c.z - s.z)

        yield Vector3(c.x - s.x, c.y + s.y, c.z + s.z)
        yield Vector3(c.x + s.x, c.y - s.y, c.z + s.z)
        yield Vector3(c.x - s.x, c.y - s.y, c.z + s.z)
        yield Vector3(c.x + s.x, c.y + s.y, c.z + s.z)

    @property
    def min(self) -> Vector3:
        return self.position - self.size * 0.5

    @property
    def max(self) -> Vector3:
        return self.position + self.size * 0.5

    @property
    def v_size(self) -> Vector3:
        return Vector3(self.size, self.size, self.size)

    @property
    def center(self) -> Vector3:
        return self.position

    def contains(self, point: Vector3) -> bool:
        delta = (self.position.x - point.x) * 2.0
        if delta > self.size.x:
            return False
        delta = (self.position.y - point.y) * 2.0
        if delta > self.size.y:
            return False
        delta = (self.position.z - point.z) * 2.0
        if delta > self.size.z:
            return False
        return True

    # def encapsulate(self, point: Vector3) -> bool:
    #     if self.contains(point):
    #         return False
    #
