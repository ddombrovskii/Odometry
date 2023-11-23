import dataclasses
from .transform_3d import Transform3d
from .vector3 import Vector3


@dataclasses.dataclass
class Ray:
    __slots__ = "_direction", "_origin", "_length"

    def __init__(self, direction: Vector3 = None, origin: Vector3 = None):
        if direction is None and origin is None:
            self._direction: Vector3 = Vector3(0.0, 1.0, 0.0)
            self._origin: Vector3 = Vector3(0.0, 0.0, 0.0)
            self._length: float = 0.0
            return

        if direction is None:
            isinstance(origin, Vector3)
            self._origin: Vector3 = origin
            self._direction: Vector3 = Vector3(0.0, 1.0, 0.0)
            self._length: float = 0.0
            return

        if origin is None:
            isinstance(direction, Vector3)
            self._origin: Vector3 = Vector3(0.0, 0.0, 0.0)
            self._direction: Vector3 = direction.normalize()
            self._length: float = 0.0
            return

        isinstance(direction, Vector3)
        isinstance(origin, Vector3)
        self._direction: Vector3 = direction.normalize()
        self._origin: Vector3 = origin
        self._length: float = 0.0

    def __str__(self) -> str:
        return f"{{\n" \
               f"\t\"origin\"    : {self.origin},\n" \
               f"\t\"direction\" : {self.direction},\n" \
               f"\t\"length\"    : {self.length}" \
               f"\n}}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Ray):
            return False
        if self.direction != other.direction:
            return False
        if self.origin != other.origin:
            return False
        if self.length != other.length:
            return False
        return True

    @property
    def direction(self) -> Vector3:
        return self._direction

    @property
    def origin(self) -> Vector3:
        return self._origin

    @direction.setter
    def direction(self, value: Vector3) -> None:
        assert isinstance(value, Vector3)
        self._direction = value.normalize()

    @origin.setter
    def origin(self, value: Vector3) -> None:
        assert isinstance(value, Vector3)
        self._origin = value

    @property
    def length(self) -> float:
        return self._length

    @length.setter
    def length(self, value: float) -> None:
        assert isinstance(value, float)
        self._length = value

    @property
    def end_point(self) -> Vector3:
        return self.origin + self.direction * self.length

    def transform_ray(self, t: Transform3d):
        self._direction = t.transform_vect(self.direction, 0.0).normalize()
        self._origin    = t.transform_vect(self.origin,    1.0)
        return self

    def transformed_ray(self, t: Transform3d):
        r = Ray(self.direction, self.origin)
        return r.transform_ray(t)
