from accelerometer import Accelerometer
from cgeo import LoopTimer
from typing import List
import datetime as dt


def read_current_data(accelerometer: Accelerometer, mode: int = 3) -> str:
    accelerometer.read_accel_measurements()
    if mode == 0:
        return f"{{\n" \
               f"\t\"accel_dt\"       : {accelerometer.accel_dt},\n" \
               f"\t\"accel_t\"        : {accelerometer.accel_t},\n" \
               f"\t\"acceleration\"   : {accelerometer.acceleration}\n" \
               f"\n}}"
    if mode == 1:
        return f"{{\n" \
               f"\t\"accel_dt\"       : {accelerometer.accel_dt},\n" \
               f"\t\"accel_t\"        : {accelerometer.accel_t},\n" \
               f"\t\"angles_velocity\": {accelerometer.angles_velocity},\n" \
               f"\t\"acceleration\"   : {accelerometer.acceleration}\n" \
               f"\n}}"
    if mode == 2:
        return f"{{\n" \
               f"\t\"accel_dt\"       : {accelerometer.accel_dt},\n" \
               f"\t\"accel_t\"        : {accelerometer.accel_t},\n" \
               f"\t\"acceleration\"   : {accelerometer.acceleration},\n" \
               f"\t\"angles_velocity\": {accelerometer.angles_velocity},\n" \
               f"\t\"velocity\"       : {accelerometer.velocity}\n" \
               f"\n}}"
    if mode == 3:
        return f"{{\n" \
               f"\t\"accel_dt\"       : {accelerometer.accel_dt},\n" \
               f"\t\"accel_t\"        : {accelerometer.accel_t},\n" \
               f"\t\"acceleration\"   : {accelerometer.acceleration},\n" \
               f"\t\"angles_velocity\": {accelerometer.angles_velocity},\n" \
               f"\t\"velocity\"       : {accelerometer.velocity},\n" \
               f"\t\"position\"       : {accelerometer.position}" \
               f"\n}}"
    return f"{{\n" \
           f"\t\"accel_dt\"       : {accelerometer.accel_dt},\n" \
           f"\t\"accel_t\"        : {accelerometer.accel_t},\n" \
           f"\t\"acceleration\"   : {accelerometer.acceleration}\n" \
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
        print(f"\"record_date\": {dt.datetime.now().strftime('%H; %M; %S')},", file=out_put)
        lt = LoopTimer()
        lt.timeout = time_delta
        while True:
            with lt:
                print(read_current_data(accelerometer, mode), file=out_put)
                if lt.time >= reading_time:
                    break
                print(',', file=out_put)
        print("\t]\n}", file=out_put)
