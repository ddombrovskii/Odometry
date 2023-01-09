from typing import List, Tuple, Callable
from cgeo.filtering import RealTimeFilter
import matplotlib.pyplot as plt
from cgeo.vectors import Vec3
import dataclasses
import numpy as np
import json


@dataclasses.dataclass
class WayPoint:
    acceleration: Vec3
    velocity: Vec3
    position: Vec3
    ang_velocity: Vec3
    angle: Vec3
    time_value: float
    time_delta: float


@dataclasses.dataclass
class AccelerometerLog:
    device_name: str
    log_time_start: str
    way_points: List[WayPoint]


def read_accelerometer_log(path_2_json: str) -> AccelerometerLog:
    with open(path_2_json) as input_json:
        raw_json = json.load(input_json)
        way_points = [] * len(raw_json['way_points'])
        v = Vec3(0.0)
        p = Vec3(0.0)

        _filter_x = RealTimeFilter()
        _filter_x.mode = 2
        _filter_y = RealTimeFilter()
        _filter_y.mode = 2
        _filter_z = RealTimeFilter()
        _filter_z.mode = 2

        _filter_o_x = RealTimeFilter()
        _filter_o_x.mode = 2
        _filter_o_y = RealTimeFilter()
        _filter_o_y.mode = 2
        _filter_o_z = RealTimeFilter()
        _filter_o_z.mode = 2

        for item in raw_json['way_points']:
            a = Vec3(_filter_x.filter(float(item["acceleration"]["x"])),
                     _filter_y.filter(float(item["acceleration"]["y"])),
                     _filter_z.filter(float(item["acceleration"]["z"])))
            o = Vec3(_filter_o_x.filter(float(item["angles_velocity"]["x"])),
                     _filter_o_y.filter(float(item["angles_velocity"]["y"])),
                     _filter_o_z.filter(float(item["angles_velocity"]["z"])))
            o_ = Vec3(_filter_o_x.filter(float(item["angles"]["x"])),
                      _filter_o_y.filter(float(item["angles"]["y"])),
                      _filter_o_z.filter(float(item["angles"]["z"])))
            v = Vec3(_filter_o_x.filter(float(item["velocity"]["x"])),
                     _filter_o_y.filter(float(item["velocity"]["y"])),
                     _filter_o_z.filter(float(item["velocity"]["z"])))
            p = Vec3(_filter_o_x.filter(float(item["position"]["x"])),
                     _filter_o_y.filter(float(item["position"]["y"])),
                     _filter_o_z.filter(float(item["position"]["z"])))
            t = float(item["time"])

            dt = float(item["time_delta"])

            if len(way_points) == 0:
                way_points.append(WayPoint(a, Vec3(0.0), Vec3(0.0), o, o_, t, dt))
                continue

            way_points.append(WayPoint(a, v, p, o, o_, t, dt))

        return AccelerometerLog("", "", way_points)


def accelerations(way_points: List[WayPoint]) -> Tuple[List[float], List[float], List[float]]:
    return [v.acceleration.x for v in way_points], \
           [v.acceleration.y for v in way_points], \
           [v.acceleration.z for v in way_points]


def velocities(way_points: List[WayPoint]) -> Tuple[List[float], List[float], List[float]]:
    return [v.velocity.x for v in way_points], \
           [v.velocity.y for v in way_points], \
           [v.velocity.z for v in way_points]


def positions(way_points: List[WayPoint]) -> Tuple[List[float], List[float], List[float]]:
    return [v.position.x for v in way_points], \
           [v.position.y for v in way_points], \
           [v.position.z for v in way_points]


def ang_velocities(way_points: List[WayPoint]) -> Tuple[List[float], List[float], List[float]]:
    return [v.ang_velocity.x for v in way_points], \
           [v.ang_velocity.y for v in way_points], \
           [v.ang_velocity.z for v in way_points]


def angles(way_points: List[WayPoint]) -> Tuple[List[float], List[float], List[float]]:
    return [v.angle.x for v in way_points], \
           [v.angle.y for v in way_points], \
           [v.angle.z for v in way_points]


def time_vals(way_points: List[WayPoint]) -> List[float]:
    t_0 = 0.0
    time_values = []
    for wp in way_points:
        time_values.append(t_0)
        t_0 += wp.time_delta
    return time_values


q_value = 1.0


def _round(x: float, value: float = 0.01) -> float:
    return int(x / value) * value


def _integrate(dx_vals: List[float], x_vals: List[float], round_f: Callable[[float], float] = None) -> List[float]:
    int_val = 0.0
    integral = []
    if round_f is None:
        round_f = _round

    for dx_i, x_i in zip(dx_vals, x_vals):
        int_val += dx_i * round_f(x_i)
        integral.append(int_val)
    return integral


def integrate(ax: List[float], ay: List[float], az: List[float],
              v_ax: List[float], v_ay: List[float], v_az: List[float],
              dt: List[float]) -> \
        Tuple[List[float], List[float], List[float],
              List[float], List[float], List[float],
              List[float], List[float], List[float]]:
    vx = _integrate(dt, ax)
    vy = _integrate(dt, ay)
    vz = _integrate(dt, az)

    sx = _integrate(dt, vx)
    sy = _integrate(dt, vy)
    sz = _integrate(dt, vz)

    ang_x = _integrate(dt, v_ax)
    ang_y = _integrate(dt, v_ay)
    ang_z = _integrate(dt, v_az)

    return vx, vy, vz, sx, sy, sz, ang_x, ang_y, ang_z


def draw_acceleration(log_info: AccelerometerLog):
    print(f"way points number: {len(log_info.way_points)}")

    _x = [v.acceleration.x for v in log_info.way_points]
    _y = [v.acceleration.y for v in log_info.way_points]
    _z = [v.acceleration.z for v in log_info.way_points]

    print(f"x:[{np.amin(_x):.12}, {np.amax(_x):.12}]")
    print(f"y:[{np.amin(_y):.12}, {np.amax(_y):.12}]")
    print(f"z:[{np.amin(_z):.12}, {np.amax(_z):.12}]")

    fig = plt.figure()

    ax = plt.axes(projection='3d')

    ax.plot3D(_x, _y, _z, 'r')

    plt.show()


def draw_acceleration_2d(log_info: AccelerometerLog):
    print(f"way points number: {len(log_info.way_points)}")

    ax, ay, az = accelerations(log_info.way_points)
    ang_vx, ang_vy, ang_vz = ang_velocities(log_info.way_points)
    time_values = time_vals(log_info.way_points)
    dtime_values = [p.time_delta for p in log_info.way_points]
    dtime_values[0] = dtime_values[-1]
    # vx, vy, vz = velocities(log_info.way_points)
    # sx, sy, sz = positions(log_info.way_points)
    # ang_x, ang_y, ang_z = angles(log_info.way_points)

    vx, vy, vz, sx, sy, sz, ang_x, ang_y, ang_z = integrate(ax, ay, az, ang_vx, ang_vy, ang_vz, dtime_values)

    fig_1 = plt.figure()

    axes = plt.axes()  # (projection='3d')
    axes.plot(time_values, ax, '*r')
    axes.plot(time_values, ay, '*g')
    axes.plot(time_values, az, '*b')
    axes.legend(['$a_{x}$', '$a_{y}$', '$a_{z}$'])
    axes.set_xlabel("$x,[sec]$")
    axes.set_ylabel("$a(t),[m/sec^{2}]$")
    plt.grid(True)
    plt.show()

    fig_1 = plt.figure()

    axes = plt.axes()  # (projection='3d')

    # axes.plot3D(ax, ay, az, 'r')
    axes.plot(time_values, vx, 'r')
    axes.plot(time_values, vy, 'g')
    axes.plot(time_values, vz, 'b')
    axes.legend(['$v_{x}$', '$v_{y}$', '$v_{z}$'])
    axes.set_xlabel("$x,[sec]$")
    axes.set_ylabel("$v(t),[m/sec]$")
    plt.grid(True)
    plt.show()
    return
    fig_1 = plt.figure()

    axes = plt.axes()
    axes.plot(time_values, sx, 'r')
    axes.plot(time_values, sy, 'g')
    axes.plot(time_values, sz, 'b')
    axes.legend(['$s_{x}$', '$s_{y}$', '$s_{z}$'])
    axes.set_xlabel("$x,[sec]$")
    axes.set_ylabel("$S(t),[m]$")
    plt.grid(True)
    plt.show()

    fig_1 = plt.figure()

    axes = plt.axes()
    axes.plot(time_values, ang_vx, 'r')
    axes.plot(time_values, ang_vy, 'g')
    axes.plot(time_values, ang_vz, 'b')
    axes.legend(['$angV_{x}$', '$angV_{y}$', '$angV_{z}$'])
    axes.set_xlabel("$x,[sec]$")
    axes.set_ylabel("$angV(t),[grad/sec]$")
    plt.grid(True)
    plt.show()

    fig_1 = plt.figure()

    axes = plt.axes()
    axes.plot(time_values, ang_x, 'r')
    axes.plot(time_values, ang_y, 'g')
    axes.plot(time_values, ang_z, 'b')
    axes.legend(['$ang_{x}$', '$ang_{y}$', '$ang_{z}$'])
    axes.set_xlabel("$x,[sec]$")
    axes.set_ylabel("$angV(t),[grad/sec]$")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # log = read_accelerometer_log("accelerometer_log_coridor.json")
    log = read_accelerometer_log("accelerometer_records\still_callib_and_filtered.json")
    draw_acceleration_2d(log)
    # draw_acceleration(log)
