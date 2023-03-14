# from accelerometer_core.utilities.loop_timer import LoopTimer
# from accelerometer_core.inertial_measurement_unit import IMU
# from accelerometer_core.accelerometer import Accelerometer
# from accelerometer_core.utilities.vector3 import Vector3

from .utilities.loop_timer import LoopTimer
from .inertial_measurement_unit import IMU
from .accelerometer import Accelerometer
from .utilities.vector3 import Vector3
from collections import namedtuple
from typing import List
import datetime as dt
import json


TIME            = "time"
DTIME           = "dtime"
ACCELERATION    = "acceleration"
VELOCITY        = "velocity"
POSITION        = "position"
ANGLES_VELOCITY = "angles_velocity"
ANGLES          = "angles"
DEVICE_NAME     = "device_name"
LOG_TIME_START  = "log_time_start"
WAY_POINTS      = "way_points"


class AccelMeasurement(namedtuple('AccelMeasurement', 'time, dtime, acceleration, angles_velocity')):
    def __new__(cls,
                time: float,
                dtime: float,
                acceleration: Vector3,
                angles_velocity: Vector3):
        """
        raw accelerometer read data
        """
        return super().__new__(cls, time, dtime, acceleration, angles_velocity)


class AccelerometerLog:
    def __init__(self, n: str, t: str, wp: List[AccelMeasurement]):
        self.device_name: str = n
        self.log_time_start: str = t
        self.way_points: List[AccelMeasurement] = wp

    @property
    def accelerations_x(self) -> List[float]: return [v.acceleration.x for v in self.way_points]

    @property
    def accelerations_y(self) -> List[float]: return [v.acceleration.y for v in self.way_points]

    @property
    def accelerations_z(self) -> List[float]: return [v.acceleration.z for v in self.way_points]

    @property
    def accelerations(self) -> List[Vector3]: return [v.acceleration for v in self.way_points]

    @property
    def angles_velocities_x(self) -> List[float]: return [v.angles_velocity.x for v in self.way_points]

    @property
    def angles_velocities_y(self) -> List[float]: return [v.angles_velocity.y for v in self.way_points]

    @property
    def angles_velocities_z(self) -> List[float]: return [v.angles_velocity.z for v in self.way_points]

    @property
    def angles_velocities(self) -> List[Vector3]: return [v.angles_velocity for v in self.way_points]

    @property
    def time_values(self) -> List[float]: return [v.time - self.way_points[0].time for v in self.way_points]


class WayPoint(namedtuple('WayPoint', 'time, dtime, acceleration, velocity, position, angles_velocity, angles')):

    def __new__(cls,
                time: float,
                dtime: float,
                acceleration: Vector3,
                velocity: Vector3,
                position: Vector3,
                angles_velocity: Vector3,
                angles: Vector3):
        return super().__new__(cls, time, dtime, acceleration, velocity, position, angles_velocity, angles)


class IMULog:
    def __init__(self, n: str, t: str, wp: List[WayPoint]):
        self.device_name: str           = n
        self.log_time_start: str        = t
        self.way_points: List[WayPoint] = wp

    @property
    def accelerations_x(self) -> List[float]: return [v.acceleration.x for v in self.way_points]

    @property
    def accelerations_y(self) -> List[float]: return [v.acceleration.y for v in self.way_points]

    @property
    def accelerations_z(self) -> List[float]: return [v.acceleration.z for v in self.way_points]

    @property
    def accelerations(self) -> List[Vector3]: return [v.acceleration for v in self.way_points]

    @property
    def velocities_x(self) -> List[float]: return [v.velocity.x for v in self.way_points]

    @property
    def velocities_y(self) -> List[float]: return [v.velocity.y for v in self.way_points]

    @property
    def velocities_z(self) -> List[float]: return [v.velocity.z for v in self.way_points]

    @property
    def velocities(self) -> List[Vector3]: return [v.velocity for v in self.way_points]

    @property
    def positions_x(self) -> List[float]: return [v.position.x for v in self.way_points]

    @property
    def positions_y(self) -> List[float]: return [v.position.y for v in self.way_points]

    @property
    def positions_z(self) -> List[float]: return [v.position.z for v in self.way_points]

    @property
    def positions(self) -> List[Vector3]: return [v.position for v in self.way_points]

    @property
    def angles_velocities_x(self) -> List[float]: return [v.angles_velocity.x for v in self.way_points]

    @property
    def angles_velocities_y(self) -> List[float]: return [v.angles_velocity.y for v in self.way_points]

    @property
    def angles_velocities_z(self) -> List[float]: return [v.angles_velocity.z for v in self.way_points]

    @property
    def angles_velocities(self) -> List[Vector3]: return [v.angles_velocity for v in self.way_points]

    @property
    def angles_x(self) -> List[float]: return [v.angles.x for v in self.way_points]

    @property
    def angles_y(self) -> List[float]: return [v.angles.y for v in self.way_points]

    @property
    def angles_z(self) -> List[float]: return [v.angles.z for v in self.way_points]

    @property
    def angles(self) -> List[Vector3]: return [v.angles for v in self.way_points]

    @property
    def time_values(self) -> List[float]: return [v.time - self.way_points[0].time for v in self.way_points]


def read_accel(accelerometer: Accelerometer) -> str:
    if not accelerometer.read_measurements():
        raise RuntimeError("Accelerometer read error")
    return f"{{\n" \
           f"\t\"{DTIME}\"           : {accelerometer.delta_t},\n" \
           f"\t\"{TIME}\"            : {accelerometer.curr_t},\n" \
           f"\t\"{ACCELERATION}\"    : {accelerometer.acceleration},\n" \
           f"\t\"{ANGLES_VELOCITY}\" : {accelerometer.omega}\n" \
           f"\n}}"


def read_imu(imu: IMU) -> str:
        # if not imu.read():
        #     raise RuntimeError("IMU read error")
        return f"{{\n" \
               f"\t\"{DTIME}\"           : {imu.delta_t},\n" \
               f"\t\"{TIME}\"            : {imu.curr_t},\n" \
               f"\t\"{ACCELERATION}\"    : {imu.acceleration},\n" \
               f"\t\"{VELOCITY}\"        : {imu.velocity},\n" \
               f"\t\"{POSITION}\"        : {imu.position},\n" \
               f"\t\"{ANGLES_VELOCITY}\" : {imu.omega},\n" \
               f"\t\"{ANGLES}\"          : {imu.angles}\n" \
               f"\n}}"


def read_accel_data(accelerometer: Accelerometer, reading_time: float = 1.0, time_delta: float = 0.05) -> \
        List[str]:
    lt = LoopTimer()
    lt.timeout = time_delta
    records: List[str] = []
    while True:
        with lt:
            records.append(read_accel(accelerometer))
            if lt.time >= reading_time:
                break
    return records


def record_accel_log(file_path: str, accelerometer: Accelerometer,
                     reading_time: float = 1.0, time_delta: float = 0.075) -> None:
    with open(file_path, 'wt') as out_put:
        print(f"{{\n\"record_date\": \"{dt.datetime.now().strftime('%H; %M; %S')}\",\n", file=out_put)
        print("\"way_points\" :[", file=out_put)
        lt = LoopTimer()
        lt.timeout = time_delta
        while True:
            with lt:
                print(read_accel(accelerometer), file=out_put)
                if lt.time >= reading_time:
                    break
                print(',', file=out_put)
        print("\t]\n}", file=out_put)


def record_imu_log(file_path: str, imu: IMU,
                   reading_time: float = 1.0, time_delta: float = 0.075) -> None:
    with open(file_path, 'wt') as out_put:
        print(f"{{\n\"record_date\": \"{dt.datetime.now().strftime('%H; %M; %S')}\",\n", file=out_put)
        print("\"way_points\" :[", file=out_put)
        lt = LoopTimer()
        lt.timeout = time_delta
        while True:
            with lt:
                print(read_imu(imu), file=out_put)
                if lt.time >= reading_time:
                    break
                print(',', file=out_put)
        print("\t]\n}", file=out_put)


def read_accel_log(record_path: str) -> AccelerometerLog:
    with open(record_path) as input_json:
        raw_json = json.load(input_json)
        if not(WAY_POINTS in raw_json):
            return AccelerometerLog("error", "error", [])
        log_time_start = raw_json[LOG_TIME_START] if LOG_TIME_START in raw_json else "no-name"
        device_name = raw_json[DEVICE_NAME] if DEVICE_NAME in raw_json else "no-time"
        way_points = [None] * len(raw_json[WAY_POINTS])
        for item_index, item in enumerate(raw_json[WAY_POINTS]):
            if ACCELERATION in item:
                accel = Vector3(float(item[ACCELERATION]["x"]),
                                float(item[ACCELERATION]["y"]),
                                float(item[ACCELERATION]["z"]))
            else:
                accel = Vector3(0.0, 0.0, 0.0)

            if ANGLES_VELOCITY in item:
                ang_vel = Vector3(float(item[ANGLES_VELOCITY]["x"]),
                                  float(item[ANGLES_VELOCITY]["y"]),
                                  float(item[ANGLES_VELOCITY]["z"]))
            else:
                ang_vel = Vector3(0.0, 0.0, 0.0)

            if TIME in item:
                t = float(item[TIME])
            else:
                t = 0.0

            if DTIME in item:
                d_t = float(item[DTIME])
            else:
                d_t = 0.0

            way_points[item_index] = AccelMeasurement(t, d_t, accel, ang_vel)

        return AccelerometerLog(device_name, log_time_start, way_points)


def read_imu_log(record_path: str) -> IMULog:
    with open(record_path) as input_json:
        raw_json = json.load(input_json)
        if not(WAY_POINTS in raw_json):
            return IMULog("error", "error", [])
        log_time_start = raw_json[LOG_TIME_START] if LOG_TIME_START in raw_json else "no-name"
        device_name = raw_json[DEVICE_NAME] if DEVICE_NAME in raw_json else "no-time"
        way_points = [None] * len(raw_json[WAY_POINTS])

        for item_index, item in enumerate(raw_json[WAY_POINTS]):
            if ACCELERATION in item:
                accel = Vector3(float(item[ACCELERATION]["x"]),
                                float(item[ACCELERATION]["y"]),
                                float(item[ACCELERATION]["z"]))
            else:
                accel = Vector3(0.0, 0.0, 0.0)

            if ANGLES_VELOCITY in item:
                ang_vel = Vector3(float(item[ANGLES_VELOCITY]["x"]),
                                  float(item[ANGLES_VELOCITY]["y"]),
                                  float(item[ANGLES_VELOCITY]["z"]))
            else:
                ang_vel = Vector3(0.0, 0.0, 0.0)

            if ANGLES in item:
                angle = Vector3(float(item[ANGLES]["x"]),
                                float(item[ANGLES]["y"]),
                                float(item[ANGLES]["z"]))
            else:
                angle = Vector3(0.0, 0.0, 0.0)

            if VELOCITY in item:
                velocity = Vector3(float(item[VELOCITY]["x"]),
                                   float(item[VELOCITY]["y"]),
                                   float(item[VELOCITY]["z"]))
            else:
                velocity = Vector3(0.0, 0.0, 0.0)

            if POSITION in item:
                position = Vector3(float(item[POSITION]["x"]),
                                   float(item[POSITION]["y"]),
                                   float(item[POSITION]["z"]))
            else:
                position = Vector3(0.0, 0.0, 0.0)

            if TIME in item:
                t = float(item[TIME])
            else:
                t = 0.0

            if DTIME in item:
                d_t = float(item[DTIME])
            else:
                d_t = 0.0

            way_points[item_index]  = WayPoint(t, d_t, accel, velocity, position, ang_vel, angle)

        return IMULog(device_name, log_time_start, way_points)
