from Utilities import Vector2


class LinearRegulator:
    def __init__(self):
        self._threshold: float = 0.1
        self._velocity: float = 60.0
        self._linear_val: float = 2.0

    @property
    def velocity(self) -> float:
        return self._velocity

    @velocity.setter
    def velocity(self, val: float) -> None:
        self._velocity = val if val > 0.0 else 0.0

    @property
    def threshold(self) -> float:
        return self._threshold

    @threshold.setter
    def threshold(self, val: float) -> None:
        self._threshold = max(min(val, 1.0), 0.0)

    @property
    def linear_val(self) -> float:
        return self._velocity

    @linear_val.setter
    def linear_val(self, val: float) -> None:
        self._linear_val = val if abs(val) > 1e-6 else self._linear_val

    def __call__(self, sensor_value: float) -> Vector2:
        u = self._linear_val * (sensor_value - self._threshold)
        return Vector2(self._velocity + u, self._velocity - u)

    def __str__(self):
        return f"{{\n" \
               f"\t\"linear_val\": {self.linear_val},\n" \
               f"\t\"threshold\" : {self.threshold},\n" \
               f"\t\"velocity\"  : {self.velocity}\n" \
               f"}}"
