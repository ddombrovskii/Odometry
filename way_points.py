import math
import struct
import time
from collections import namedtuple

import numpy as np
import serial

from Accelerometer.accelerometer_core.accelerometer_bno055 import write_package, read_package
from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU
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
        self._path_length: List[float]   = [0.0]
        self._way_points: List[WayPoint] = []
        self._curr_path_length = 0.0
        self._point_reach_threshold: float = 0.125
        self._error_delta = 0.0
        self._error_int = 0.0
        self._error = 0.0
        self._time_prev = 0.0
        self._time_curr = 0.0
        self._section_curr = 0
        # PID
        self._i_saturation = 10.0
        # max args
        self._response_max: float = 100.0
        # min args
        self._response_min: float = -100.0

        self._threshold: float = 0.125

        self._kp: float = 0.9999
        self._ki: float = 0.0
        self._kd: float = 0.0

        self._err_p = 0.0
        self._err_i = 0.0
        self._err_d = 0.0
        self._e_old = 0.0

    def add_point(self, x: float, y: float) -> None:
        self._path_points.append(Vector2(x, y))
        if len(self._path_points) == 1:
            return
        self._path_length.append(self._path_length[-1] + (self._path_points[-1] - self._path_points[-2]).magnitude())

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

    def move(self, position: Vector2, direction: Vector2) -> Tuple[bool, float]:
        if self._section_curr == len(self._path_points) - 1:
            return False, 0.0
        move_next, d_error = self._compute_error(self._section_curr, position, direction)
        self._error_delta = d_error - self._error
        self._error = d_error
        self._error_int += self._error

        self._way_points.append(
            WayPoint(position, self._error, self._error_delta, self._error_int, time.perf_counter()))

        self._err_p = self.kp * self._error
        self._err_i = _clamp(self._err_i + self.ki * self._error, -self.integral_saturation, self.integral_saturation)
        self._err_d = self.kd * (self._error - self._e_old)
        response = _clamp(self._err_p + self._err_i + self._err_d, self.response_min, self.response_max)
        if move_next:
            self._section_curr += 1
            return True, response
        return True, response

    def _compute_error(self, section_index, position: Vector2, direction: Vector2) -> Tuple[bool, float]:
        p0 = self._path_points[section_index]
        p1 = self._path_points[section_index + 1]
        self._curr_path_length += (self.way_points[-1].position - position).magnitude() if len(self.way_points) != 0 else 0.0
        # height0, position0 = WayPoints._distance(position_from, p0, p1)
        # height1, position1 = WayPoints._distance(position_to,   p0, p1)
        # error = (height0 + height1) * (height0 + height1) * 0.25
        error = Vector2.cross((p1 - p0).normalized(), direction.normalized())  #  1.0 if Vector2.cross(p1 - p0, position_to) >= 0.0 else -1.0
        if abs(self._curr_path_length - self._path_length[section_index + 1]) <= self._point_reach_threshold:
            return True, -error
        return False, -error

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
    x = np.array([0.0, 1.5, 1.5, 0.0])
    y = np.array([0.0, 0.0, 1.5, 1.5])
    t = np.array([0.0, 0.333, 0.666, 1.0])
    t_interp = np.linspace(0, 1.0, 16)
    x_1 = np.interp(t_interp, t, x)
    y_1 = np.interp(t_interp, t, y)
    for xi, yi in zip(x_1, y_1):
        wp.add_point(xi, yi)
    t = 0.0
    imu = IMU()
    t_0 = 0.0
    while imu.start_time > t:
        t_0 = time.perf_counter()
        imu.update()
        t += time.perf_counter() - t_0

    while imu.calib_time > t:
        t_0 = time.perf_counter()
        imu.update()
        t += time.perf_counter() - t_0

    imu.begin_record("robot_imu_record.json")
    while True:
        direction = Vector2(imu.accelerometer.basis.up.x, imu.accelerometer.basis.up.y)
        position  = Vector2(imu.position.x, imu.position.y)
        flag, signal = wp.move(position, direction)
        message = imu.accelerometer.read_config.to_bytes(1, 'big') + b';' + bytes(str(180.0 + signal * 180.0), 'utf-8')
        # write_package(imu.accelerometer.device, message)
        # time.sleep(0.01)
        # response = read_package(imu.accelerometer.device)
        # status = response[0]
        # if status != 1:
        #     ...
        print(message)
        imu.update()
        if not flag:
            break


