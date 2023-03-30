from Utilities import Vector2


def _clamp(val, max_, min_):
    return max(min(val, max_), min_)


class PID:
    def __init__(self):
        # max args
        self._kp_max: float = 10.0
        self._ki_max: float = 1000.0
        self._kd_max: float = 1000.0
        # min args
        self._kp_min: float = -10.0
        self._ki_min: float = -1000.0
        self._kd_min: float = -1000.0

        self._threshold: float = 0.1

        self._kp: float = 0.5
        self._ki: float = 0.01
        self._kd: float = 5.0

        self._velocity:     float = 60

        self._p = 0.0
        self._i = 0.0
        self._d = 0.0
        self._e_old = 0.0

    @property
    def threshold(self) -> float:
        return self._threshold

    @threshold.setter
    def threshold(self, val: float) -> None:
        self._threshold = val  # max(min(val, 1.0), 0.0)

    @property
    def velocity(self) -> float:
        return self._velocity

    @velocity.setter
    def velocity(self, val: float) -> None:
        self._velocity = val if val > 0.0 else 0.0

    @property
    def kp(self) -> float:
        return self._kp

    @kp.setter
    def kp(self, val: float) -> None:
        self._kp = _clamp(val, self._kp_min, self._kp_max)

    @property
    def kd(self) -> float:
        return self._kd

    @kd.setter
    def kd(self, val: float) -> None:
        self._kd = _clamp(val, self._kd_min, self._kd_max)

    @property
    def ki(self) -> float:
        return self._ki

    @ki.setter
    def ki(self, val: float) -> None:
        self._ki = _clamp(val, self._ki_min, self._ki_max)

    @property
    def ki_max(self) -> float:
        return self._ki_max

    @ki_max.setter
    def ki_max(self, val: float) -> None:
        self._ki_max = max(self._ki_min, val)

    @property
    def kd_max(self) -> float:
        return self._kd_max

    @kd_max.setter
    def kd_max(self, val: float) -> None:
        self._kd_max = max(self._kd_min, val)

    @property
    def kp_max(self) -> float:
        return self._kp_max

    @kp_max.setter
    def kp_max(self, val: float) -> None:
        self._kp_max = max(self._kp_min, val)

    @property
    def ki_min(self) -> float:
        return self._ki_min

    @ki_min.setter
    def ki_min(self, val: float) -> None:
        self._ki_min = min(val, self._ki_max)

    @property
    def kd_min(self) -> float:
        return self._kd_min

    @kd_min.setter
    def kd_min(self, val: float) -> None:
        self._kd_min = min(self._kd_max, val)

    @property
    def kp_min(self) -> float:
        return self._kp_min

    @kp_min.setter
    def kp_min(self, val: float) -> None:
        self._kp_min = min(self._kp_max, val)

    def __call__(self, sensor_value: float) -> Vector2:
        e = sensor_value - self._threshold
        self._p = _clamp(self.kp * e, self.kp_min, self.kp_max)
        self._i = _clamp(self._i + self.ki * e, self.ki_min, self.ki_max)
        self._d = self.kd * (e - self._e_old)
        u = self._p + self._i + self._d
        return Vector2(self._velocity + u, self._velocity - u)

    def __str__(self):
        return f"{{\n" \
               f"\t\"kp\": {self.kp},\n" \
               f"\t\"ki\": {self.ki},\n" \
               f"\t\"kp_max\": {self.kp_max},\n" \
               f"\t\"ki_max\": {self.ki_max},\n" \
               f"\t\"kd_max\": {self.kd_max},\n" \
               f"\t\"kp_min\": {self.kp_min},\n" \
               f"\t\"ki_min\": {self.ki_min},\n" \
               f"\t\"kd_min\": {self.kd_min},\n" \
               f"\t\"threshold\" : {self.threshold},\n" \
               f"\t\"velocity\"  : {self.velocity}\n" \
               f"}}"
