from cgeo import Vec3
from cgeo.filtering import RealTimeFilter
from accelerometer import Accelerometer
from constants import *
import json


def load_accelerometer_settings(acc: Accelerometer, settings_file: str) -> bool:
    json_file = None
    with open(settings_file, "rt") as output_file:
        json_file = json.load(output_file)
        if json_file is None:
            return False
    flag = False

    if "address" in json_file:
        prev_address = acc.address
        address = int(json_file["address"])
        if address != acc.address:
            acc.address = int(json_file["address"])
            if acc.address == prev_address:
                print("incorrect device address in HardwareAccelerometerSettings")
        flag |= True
    try:
        if "acceleration_range_raw" in json_file:
            acc.acceleration_range_raw = int(json_file["acceleration_range_raw"])
            flag |= True
    except RuntimeWarning as _ex:
        print("acceleration_range_raw read error")
        acc.acceleration_range_raw = ACCEL_RANGE_2G

    try:
        if "gyroscope_range_raw" in json_file:
            acc.gyroscope_range_raw = int(json_file["gyroscope_range_raw"])
            flag |= True
    except RuntimeWarning as _ex:
        print("gyroscope_range_raw read error")
        acc.acceleration_range_raw = GYRO_RANGE_250DEG

    try:
        if "hardware_filter_range_raw" in json_file:
            acc.hardware_filter_range_raw = int(json_file["hardware_filter_range_raw"])
            flag |= True
    except RuntimeWarning as _ex:
        print("hardware_filter_range_raw read error")

    try:
        if "use_filtering" in json_file:
            acc.use_filtering = bool(json_file["use_filtering"])
            flag |= True
    except RuntimeWarning as _ex:
        print("use_filtering read error")

    try:
        if "angles_velocity_calibration" in json_file:
            acc.angles_velocity_calibration = Vec3(float(json_file["angles_velocity_calibration"]["x"]),
                                                   float(json_file["angles_velocity_calibration"]["y"]),
                                                   float(json_file["angles_velocity_calibration"]["z"]))
            flag |= True
    except RuntimeWarning as _ex:
        print("use_filtering read error")

    try:
        if "acceleration_calibration" in json_file:
            acc.acceleration_calibration = Vec3(float(json_file["acceleration_calibration"]["x"]),
                                                float(json_file["acceleration_calibration"]["y"]),
                                                float(json_file["acceleration_calibration"]["z"]))
            flag |= True
    except RuntimeWarning as _ex:
        print("use_filtering read error")

    if "ax_filters" in json_file:
        for filter_id, filter_ in enumerate(json_file["ax_filters"]):
            try:
                if filter_id == len(acc.filters_ax):
                    acc.filters_ax.append(RealTimeFilter())
                    acc.filters_ax[-1].load_settings(filter_)
                    continue
                acc.filters_ax[filter_id].load_settings(filter_)
            except RuntimeWarning as _ex:
                print(f"Accelerometer load settings error :: incorrect ax_filters\n"
                      f"fiter_id: {filter_id}\nfilter:\n{filter_}")
                continue
        flag |= True

    if "ay_filters" in json_file:
        for filter_id, filter_ in enumerate(json_file["ay_filters"]):
            try:
                if filter_id == len(acc.filters_ay):
                    acc.filters_ay.append(RealTimeFilter())
                    acc.filters_ay[-1].load_settings(filter_)
                    continue
                acc.filters_ay[filter_id].load_settings(filter_)
            except RuntimeWarning as _ex:
                print(f"Accelerometer load settings error :: incorrect ay_filters\n"
                      f"fiter_id: {filter_id}\nfilter:\n{filter_}")
                continue
        flag |= True

    if "az_filters" in json_file:
        for filter_id, filter_ in enumerate(json_file["az_filters"]):
            try:
                if filter_id == len(acc.filters_az):
                    acc.filters_az.append(RealTimeFilter())
                    acc.filters_az[-1].load_settings(filter_)
                    continue
                acc.filters_az[filter_id].load_settings(filter_)
            except RuntimeWarning as _ex:
                print(f"Accelerometer load settings error :: incorrect az_filters\n"
                      f"fiter_id: {filter_id}\nfilter:\n{filter_}")
                continue
        flag |= True

    if "gx_filters" in json_file:
        for filter_id, filter_ in enumerate(json_file["gx_filters"]):
            try:
                if filter_id == len(acc.filters_gx):
                    acc.filters_gx.append(RealTimeFilter())
                    acc.filters_gx[-1].load_settings(filter_)
                    continue
                acc.filters_gx[filter_id].load_settings(filter_)
            except RuntimeWarning as _ex:
                print(f"Accelerometer load settings error :: incorrect gx_filters\n"
                      f"fiter_id: {filter_id}\nfilter:\n{filter_}")
                continue
        flag |= True

    if "gy_filters" in json_file:
        for filter_id, filter_ in enumerate(json_file["gy_filters"]):
            try:
                if filter_id == len(acc.filters_gy):
                    acc.filters_gy.append(RealTimeFilter())
                    acc.filters_gy[-1].load_settings(filter_)
                    continue
                acc.filters_gy[filter_id].load_settings(filter_)
            except RuntimeWarning as _ex:
                print(f"Accelerometer load settings error :: incorrect gy_filters\n"
                      f"fiter_id: {filter_id}\nfilter:\n{filter_}")
                continue
        flag |= True

    if "gz_filters" in json_file:
        for filter_id, filter_ in enumerate(json_file["gz_filters"]):
            try:
                if filter_id == len(acc.filters_gz):
                    acc.filters_gz.append(RealTimeFilter())
                    acc.filters_gz[-1].load_settings(filter_)
                    continue
                acc.filters_gz[filter_id].load_settings(filter_)
            except RuntimeWarning as _ex:
                print(f"Accelerometer load settings error :: incorrect gz_filters\n"
                      f"fiter_id: {filter_id}\nfilter:\n{filter_}")
                continue
        flag |= True
    acc.reset()
    return flag


def save_accelerometer_settings(acc: Accelerometer, settings_file: str) -> None:
    with open(settings_file, "wt") as output_file:
        print(acc, file=output_file)
