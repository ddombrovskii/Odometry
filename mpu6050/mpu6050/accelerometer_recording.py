from inertial_measurement_unit import IMU
from accelerometer import Accelerometer
from typing import List, Tuple
from cgeo import LoopTimer
from cgeo import Vec3
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


class WayPoint:
    def __init__(self, _t: float, d_t: float, accel: Vec3, vel: Vec3, pos: Vec3, ang_vel: Vec3, ang: Vec3):
        """
        IMU way point
        """
        self.time: float           = _t
        self.dtime: float          = d_t
        self.acceleration: Vec3    = accel
        self.velocity: Vec3        = vel
        self.position: Vec3        = pos
        self.angles_velocity: Vec3 = ang_vel
        self.angle: Vec3           = ang


class AccelMeasurement:
    def __init__(self, _t: float, d_t: float, accel: Vec3, ang_vel: Vec3):
        """
        raw accelerometer read data
        """
        self.time: float           = _t
        self.dtime: float          = d_t
        self.acceleration: Vec3    = accel
        self.angles_velocity: Vec3 = ang_vel


class AccelerometerLog:
    def __init__(self, n: str, t: str, wp: List[AccelMeasurement]):
        self.device_name: str = n
        self.log_time_start: str = t
        self.way_points: List[AccelMeasurement] = wp


class IMULog:
    def __init__(self, n: str, t: str, wp: List[WayPoint]):
        self.device_name: str = n
        self.log_time_start: str = t
        self.way_points: List[WayPoint] = wp


def read_accel(accelerometer: Accelerometer) -> str:
    if not accelerometer.read_accel_measurements():
        raise RuntimeError("Accelerometer read error")
    return f"{{\n" \
            f"\t\"{DTIME}\"           : {accelerometer.delta_t},\n" \
            f"\t\"{TIME}\"            : {accelerometer.curr_t},\n" \
            f"\t\"{ACCELERATION}\"    : {accelerometer.acceleration},\n" \
            f"\t\"{ANGLES_VELOCITY}\" : {accelerometer.ang_velocity}\n" \
            f"\n}}"


def read_imu(imu: IMU) -> str:
        if not imu.read():
            raise RuntimeError("IMU read error")
        return f"{{\n" \
               f"\t\"{DTIME}\"           : {imu.delta_t},\n" \
               f"\t\"{TIME}\"            : {imu.curr_t},\n" \
               f"\t\"{ACCELERATION}\"    : {imu.acceleration},\n" \
               f"\t\"{VELOCITY}\"        : {imu.velocity},\n" \
               f"\t\"{POSITION}\"        : {imu.position},\n" \
               f"\t\"{ANGLES_VELOCITY}\" : {imu.angles_velocity},\n" \
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
        way_points = [] * len(raw_json[WAY_POINTS])  # todo chek...
        for item_index, item in enumerate(raw_json[WAY_POINTS]):
            if ACCELERATION in item:
                accel = Vec3(float(item[ACCELERATION]["x"]),
                             float(item[ACCELERATION]["y"]),
                             float(item[ACCELERATION]["z"]))
            else:
                accel = Vec3(0, 0, 0)

            if ANGLES_VELOCITY in item:
                ang_vel = Vec3(float(item[ANGLES_VELOCITY]["x"]),
                               float(item[ANGLES_VELOCITY]["y"]),
                               float(item[ANGLES_VELOCITY]["z"]))
            else:
                ang_vel = Vec3(0, 0, 0)

            if TIME in item:
                t = float(item[TIME])
            else:
                t = 0.0

            if DTIME in item:
                dt = float(item[DTIME])
            else:
                dt = 0.0

            way_points[item_index] = AccelMeasurement(t, dt, accel, ang_vel)

        return AccelerometerLog(device_name, log_time_start, way_points)


def read_imu_log(record_path: str) -> IMULog:
    with open(record_path) as input_json:
        raw_json = json.load(input_json)
        if not(WAY_POINTS in raw_json):
            return IMULog("error", "error", [])
        log_time_start = raw_json[LOG_TIME_START] if LOG_TIME_START in raw_json else "no-name"
        device_name = raw_json[DEVICE_NAME] if DEVICE_NAME in raw_json else "no-time"
        way_points = [] * len(raw_json[WAY_POINTS])

        for item_index, item in enumerate(raw_json[WAY_POINTS]):
            if ACCELERATION in item:
                accel = Vec3(float(item[ACCELERATION]["x"]),
                             float(item[ACCELERATION]["y"]),
                             float(item[ACCELERATION]["z"]))
            else:
                accel = Vec3(0, 0, 0)

            if ANGLES_VELOCITY in item:
                ang_vel = Vec3(float(item[ANGLES_VELOCITY]["x"]),
                               float(item[ANGLES_VELOCITY]["y"]),
                               float(item[ANGLES_VELOCITY]["z"]))
            else:
                ang_vel = Vec3(0, 0, 0)

            if ANGLES in item:
                angle = Vec3(float(item[ANGLES]["x"]),
                             float(item[ANGLES]["y"]),
                             float(item[ANGLES]["z"]))
            else:
                angle = Vec3(0, 0, 0)

            if VELOCITY in item:
                velocity = Vec3(float(item[VELOCITY]["x"]),
                                float(item[VELOCITY]["y"]),
                                float(item[VELOCITY]["z"]))
            else:
                velocity = Vec3(0, 0, 0)

            if POSITION in item:
                position = Vec3(float(item[POSITION]["x"]),
                                float(item[POSITION]["y"]),
                                float(item[POSITION]["z"]))
            else:
                position = Vec3(0, 0, 0)

            if TIME in item:
                t = float(item[TIME])
            else:
                t = 0.0

            if DTIME in item:
                dt = float(item[DTIME])
            else:
                dt = 0.0
            way_points[item_index]  = WayPoint(t, dt, accel, velocity, position, ang_vel, angle)

        return IMULog(device_name, log_time_start, way_points)


def accelerations(log: AccelerometerLog, start_time: float = 0.0) -> Tuple[List[float], List[float], List[float]]:
    t0 = log.way_points[0].time
    return [v.acceleration.x for v in log.way_points if v.time -  t0 >= start_time], \
           [v.acceleration.y for v in log.way_points if v.time -  t0 >= start_time], \
           [v.acceleration.z for v in log.way_points if v.time -  t0 >= start_time]


def ang_velocities(log: AccelerometerLog, start_time: float = 0.0) -> Tuple[List[float], List[float], List[float]]:
    t0 = log.way_points[0].time
    return [v.angles_velocity.x for v in log.way_points if v.time -  t0 >= start_time], \
           [v.angles_velocity.y for v in log.way_points if v.time -  t0 >= start_time], \
           [v.angles_velocity.z for v in log.way_points if v.time -  t0 >= start_time]


def imu_accelerations(log: IMULog, start_time: float = 0.0) -> Tuple[List[float], List[float], List[float]]:
    t0 = log.way_points[0].time
    return [v.acceleration.x for v in log.way_points if v.time -  t0 >= start_time], \
           [v.acceleration.y for v in log.way_points if v.time -  t0 >= start_time], \
           [v.acceleration.z for v in log.way_points if v.time -  t0 >= start_time]


def imu_velocities(log: IMULog, start_time: float = 0.0) -> Tuple[List[float], List[float], List[float]]:
    t0 = log.way_points[0].time
    return [v.velocity.x for v in log.way_points if v.time - t0 >= start_time], \
           [v.velocity.y for v in log.way_points if v.time - t0 >= start_time], \
           [v.velocity.z for v in log.way_points if v.time - t0 >= start_time]


def imu_positions(log: IMULog, start_time: float = 0.0) -> Tuple[List[float], List[float], List[float]]:
    t0 = log.way_points[0].time
    return [v.position.x for v in log.way_points if v.time -  t0 >= start_time], \
           [v.position.y for v in log.way_points if v.time -  t0 >= start_time], \
           [v.position.z for v in log.way_points if v.time -  t0 >= start_time]


def imu_ang_velocities(log: IMULog, start_time: float = 0.0) -> Tuple[List[float], List[float], List[float]]:
    t0 = log.way_points[0].time
    return [v.angles_velocity.x for v in log.way_points if v.time -  t0 >= start_time], \
           [v.angles_velocity.y for v in log.way_points if v.time -  t0 >= start_time], \
           [v.angles_velocity.z for v in log.way_points if v.time -  t0 >= start_time]


def imu_angles(log: IMULog, start_time: float = 0.0) -> Tuple[List[float], List[float], List[float]]:
    t0 = log.way_points[0].time
    return [v.angle.x for v in log.way_points if v.time - t0 >= start_time], \
           [v.angle.y for v in log.way_points if v.time - t0 >= start_time], \
           [v.angle.z for v in log.way_points if v.time - t0 >= start_time]


def imu_time_values(log: IMULog, start_time: float = 0.0) -> List[float]:
    t0 =  log.way_points[0].time
    return [v.time - t0 for v in log.way_points if v.time - t0 >= start_time]


def time_values(log: AccelerometerLog, start_time: float = 0.0) -> List[float]:
    t0 =  log.way_points[0].time
    return [v.time - t0 for v in log.way_points if v.time - t0 >= start_time]


def integrate_angles(log: AccelerometerLog) -> Tuple[List[float], List[float], List[float]]:
    a_prev = Vec3(0)  # log.way_points[0].angle
    a_curr = Vec3(0)
    ax: List[float] = []
    ay: List[float] = []
    az: List[float] = []
    for wp in log.way_points:
        dti = wp.dtime
        a_curr = wp.angles_velocity
        ax.append(ax[-1] + (a_prev.x + a_curr.x) * 0.5 * dti) if len(ax) != 0 else ax.append((a_prev.x + a_curr.x) * 0.5 * dti)
        ay.append(ay[-1] + (a_prev.y + a_curr.y) * 0.5 * dti) if len(ay) != 0 else ay.append((a_prev.y + a_curr.y) * 0.5 * dti)
        az.append(az[-1] + (a_prev.z + a_curr.z) * 0.5 * dti) if len(az) != 0 else az.append((a_prev.z + a_curr.z) * 0.5 * dti)
        a_prev = a_curr
    return ax, ay, az


# add local accel basis
def integrate_accelerations(log: AccelerometerLog) -> Tuple[List[float], List[float], List[float]]:
    a_prev = Vec3(0)  # log.way_points[0].angle
    a_curr = Vec3(0)
    ax: List[float] = []
    ay: List[float] = []
    az: List[float] = []
    for wp in log.way_points:
        dti = wp.dtime
        a_curr = wp.acceleration
        ax.append(ax[-1] + (a_prev.x + a_curr.x) * 0.5 * dti) if len(ax) != 0 else ax.append((a_prev.x + a_curr.x) * 0.5 * dti)
        ay.append(ay[-1] + (a_prev.y + a_curr.y) * 0.5 * dti) if len(ay) != 0 else ay.append((a_prev.y + a_curr.y) * 0.5 * dti)
        az.append(az[-1] + (a_prev.z + a_curr.z) * 0.5 * dti) if len(az) != 0 else az.append((a_prev.z + a_curr.z) * 0.5 * dti)
        a_prev = a_curr
    return ax, ay, az


def integrate_velocities(log: AccelerometerLog) -> Tuple[List[float], List[float], List[float]]:
    vx, vy, vz = integrate_accelerations(log)
    s_prev = Vec3(0)
    s_curr = Vec3(0)
    sx: List[float] = []
    sy: List[float] = []
    sz: List[float] = []
    for index in range(min((len(vx), len(vy), len(vz)))):
        dti = log.way_points[index].dtime
        s_curr.x = vx[index]
        s_curr.y = vy[index]
        s_curr.z = vz[index]
        sx.append(sx[-1] + (s_prev.x + s_curr.x) * 0.5 * dti) if len(sx) != 0 else sx.append((s_prev.x + s_curr.x) * 0.5 * dti)
        sy.append(sy[-1] + (s_prev.y + s_curr.y) * 0.5 * dti) if len(sy) != 0 else sy.append((s_prev.y + s_curr.y) * 0.5 * dti)
        sz.append(sz[-1] + (s_prev.z + s_curr.z) * 0.5 * dti) if len(sz) != 0 else sz.append((s_prev.z + s_curr.z) * 0.5 * dti)
        s_prev = s_curr
    return sx, sy, sz


def integrate(log: AccelerometerLog) -> Tuple[List[float], List[float], List[float],
                                              List[float], List[float], List[float],
                                              List[float], List[float], List[float]]:
    vx, vy, vz = integrate_accelerations(log)
    ax, ay, az = integrate_angles(log)
    s_prev = Vec3(0)
    s_curr = Vec3(0)
    sx: List[float] = []
    sy: List[float] = []
    sz: List[float] = []
    for index in range(min((len(vx), len(vy), len(vz)))):
        dti = log.way_points[index].dtime
        s_curr.x = vx[index]
        s_curr.y = vy[index]
        s_curr.z = vz[index]
        sx.append(sx[-1] + (s_prev.x + s_curr.x) * 0.5 * dti) if len(sx) != 0 else sx.append((s_prev.x + s_curr.x) * 0.5 * dti)
        sy.append(sy[-1] + (s_prev.y + s_curr.y) * 0.5 * dti) if len(sy) != 0 else sy.append((s_prev.y + s_curr.y) * 0.5 * dti)
        sz.append(sz[-1] + (s_prev.z + s_curr.z) * 0.5 * dti) if len(sz) != 0 else sz.append((s_prev.z + s_curr.z) * 0.5 * dti)
        s_prev = s_curr
    return vx, vy, vz, sx, sy, sz, ax, ay, az


