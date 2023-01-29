import random

from cgeo.surface.interpolator import Interpolator
from PIL import Image, ImageFilter, ImageOps
import matplotlib.pyplot as plt
from typing import Tuple, List
from cgeo import Vec2
import numpy as np
import numpy
import math


def _lerp(x_0: float, x_1: float, t):
    return x_0 + (x_1 - x_0) * t


class Attractor:
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self._position: Vec2 = Vec2(x, y)
        self._radius: float = 25
        self._mass: float = 1.0

    @property
    def mass(self) -> float:
        return self._mass

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def position(self) -> Vec2:
        return self._position

    @mass.setter
    def mass(self, m: float) -> None:
        self._mass  = m

    @radius.setter
    def radius(self, r: float) -> None:
        self._radius = r

    @position.setter
    def position(self, p: Vec2) -> None:
        self._position = p

    def field_value(self, x: float, y: float) -> float:
        rho: float = ((self._position.x - x) ** 2 + (self._position.y - y) ** 2) / self.radius
        return 0.0 - math.exp(-rho) * self.mass

    def field_value_derivative(self, x: float, y: float, dx: float = 0.001, dy: float = 0.001) -> Tuple[float, float]:
        return (self.field_value(x + dx, y) - self.field_value(x - dx, y)) * 0.5 / dx, \
               (self.field_value(x, y + dy) - self.field_value(x, y - dy)) * 0.5 / dy

    def attractor_map(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        area = np.zeros((y.size, x.size,), dtype=float)
        for i in range(area.size):
            row, col = divmod(i, x.size)
            area[row, col] = self.field_value(x[col], y[row])
        return area

    def attractor_derivative_map(self, x: np.ndarray, y: np.ndarray,
                                 dx: float = 0.001, dy: float = 0.001) -> np.ndarray:
        area = np.zeros((y.size, x.size,), dtype=float)
        for i in range(area.size):
            row, col = divmod(i, x.size)
            area[row, col] = self.field_value_derivative(y[row], x[col], dx, dy)
        return area


_scans_count = 32
_d_scan_ang = math.pi * 2.0 / (_scans_count - 1)
_sin_scan = [math.sin(_d_scan_ang * i) for i in range(_scans_count)]
_cos_scan = [math.cos(_d_scan_ang * i) for i in range(_scans_count)]


class AreaPenaltyMap:
    def __init__(self, src: str):
        self._dx: float = 0.0001
        self._dy: float = 0.0001
        self._map: Interpolator = None
        self._map_src: str = src
        self._filter_size: float = 5.0
        self._reload_area_map()

    def _reload_area_map(self):
        if self._map is None:
            self._map = Interpolator()
            # self._map.bi_cubic = True
        image_ = ImageOps.grayscale(Image.open(self._map_src))
        image_ = image_.filter(ImageFilter.GaussianBlur(self.filter_size))
        image_.save("map_blured.png")
        image_ = -numpy.asarray(image_, dtype=float) / 255.0
        self._map.control_points = image_
        self._map.save("area_map.json")

    @property
    def dx(self) -> float:
        return self._dx

    @property
    def dy(self) -> float:
        return self._dy

    @dx.setter
    def dx(self, value: float) -> None:
        self._dx = min(abs(value), 1.0 / (self._map.colons - 1))

    @dy.setter
    def dy(self, value: float) -> None:
        self._dy = min(abs(value), 1.0 / (self._map.rows - 1))

    @property
    def filter_size(self) -> float:
        return self._filter_size

    @property
    def width(self) -> float:
        return self._map.width

    @property
    def height(self) -> float:
        return self._map.height

    @property
    def x0(self) -> float:
        return self._map.x_0

    @property
    def y0(self) -> float:
        return self._map.y_0

    @width.setter
    def width(self, value: float) -> None:
        self._map.width = value

    @height.setter
    def height(self, value: float) -> None:
        self._map.height = value

    @x0.setter
    def x0(self, value: float) -> None:
        self._map.x_0 = value

    @y0.setter
    def y0(self, value: float) -> None:
        self._map.y_0 = value

    @filter_size.setter
    def filter_size(self, value: float) -> None:
        self._filter_size = min(max(value, 1.0), 100)
        self._reload_area_map()

    def penalty_value(self, _x: float, _y: float, attractors: List[Attractor] = None) -> float:
        if attractors is None:
            return self._map.interpolate_point(_x, _y)
        attractors_sum = sum(attractor.field_value(_x, _y) for attractor in attractors)
        map_sum = self._map.interpolate_point(_x, _y)
        return _lerp(map_sum, map_sum - attractors_sum, map_sum)

    def penalty_values(self, _x: np.ndarray, _y: np.ndarray, attractors: List[Attractor] = None) -> np.ndarray:
        result = np.zeros((_y.size, _x.size,), dtype=float)
        for i in range(result.size):
            row, col = divmod(i, _x.size)
            result[row, col] = self.penalty_value(_x[col], _y[row], attractors)
        return result

    def penalty_value_derivative(self, _x: float, _y: float, attractors: List[Attractor] = None) -> Vec2:
        return Vec2((self.penalty_value(_x + self.dx, _y, attractors) -
                     self.penalty_value(_x - self.dx, _y, attractors)) * 0.5 / self.dx,
                    (self.penalty_value(_x, _y + self.dy, attractors) -
                     self.penalty_value(_x, _y - self.dy, attractors)) * 0.5 / self.dy)

    def penalty_value_derivative_dir(self, _x: float, _y: float, attractors: List[Attractor] = None) -> Vec2:
        return self.penalty_value_derivative(_x, _y, attractors).normalize()

    def lower_penalty_scan(self, _x0: float, _y0: float, attractors: List[Attractor] = None,
                           sacn_r: float = 0.2) -> Vec2:
        x_curr: float
        y_curr: float
        p_curr = Vec2(_x0, _y0)
        p_min = Vec2(_x0, _y0)
        min_val: float = 1e12
        val: float
        # scan
        for i in range(_scans_count):
            p_curr.x = _x0 + sacn_r * _sin_scan[i]
            p_curr.y = _y0 + sacn_r * _cos_scan[i]
            val = self.penalty_value(p_curr.x, p_curr.y, attractors)
            if val < min_val:
                min_val = val
                p_min.x = p_curr.x
                p_min.y = p_curr.y
        # return p_min
        # gradient p_min -= self.penalty_value_derivative(p_curr.x, p_curr.y, attractors) * 0.01

        # bisect
        p_curr.x = _x0
        p_curr.y = _y0
        n_iters = 0
        pc: Vec2 = Vec2()
        _eps = 1e-6  # 0.5 * math.sqrt(self.dx**2 + self.dy**2)
        direction = Vec2(p_min.x - _x0, p_min.y - _y0)
        m_direction = direction.magnitude
        if m_direction < 1e-3:
            return p_min
        direction /= m_direction
        direction.x *= _eps
        direction.y *= _eps
        while True:
            if n_iters == 8:
                break
            n_iters += 1
            if (p_curr - p_min).magnitude < 0.01 * sacn_r:
                break
            pc = Vec2((p_curr.x + p_min.x) * 0.5, (p_curr.y + p_min.y) * 0.5)
            if self.penalty_value(pc.x + direction.x, pc.y + direction.y, attractors) > \
               self.penalty_value(pc.x - direction.x, pc.y - direction.y, attractors):
                p_min.x = pc.x
                p_min.y = pc.y
                continue
            p_curr.x = pc.x
            p_curr.y = pc.y
        return pc

    def area_scan(self, _x0: float, _y0: float, attractors: List[Attractor] = None,
                  n_steps: int = 2024, accuracy: float = 0.225) -> List[Vec2]:
        way_points: List[Vec2] = [Vec2(_x0, _y0)]
        curr_iter: int = 0
        while True:
            pt = way_points[-1]
            pt_new = self.lower_penalty_scan(pt.x, pt.y, attractors, accuracy)
            way_points.append(pt_new)
            curr_iter += 1
            if curr_iter == n_steps:
                break
            do_break = False
            for attractor in attractors:
                if (way_points[-1] - attractor.position).magnitude < accuracy:
                    do_break = True
                    break

            if do_break:
                break
        print(f"way_points count {len(way_points)}")
        return way_points

"""
def area_map_gradient(_x0: float, _y0: float, _map: Interpolator, attractors: List[Attractor],
                      n_steps: int = 10024, accuracy: float = 1e-6) -> List[Vec2]:
    way_points: List[Vec2] = [Vec2(_x0, _y0)]
    curr_iter: int = -1
    while True:
        pt = way_points[-1]
        d_xy = area_map_derivative_identity(pt.x, pt.y, _map, attractors) * 0.01
        print(d_xy)
        way_points.append(Vec2(pt.x - d_xy.x, pt.y - d_xy.y))
        curr_iter += 1
        if curr_iter == n_steps:
            break
        if (way_points[-1] - way_points[-2]).magnitude < accuracy:
            break
    return way_points

"""


def curve_seg_interpolate_(p0: Tuple[float, float], dp0: Tuple[float, float],
                           dp1: Tuple[float, float], n_points: int = 9):
    def _quad_f(_t, a, b, c) ->  float:
        return _t * _t * a + _t * b + c
    dt = 1.0 / (n_points - 1)

    t = [dt  * i for i in range(n_points)]
    ax = 0.5 * (dp1[0] - dp0[0])
    ay = 0.5 * (dp1[1] - dp0[1])
    return [_quad_f(ti, ax, dp0[0], p0[0]) for ti in t], \
           [_quad_f(ti, ay, dp0[1], p0[1]) for ti in t]


def curve_seg_interpolate(dp1: Tuple[float, float],
                          p1: Tuple[float, float],
                          p2: Tuple[float, float], n_points: int = 9) ->\
        Tuple[List[float], List[float], Tuple[float, float]]:

    def _quad_f(_t, a, b, c) ->  float:
        return _t * _t * a + _t * b + c

    dt = 1.0 / (n_points - 1)
    cx_1, cy_1, cz_1 = (p2[0] - p1[0] - dp1[0]), dp1[0], p1[0]
    cx_2, cy_2, cz_2 = (p2[1] - p1[1] - dp1[1]), dp1[1], p1[1]
    x = [_quad_f(dt  * i, cx_1, cy_1, cz_1) for i in range(n_points)]
    y = [_quad_f(dt  * i, cx_2, cy_2, cz_2) for i in range(n_points)]
    return x, y, ((x[-1] - x[-2]) / dt, (y[-1] - y[-2]) / dt)


def interpolate_curve(points: List[Tuple[float, float]], segment_steps: int = 32) -> Tuple[List[float], List[float]]:
    n_points = len(points)
    xs = []
    ys = []
    dp = (1.0, 2.0)
    for i in range(0, n_points-1):
        p1 = points[i]
        p2 = points[min(i + 1, n_points - 1)]
        x, y, dp = curve_seg_interpolate(dp, p1, p2, segment_steps)
        xs.extend(x)
        ys.extend(y)
    return xs, ys


if __name__ == "__main__":
    pnts = [(1.0, 1.0), (2.0, 2.0), (3.0, 1.0), (4.0, -2.0), (5.0, 1.0),  (3.0, 2.0), (10, -1)]
    x, y = interpolate_curve(pnts)
    plt.plot(x, y, 'r')
    # plt.plot(x, y, 'r*')
    [plt.plot(px, py, "go") for (px, py) in pnts]
    plt.show()
    start_pt   = Vec2(0, 3)
    start_pt1  = Vec2(1.6, 9.8)
    start_pt2  = Vec2(0, 7.7)
    finish_pt = Vec2(9.8, 6.6)
    exit(111)
    area_map = AreaPenaltyMap('map1.png')
    area_map.width  = 10.0
    area_map.height = 10.0
    x = np.linspace(0.0, 10.0, 512)
    attr  = Attractor(finish_pt.x, finish_pt.y)
    attr.mass = 100
    attr.radius = 40.0
    attr1 = Attractor(6.0, 9.0)
    attr1.radius = 0.5
    attr1.mass = 2
    #
    wps1 = area_map.area_scan(start_pt.x, start_pt.y, [attr, attr1])
    wps2 = area_map.area_scan(start_pt1.x, start_pt1.y, [attr, attr1])
    wps3 = area_map.area_scan(start_pt2.x, start_pt2.y, [attr, attr1])
    attr.mass = 1.0
    attr.radius = 5.0
    z = area_map.penalty_values(x, x, [attr, attr1])

    plt.imshow(np.flipud(z), extent=[area_map.x0, area_map.x0 + area_map.width,
                                     area_map.y0, area_map.y0 + area_map.height])
    x_wps1 = [v.x for v in wps1]
    y_wps1 = [v.y for v in wps1]
    plt.plot(x_wps1, y_wps1, 'r')

    x_wps2 = [v.x for v in wps2]
    y_wps2 = [v.y for v in wps2]
    plt.plot(x_wps2, y_wps2, 'g')

    x_wps3 = [v.x for v in wps3]
    y_wps3 = [v.y for v in wps3]
    plt.plot(x_wps3, y_wps3, 'b')

    plt.plot( start_pt.x,  start_pt.y, 'or')
    plt.plot( start_pt1.x,  start_pt1.y, 'og')
    plt.plot( start_pt2.x,  start_pt2.y, 'ob')
    plt.plot(finish_pt.x, finish_pt.y, 'ok')
    phi = np.linspace(0, 2 * np.pi, 16)
    plt.show()

