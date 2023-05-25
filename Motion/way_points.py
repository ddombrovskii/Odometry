import math
import time
from collections import namedtuple

from Utilities.Geometry import Vector2
from typing import List, Tuple


def _clamp(val, min_, max_):
    return max(min(val, max_), min_)


class WayPoint(namedtuple("WayPoint", "position, error, derror, ierror, time")):
    __slots__ = ()

    def __new__(cls, position: Vector2, error: float, derror: float, ierror: float, time: float):
        return super().__new__(cls, position, error, derror, ierror, time)

    def __str__(self):
        return "{\n" \
               f"\"position\": {self.position},\n" \
               f"\"derror\": {self.derror},\n" \
               f"\"error\": {self.error},\n" \
               f"\"ierror\": {self.ierror},\n" \
               f"\"time\": {self.time}\n" \
               "}"


class WayPoints:
    def __init__(self):
        self._path_points: List[Vector2] = []
        self._way_points: List[WayPoint] = []
        self._point_reach_threshold: float = 0.125
        self._err_prev  = 0.0
        self._err_curr  = 0.0
        self._err_total = 0.0
        self._time_prev = 0.0
        self._time_curr = 0.0
        self._section_curr = 0
        # PID
        self._i_saturation = 10.0
        # max args
        self._response_max: float = 1.0
        # min args
        self._response_min: float = -1.0

        self._threshold: float = 0.1

        self._kp: float = 0.5
        self._ki: float = 0.02
        self._kd: float = 0.01

        self._err_p = 0.0
        self._err_i = 0.0
        self._err_d = 0.0
        self._e_old = 0.0

    @property
    def path_points(self) -> List[Vector2]:
        return self._path_points

    @property
    def way_points(self) -> List[WayPoint]:
        return self._way_points

    @property
    def point_reach_threshold(self) -> float:
        return self._point_reach_threshold

    @point_reach_threshold.setter
    def point_reach_threshold(self, val: float) -> None:
        assert isinstance(val, float)
        self._point_reach_threshold = val  # max(min(val, 1.0), 0.0)

    @property
    def threshold(self) -> float:
        return self._threshold

    @threshold.setter
    def threshold(self, val: float) -> None:
        assert isinstance(val, float)
        self._threshold = val  # max(min(val, 1.0), 0.0)

    @property
    def integral_saturation(self) -> float:
        return self._i_saturation

    @integral_saturation.setter
    def integral_saturation(self, val: float) -> None:
        assert isinstance(val, float)
        self._i_saturation = val

    @property
    def kp(self) -> float:
        return self._kp

    @kp.setter
    def kp(self, val: float) -> None:
        assert isinstance(val, float)
        self._kp = val

    @property
    def kd(self) -> float:
        return self._kd

    @kd.setter
    def kd(self, val: float) -> None:
        assert isinstance(val, float)
        self._kd = val

    @property
    def ki(self) -> float:
        return self._ki

    @ki.setter
    def ki(self, val: float) -> None:
        assert isinstance(val, float)
        self._ki = val

    @property
    def response_max(self) -> float:
        return self._response_max

    @response_max.setter
    def response_max(self, val: float) -> None:
        assert isinstance(val, float)
        self._response_max = max(self._response_min, val)

    @property
    def response_min(self) -> float:
        return self._response_min

    @response_min.setter
    def response_min(self, val: float) -> None:
        assert isinstance(val, float)
        self._response_min = min(self._response_max, val)

    def move(self, current_position: Vector2, target_position: Vector2) -> Tuple[bool, float]:
        if self._section_curr == len(self._path_points) - 1:
            return False, 0.0
        move_next, error = self._compute_error(self._section_curr, current_position, target_position)
        self._err_total += error
        self._err_prev = self._err_curr
        self._err_curr = error
        if len(self._way_points) == 0:
            self._way_points.append(WayPoint(target_position, error, 0.0, self._err_total, time.perf_counter()))
        else:
            t = time.perf_counter()
            dt = t - self._way_points[-1].time
            self._way_points.append(WayPoint(target_position, error,
                                             (error - self._err_prev) / dt, self._err_total * dt, t))

        self._err_p = self.kp * self._err_curr
        self._err_i = _clamp(self._err_i + self.ki * self._err_curr,
                             -self.integral_saturation, self.integral_saturation)
        self._err_d = self.kd * (self._err_curr - self._e_old)
        response = _clamp(self._err_p + self._err_i + self._err_d, self.response_min, self.response_max)
        if move_next:
            self._section_curr += 1
            return True, response
        return True, response

    def _compute_error(self, section_index, position_from: Vector2, position_to: Vector2) -> Tuple[bool, float]:
        p0 = self._path_points[section_index]
        p1 = self._path_points[section_index + 1]
        height0, position0 = WayPoints._distance(position_from, p0, p1)
        height1, position1 = WayPoints._distance(position_to,   p0, p1)
        height = (position0 - position1).magnitude()
        error = (height0 + height1) * height * 0.5
        error *= 1.0 if Vector2.cross(p1 - p0, position_to) > 0.0 else -1.0
        if (position_from - p1).magnitude() <= self._point_reach_threshold:
            return True, error
        return False, error

    @staticmethod
    def _distance(p: Vector2, p1: Vector2, p2: Vector2) -> Tuple[float, Vector2]:
        ort_p1_p2 = p2 - p1
        ort_p__p1 = p  - p1
        direction = ort_p1_p2.normalized()
        position  = Vector2.dot(p - p1, direction) * direction
        height    = (ort_p__p1 - position).magnitude()
        return height, position + p1


from matplotlib import pyplot as plt


def draw_plot(x, y):
    figure, axis = plt.subplots()
    axis.plot(x, y, 'k')


if __name__ == "__main__":
    wp = WayPoints()
    wp.path_points.append(Vector2(0, 0))
    wp.path_points.append(Vector2(5, 0))
    wp.path_points.append(Vector2(8, 0.0))
    x_path = [v.x for v in wp.path_points]
    y_path = [v.y for v in wp.path_points]
    x_way = []
    y_way = []
    way_points = []
    response = []
    errors = []
    n_points = 1000
    dx = 8.0 / (n_points - 1)
    for i in range(n_points):
        x_way.append(dx * i)
        y_way.append(math.cos(dx * i * 5.0) * 0.1)
        way_points.append(Vector2(x_way[-1], y_way[-1]))

    for (p1, p2) in zip(way_points[:-1], way_points[1:]):
        flag, resp = wp.move(p1, p2)
        response.append(resp)
        errors.append(wp.way_points[-1].error) if len(errors) == 0 else errors.append(wp.way_points[-1].error + errors[-1])

    figure, axis = plt.subplots()
    #axis.plot(x_path, y_path, 'k')
    axis.plot(x_way, y_way, 'k')
    axis.plot(x_way[:-1], response, 'g')
    axis.plot(x_way[:-1], errors, 'r')
    plt.show()