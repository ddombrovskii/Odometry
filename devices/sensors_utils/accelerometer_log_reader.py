from Odometry.devices.sensors_utils.real_time_filter import RealTimeFilter
from Odometry.vmath.core.vectors import Vec3
import matplotlib.pyplot as plt
from typing import List
import dataclasses
import numpy as np
import json


@dataclasses.dataclass
class WayPoint:
    acceleration: Vec3
    velocity: Vec3
    position: Vec3
    orientation: Vec3
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
            o = Vec3(_filter_o_x.filter(float(item["orientations"]["x"])),
                     _filter_o_y.filter(float(item["orientations"]["y"])),
                     _filter_o_z.filter(float(item["orientations"]["z"])))

            t = float(item["curr_time"])

            dt = float(item["delta_time"])

            if len(way_points) == 0:
                way_points.append(WayPoint(a, Vec3(0.0), Vec3(0.0), o, t, dt))
                continue

            way_points.append(WayPoint(a,
                                       way_points[-1].velocity + a * dt,
                                       way_points[-1].position + way_points[-1].velocity * dt,
                                       o, t, dt))

        return AccelerometerLog(raw_json["device_name"], raw_json["log_time_start"], way_points)


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


if __name__ == "__main__":
    log = read_accelerometer_log("accelerometer_log 23; 42; 44.json")
    draw_acceleration(log)


