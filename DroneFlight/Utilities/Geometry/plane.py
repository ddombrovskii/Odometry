from .vector3 import Vector3
from .ray import Ray


class Plane:
    __slots__ = "_normal", "_origin"

    def __init__(self, normal: Vector3 = None, origin: Vector3 = None):
        if normal is None and origin is None:
            self._normal: Vector3 = Vector3(0, 1, 0)
            self._origin: Vector3 = Vector3(0, 0, 0)
            return

        if normal is None:
            isinstance(origin, Vector3)
            self._origin: Vector3 = origin
            self._normal: Vector3 = Vector3(0, 1, 0)
            return

        if origin is None:
            isinstance(normal, Vector3)
            self._origin: Vector3 = Vector3(0, 0, 0)
            self._normal: Vector3 = normal.normalized
            return

        isinstance(normal, Vector3)
        isinstance(origin, Vector3)
        self._normal: Vector3 = normal.normalized
        self._origin: Vector3 = origin

    def __str__(self) -> str:
        return f"{{\n\t\"normal\": {self.normal},\n\t\"origin\": {self.origin}\n}}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Plane):
            return False
        if self.normal != other.normal:
            return False
        if self.origin != other.origin:
            return False
        return True

    def flip(self):
        self._normal *= -1.0
        return self

    def flipped(self):
        return Plane(-self.normal, self.origin)

    @property
    def normal(self) -> Vector3:
        return self._normal

    @property
    def origin(self) -> Vector3:
        return self._origin

    @normal.setter
    def normal(self, value: Vector3) -> None:
        assert isinstance(value, Vector3)
        self._normal = value.normalized

    @origin.setter
    def origin(self, value: Vector3) -> None:
        assert isinstance(value, Vector3)
        self._origin = value

    def distance_to_point(self, point: Vector3) -> float:
        assert isinstance(point, Vector3)
        return Vector3.dot(point, self.normal) - Vector3.dot(self.normal, self.origin)

    def closest_point_on_plane(self, point: Vector3) -> Vector3:
        assert isinstance(point, Vector3)
        o = self.origin
        n = self.normal
        return point - n * Vector3.dot(n, point - o)

    def point_in_front_of_surface(self, point: Vector3) -> bool:
        return self.distance_to_point(point) >= 0

    def intersect_by_ray(self, ray: Ray) -> Ray:
        assert isinstance(ray, Ray)
        ray.length = (Vector3.dot(self.origin, self.normal) -
                      Vector3.dot(ray.origin, self.normal)) / Vector3.dot(ray.direction, self.normal)
        return ray

    @classmethod
    def from_three_points(cls, p1: Vector3, p2: Vector3, p3: Vector3):
        assert isinstance(p1, Vector3)
        assert isinstance(p2, Vector3)
        assert isinstance(p3, Vector3)
        normal = Vector3.cross(p2 - p1, p3 - p1).normalize()
        return cls(normal, p1)

