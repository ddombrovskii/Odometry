from Utilities import Vector2


class CubicRegulator:
    def __init__(self):
        self._threshold: float = 0.1
        self._velocity: float = 60
        self._linear_val: float = 2.0
        self._cubic_val: float = 0.03

    @property
    def velocity(self) -> float:
        return self._velocity

    @velocity.setter
    def velocity(self, val: float) -> None:
        self._velocity = val if val > 0.0 else 0.0

    @property
    def threshold(self) -> float:
        return self._velocity

    @threshold.setter
    def threshold(self, val: float) -> None:
        self._threshold = max(min(val, 1.0), 0.0)

    @property
    def linear_val(self) -> float:
        return self._linear_val

    @linear_val.setter
    def linear_val(self, val: float) -> None:
        self._linear_val = val if abs(val) > 1e-6 else self._linear_val

    @property
    def cubic_val(self) -> float:
        return self._cubic_val

    @cubic_val.setter
    def cubic_val(self, val: float) -> None:
        self._cubic_val = val if abs(val) > 1e-9 else self._linear_val

    def __call__(self, sensor_value: float) -> Vector2:
        e = sensor_value - self._threshold
        u = self._linear_val * e + self._cubic_val * e * e * e
        return Vector2(self._velocity + u, self._velocity - u)

    def __str__(self):
        return f"{{\n" \
               f"\t\"linear_val\": {self.linear_val},\n" \
               f"\t\"cubic_val\" : {self.linear_val},\n" \
               f"\t\"threshold\" : {self.threshold},\n" \
               f"\t\"velocity\"  : {self.velocity}\n" \
               f"}}"
