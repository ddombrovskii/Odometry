from collections import namedtuple
from .vector3 import Vector3
from ..color import Color


class Voxel(namedtuple('Voxel', 'position, size, color')):

    def __new__(cls, position: Vector3, size: float = 1.0, color: Color = None):
        return super().__new__(cls, position, size, color if color is not None else Color(125, 125, 125))

    # def __init__(self):
    #     self.__max: Vector3 = Vector3(-1e12, -1e12, -1e12)
    #     self.__min: Vector3 = Vector3(1e12, 1e12, 1e12)

    def __str__(self):
        return f"\t{{\n" \
               f"\t\t\"min\":   {self.min},\n" \
               f"\t\t\"max\":   {self.max},\n" \
               f"\t\t\"color\": {self.color}" \
               f"\n\t}}"

    @property
    def points(self):
        c = self.center
        s = self.v_size
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
