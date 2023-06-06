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


class WayPoint:
    def __init__(self, point: Vector2):
        self._point = point
        self.point_prev = None
        self.point_next = None

    def __str__(self):
        if (not self.has_next) and (not self.has_prev):
            return f"{{\n" \
                   f"\t\"curr\": {self.point},\n" \
                   f"}}"

        if not self.has_next:
            return f"{{\n" \
                   f"\t\"prev\": {self.point_prev},\n" \
                   f"\t\"curr\": {self.point}\n" \
                   f"}}"

        if not self.has_prev:
            return f"{{\n" \
                   f"\t\"curr\": {self.point},\n" \
                   f"\t\"prev\": {self.point_next}\n" \
                   f"}}"

        return f"{{\n" \
               f"\t\"prev\": {Vector2() if self.point_prev is None else self.point_prev},\n" \
               f"\t\"curr\": {self.point},\n" \
               f"\t\"next\": {Vector2() if self.point_next is None else self.point_next}\n" \
               f"}}"

    @property
    def has_next(self) -> bool:
        return not(self.point_next is None)

    @property
    def has_prev(self) -> bool:
        return not (self.point_prev is None)

    @property
    def point(self) -> Vector2:
        return self._point


class GridMap:
    def __init__(self, way_points):
        assert isinstance(way_points, list)
        assert len(way_points) != 0
        assert isinstance(way_points[0], WayPoint)

        self._cell_dxdy: Vector2 = Vector2(0.1, 0.1)
        self._origin: Vector2 = Vector2(0., 0.)
        self._size: Vector2 = Vector2(0., 0.)
        self._way_points: List[WayPoint] = way_points
        self._cells = {}

    def point_within(self, pt: Vector2):
        tmp = pt.point.x - self.x0
        if tmp < 0 or tmp > self.width:
            return False
        tmp = pt.point.y - self.y0
        if tmp < 0 or tmp > self.height:
            return False
        return True

    def pt_index(self, pt: Vector2):
        if not self.point_within(pt):
            return -1, -1
        int((pt.x - self.x0) / self.dx), int((pt.y - self.y0) / self.dy)

    def _link_points(self):
        for index in range(1, len(self._way_points) - 1, 1):
            pt = self._way_points[index]
            if not self.point_within(pt.point):
                del self._way_points[index]
                continue
            pt.point_prev = self._way_points[index - 1]
            pt.point_next = self._way_points[index + 1]

        pt = self._way_points[0]
        if not self.point_within(pt.point):
            del self._way_points[0]

        pt = self._way_points[-1]
        if not self.point_within(pt.point):
            del self._way_points[-1]

    def _register_points(self):
        for pt in self._way_points:
            row_col = self.pt_index(pt.point)
            if row_col in self._cells:
                self._cells[row_col].append(pt)
                continue
            self._cells.update({row_col: [pt]})

    def _rebuild(self):
        self._link_points()
        self._register_points()

    @staticmethod
    def _get_closest_in_cell(cell: List[WayPoint], point: Vector2):
        dist_min = 1e32
        pt_min = None
        for p in cell:
            dist_curr = (p.point - point).magnitude()
            if dist_curr > dist_min:
                continue
            dist_min = dist_curr
            pt_min = p
        return pt_min

    def closer_pt(self, pt: Vector2):
        row_col = self.pt_index(pt)
        if row_col in self._cells:
            return self._get_closest_in_cell(self._cells[row_col], pt)

        search_area = 0
        cells = []
        while True:
            search_area += 2
            for row in range(row_col[0] - search_area // 2, row_col[0] + search_area // 2, 1):
                for col in range(row_col[1] - search_area // 2, row_col[1] + search_area // 2, 1):
                    if (row, col) not in self._cells:
                        continue
                    cells.append(self._cells[(row, col)])
            if len(cells) == 0:
                continue

        points = [self._get_closest_in_cell(cell, pt) for cell in cells]
        dist_min = 1e32
        pt_min = None
        for p in points:
            dist_curr = (p.point - pt).magnitude()
            if dist_curr > dist_min:
                continue
            dist_min = dist_curr
            pt_min = p
        return pt_min

    @property
    def width(self) -> float:
        return self._size.x

    @property
    def height(self) -> float:
        return self._size.y

    @width.setter
    def width(self, value: float) -> None:
        self._size = Vector2(min(max(1.0, value), 1000.0), self.height)

    @height.setter
    def height(self, value: float) -> None:
        self._size = Vector2(self.width, min(max(1.0, value), 1000.0))

    @property
    def x0(self) -> float:
        return self._origin.x

    @property
    def y0(self) -> float:
        return self._origin.y

    @x0.setter
    def x0(self, value: float) -> None:
        self._origin = Vector2(value, self.height)

    @y0.setter
    def y0(self, value: float) -> None:
        self._origin = Vector2(self.width, value)

    @property
    def dx(self) -> float:
        return self._cell_dxdy.x

    @property
    def dy(self) -> float:
        return self._cell_dxdy.y


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


