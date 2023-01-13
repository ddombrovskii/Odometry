from accelerometer import Accelerometer
from typing import List, Tuple
from cgeo import LoopTimer
from cgeo import Vec3
import datetime as dt
import json


TIME = "time"
DTIME = "dtime"
ACCELERATION = "acceleration"
VELOCITY = "velocity"
POSITION = "position"
ANG_VELOCITY = "angles_velocity"
ANGLES = "angles"

DEVICE_NAME = "device_name"
LOG_TIME_START = "log_time_start"
WAY_POINTS = "way_points"


# TODO as simple class
@dataclasses.dataclass
class WayPoint:
    time: float
    dtime: float
    acceleration: Vec3
    velocity: Vec3
    position: Vec3
    angles_velocity: Vec3
    angle: Vec3


@dataclasses.dataclass
class AccelerometerLog:
    device_name: str
    log_time_start: str
    way_points: List[WayPoint]


def read_current_data(accelerometer: Accelerometer, mode: int = 3) -> str:
    accelerometer.read_accel_measurements()
    if mode == 0:
        return f"{{\n" \
               f"\t\"{DTIME: 16}\": {accelerometer.accel_dt},\n" \
               f"\t\"{TIME: 16}\": {accelerometer.accel_t},\n" \
               f"\t\"{ACCELERATION: 16}\": {accelerometer.acceleration}\n" \
               f"\n}}"

    if mode == 1:
        return f"{{\n" \
               f"\t\"{DTIME: 16}\": {accelerometer.accel_dt},\n" \
               f"\t\"{TIME: 16}\": {accelerometer.accel_t},\n" \
               f"\t\"{ACCELERATION: 16}\": {accelerometer.acceleration},\n" \
               f"\t\"{ANG_VELOCITY: 16}\": {accelerometer.angles_velocity}\n" \
               f"\n}}"

    if mode == 2:
        return f"{{\n" \
               f"\t\"{DTIME: 16}\": {accelerometer.accel_dt},\n" \
               f"\t\"{TIME: 16}\": {accelerometer.accel_t},\n" \
               f"\t\"{ACCELERATION: 16}\": {accelerometer.acceleration},\n" \
               f"\t\"{VELOCITY: 16}\": {accelerometer.velocity},\n" \
               f"\t\"{ANG_VELOCITY: 16}\": {accelerometer.angles_velocity}\n" \
               f"\n}}"

    if mode == 3:
        return f"{{\n" \
               f"\t\"{DTIME: 16}\": {accelerometer.accel_dt},\n" \
               f"\t\"{TIME: 16}\": {accelerometer.accel_t},\n" \
               f"\t\"{ACCELERATION: 16}\": {accelerometer.acceleration},\n" \
               f"\t\"{VELOCITY: 16}\": {accelerometer.velocity},\n" \
               f"\t\"{POSITION: 16}\": {accelerometer.position},\n" \
               f"\t\"{ANG_VELOCITY: 16}\": {accelerometer.angles_velocity}\n" \
               f"\n}}"

    if mode == 4:
        return f"{{\n" \
               f"\t\"{DTIME}\"       : {accelerometer.accel_dt},\n" \
               f"\t\"{TIME}\"        : {accelerometer.accel_t},\n" \
               f"\t\"{ACCELERATION}\"   : {accelerometer.acceleration},\n" \
               f"\t\"{VELOCITY}\"       : {accelerometer.velocity},\n" \
               f"\t\"{POSITION}\"       : {accelerometer.position},\n" \
               f"\t\"{ANG_VELOCITY}\": {accelerometer.angles_velocity},\n" \
               f"\t\"{ANGLES}\": {accelerometer.angles_velocity}\n" \
               f"\n}}"

    return f"{{\n" \
           f"\t\"{DTIME}\"       : {accelerometer.accel_dt},\n" \
           f"\t\"{TIME}\"        : {accelerometer.accel_t},\n" \
           f"\t\"{ACCELERATION}\"   : {accelerometer.acceleration}\n" \
           f"\n}}"


def read_data(accelerometer: Accelerometer, reading_time: float = 1.0, time_delta: float = 0.075, mode: int = 3) -> \
        List[str]:
    lt = LoopTimer()
    lt.timeout = time_delta
    records: List[str] = []
    while True:
        with lt:
            records.append(read_current_data(accelerometer, mode))
            if lt.time >= reading_time:
                break
    return records


def read_and_save_data(file_path: str, accelerometer: Accelerometer,
                       reading_time: float = 1.0, time_delta: float = 0.075, mode: int = 3) -> None:
    with open(file_path, 'wt') as out_put:
        print("{\n\"way_points\" :[", file=out_put)
        print(f"\"record_date\": \"{dt.datetime.now().strftime('%H; %M; %S')}\",", file=out_put)
        lt = LoopTimer()
        lt.timeout = time_delta
        while True:
            with lt:
                print(read_current_data(accelerometer, mode), file=out_put)
                if lt.time >= reading_time:
                    break
                print(',', file=out_put)
        print("\t]\n}", file=out_put)


def read_record(record_path: str) -> AccelerometerLog:
    with open(record_path) as input_json:
        raw_json = json.load(input_json)
        log_time_start = raw_json[LOG_TIME_START] if LOG_TIME_START in raw_json else "no-name"
        device_name = raw_json[DEVICE_NAME] if DEVICE_NAME in raw_json else "no-time"
        way_points = [] * len(raw_json[WAY_POINTS])
        v = Vec3(0.0)
        p = Vec3(0.0)

        for item in raw_json[WAY_POINTS]:
            if ACCELERATION in item:
                a = Vec3(float(item[ACCELERATION]["x"]),
                         float(item[ACCELERATION]["y"]),
                         float(item[ACCELERATION]["z"]))
            else:
                a = Vec3(0, 0, 0)

            if ANG_VELOCITY in item:
                o = Vec3(float(item[ANG_VELOCITY]["x"]),
                         float(item[ANG_VELOCITY]["y"]),
                         float(item[ANG_VELOCITY]["z"]))
            else:
                o = Vec3(0, 0, 0)

            if ANGLES in item:
                o_ = Vec3(float(item[ANGLES]["x"]),
                          float(item[ANGLES]["y"]),
                          float(item[ANGLES]["z"]))
            else:
                o_ = Vec3(0, 0, 0)

            if VELOCITY in item:
                v = Vec3(float(item[VELOCITY]["x"]),
                         float(item[VELOCITY]["y"]),
                         float(item[VELOCITY]["z"]))
            else:
                v = Vec3(0, 0, 0)

            if POSITION in item:
                p = Vec3(float(item[POSITION]["x"]),
                         float(item[POSITION]["y"]),
                         float(item[POSITION]["z"]))
            else:
                p = Vec3(0, 0, 0)

            t = float(item[TIME])
            dt = float(item[DTIME])
            way_points.append(WayPoint(t, dt, a, v, p, o, o_))

        return AccelerometerLog(device_name, log_time_start, way_points)


def accelerations(log: AccelerometerLog) -> Tuple[List[float], List[float], List[float]]:
    return [v.acceleration.x for v in log.way_points], \
           [v.acceleration.y for v in log.way_points], \
           [v.acceleration.z for v in log.way_points]


def velocities(log: AccelerometerLog) -> Tuple[List[float], List[float], List[float]]:
    return [v.velocity.x for v in log.way_points], \
           [v.velocity.y for v in log.way_points], \
           [v.velocity.z for v in log.way_points]


def positions(log: AccelerometerLog) -> Tuple[List[float], List[float], List[float]]:
    return [v.position.x for v in log.way_points], \
           [v.position.y for v in log.way_points], \
           [v.position.z for v in log.way_points]


def ang_velocities(log: AccelerometerLog) -> Tuple[List[float], List[float], List[float]]:
    return [v.angles_velocity.x for v in log.way_points], \
           [v.angles_velocity.y for v in log.way_points], \
           [v.angles_velocity.z for v in log.way_points]


def angles(log: AccelerometerLog) -> Tuple[List[float], List[float], List[float]]:
    return [v.angle.x for v in log.way_points], \
           [v.angle.y for v in log.way_points], \
           [v.angle.z for v in log.way_points]


def time_values(log: AccelerometerLog) -> List[float]:
    t_0 = 0.0
    time_values = []
    for wp in log.way_points:
        time_values.append(t_0)
        t_0 += wp.dtime
    return time_values


