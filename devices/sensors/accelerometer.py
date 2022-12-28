""" for raspberry
import sys
sys.path.append('/home/pi/Desktop/accelerometer/sensors_utils')
from real_time_filter import RealTimeFilter
"""

from devices.sensors_utils.real_time_filter import RealTimeFilter
from matplotlib import pyplot as plt
from vmath.core.vectors import Vec3
from typing import List, Tuple
import numpy as np
import json
import time

try:
    # TODO add board version check
    import smbus
except ImportError as ex:
    print(f"SM Bus import error!!!\n{ex.args}")

GRAVITY_CONSTANT = 9.80665  # [m / sec^2]

# MPU-6050 Registers
PWR_MGMT_1 = 0x6B
SAMPLE_RATE_DIV = 0x19
MPU_CONFIG = 0x1A
ACCEL_CONFIG = 0x1C
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38

GYRO_X_OUT_H = 0x43
GYRO_Y_OUT_H = 0x45
GYRO_Z_OUT_H = 0x47

ACCEL_X_OUT_H = 0x3B
ACCEL_Y_OUT_H = 0x3D
ACCEL_Z_OUT_H = 0x3F

TEMP_OUT_H = 0x41

# Scale Modifiers
ACCEL_SCALE_MODIFIER_2G = 16384.0
ACCEL_SCALE_MODIFIER_4G = 8192.0
ACCEL_SCALE_MODIFIER_8G = 4096.0
ACCEL_SCALE_MODIFIER_16G = 2048.0

GYRO_SCALE_MODIFIER_250DEG = 131.0
GYRO_SCALE_MODIFIER_500DEG = 65.5
GYRO_SCALE_MODIFIER_1000DEG = 32.8
GYRO_SCALE_MODIFIER_2000DEG = 16.4

# Pre-defined ranges
ACCEL_RANGE_2G = 0x00
ACCEL_RANGE_4G = 0x08
ACCEL_RANGE_8G = 0x10
ACCEL_RANGE_16G = 0x18

GYRO_RANGE_250DEG = 0x00
GYRO_RANGE_500DEG = 0x08
GYRO_RANGE_1000DEG = 0x10
GYRO_RANGE_2000DEG = 0x18

# Filter settings
FILTER_BW_256 = 0x00
FILTER_BW_188 = 0x01
FILTER_BW_98 = 0x02
FILTER_BW_42 = 0x03
FILTER_BW_20 = 0x04
FILTER_BW_10 = 0x05
FILTER_BW_5 = 0x06

FILTER_GX = 0
FILTER_GY = 1
FILTER_GZ = 2

FILTER_AX = 3
FILTER_AY = 4
FILTER_AZ = 5


class Integrator3d:
    SQUARES: int = 0
    TRAPEZOID: int = 1
    SIMPSON: int = 2

    def __init__(self, start_val: Vec3 = Vec3(0.0)):
        self._last_val: Vec3 = start_val
        self._curr_val: Vec3 = start_val
        self._time_val: float = -1.0
        self._time_delta: float = 0.0
        self.__mode: int = Integrator3d.TRAPEZOID
        self.__integration_f = self.__trapezoid_int

    def __call__(self, arg: Vec3, t: float) -> Vec3:
        return self.integrate(arg, t)

    def __str__(self):
        return f"{{\n" \
               f"\"prev_val\"  : {self.prev_val},\n" \
               f"\"curr_val\"  : {self.curr_val},\n" \
               f"\"time_val\"  : {self.time_val},\n" \
               f"\"time_delta\": {self.time_delta}\n" \
               f"}}"

    @property
    def time_delta(self) -> float:
        return self._time_delta

    @property
    def time_val(self) -> float:
        return self._time_val

    @property
    def curr_val(self) -> Vec3:
        return self._curr_val

    @property
    def prev_val(self) -> Vec3:
        return self._last_val

    @property
    def mode(self) -> int:
        return self.__mode

    @mode.setter
    def mode(self, arg: int) -> None:
        if arg == Integrator3d.SQUARES:
            self.__mode = arg
            self.__integration_f = self.__squares_int
            return
        if arg == Integrator3d.TRAPEZOID:
            self.__mode = arg
            self.__integration_f = self.__trapezoid_int
            return
        if arg == Integrator3d.SIMPSON:
            self.__mode = arg
            self.__integration_f = self.__simpson_int
            return

    def __squares_int(self, arg: Vec3, dt: float) -> Vec3:
        return self.curr_val + arg * dt

    def __trapezoid_int(self, arg: Vec3, dt: float) -> Vec3:
        return self.curr_val + (self.curr_val + arg) * 0.5 * dt

    def __simpson_int(self, arg: Vec3, dt: float) -> Vec3:
        return (self.curr_val + arg) * 0.5 * dt

    def integrate(self, arg: Vec3, t: float) -> Vec3:
        if self._time_val < 0:
            self._time_val = t
            self._last_val = arg
            self._curr_val = arg
            self._time_delta = 0.0
            return self.curr_val

        self._time_delta = t - self._time_val
        self._time_val = t
        val = self.__integration_f(arg, self.time_delta)
        self._last_val = self._curr_val
        self._curr_val = val
        return self.curr_val

    def reset(self) -> None:
        self._last_val = Vec3(0.0)
        self._curr_val = Vec3(0.0)
        self._time_val = 0.0
        self._time_delta = 0.0


# Based on mpu 6050
class Accelerometer:
    """
    Диапазоны измеряемых ускорений
    """
    __filter_ranges = {256: FILTER_BW_256,
                       188: FILTER_BW_188,
                       98: FILTER_BW_98,
                       42: FILTER_BW_42,
                       20: FILTER_BW_20,
                       10: FILTER_BW_10,
                       5: FILTER_BW_5}
    """
    Диапазоны измеряемых ускорений
    """
    __acc_ranges = {2: ACCEL_RANGE_2G,
                    4: ACCEL_RANGE_4G,
                    8: ACCEL_RANGE_8G,
                    16: ACCEL_RANGE_16G}
    """
    Модификаторы масштаба для ускорений
    """
    __acc_scales = {ACCEL_RANGE_2G: ACCEL_SCALE_MODIFIER_2G,
                    ACCEL_RANGE_4G: ACCEL_SCALE_MODIFIER_4G,
                    ACCEL_RANGE_8G: ACCEL_SCALE_MODIFIER_8G,
                    ACCEL_RANGE_16G: ACCEL_SCALE_MODIFIER_16G}
    """
    Диапазоны измеряемых угловых скоростей
    """
    __gyro_ranges = {250: ACCEL_RANGE_2G,
                     500: ACCEL_RANGE_4G,
                     1000: ACCEL_RANGE_8G,
                     2000: ACCEL_RANGE_16G}
    """
    Модификаторы масштаба для угловых скоростей
    """
    __gyro_scales = {GYRO_RANGE_250DEG: GYRO_SCALE_MODIFIER_250DEG,
                     GYRO_RANGE_500DEG: GYRO_SCALE_MODIFIER_500DEG,
                     GYRO_RANGE_1000DEG: GYRO_SCALE_MODIFIER_1000DEG,
                     GYRO_RANGE_2000DEG: GYRO_SCALE_MODIFIER_2000DEG}

    def __init__(self, address: int = 0x68):
        self.__i2c_bus = None

        self.__address: int = address  # mpu 6050

        self.__filters: List[List[RealTimeFilter]] = []

        self.__acceleration_range: int = -1  # 2

        self.__acceleration_range_raw: int = -1

        self.__gyroscope_range: int = -1  # 250

        self.__gyroscope_range_raw: int = -1

        self.__hardware_filter_range_raw: int = -1

        self.__use_filtering: bool = True

        self.__angles_integrator: Integrator3d = Integrator3d()

        self.__velocity_integrator: Integrator3d = Integrator3d()

        self.__position_integrator: Integrator3d = Integrator3d()

        self.__gyro_clib: Vec3 = Vec3(0.0)
        self.__accel_clib: Vec3 = Vec3(0.0)

        self.__last_orientation: Vec3 = Vec3(0.0)
        self.__last_acceleration: Vec3 = Vec3(0.0)

    def __str__(self):
        separator = ",\n"
        return f"{{" \
               f"\t\"address\":                   {self.address},\n" \
               f"\t\"acceleration_range_raw\":    {self.acceleration_range_raw},\n" \
               f"\t\"acceleration_range\":        {self.acceleration_range},\n" \
               f"\t\"acceleration_scale\":        {self.acceleration_scale},\n" \
               f"\t\"gyroscope_range_raw\":       {self.gyroscope_range_raw},\n" \
               f"\t\"gyroscope_range\":           {self.gyroscope_range},\n" \
               f"\t\"gyroscope_scale\":           {self.gyroscope_scale},\n" \
               f"\t\"hardware_filter_range_raw\": {self.hardware_filter_range_raw},\n" \
               f"\t\"use_filtering\":             {self.use_filtering},\n" \
               f"\t\"ax_filters\":[\n{separator.join(str(f) for f in self.__filters[FILTER_AX])}\n\t],\n" \
               f"\t\"ay_filters\":[\n{separator.join(str(f) for f in self.__filters[FILTER_AY])}\n\t],\n" \
               f"\t\"az_filters\":[\n{separator.join(str(f) for f in self.__filters[FILTER_AZ])}\n\t],\n" \
               f"\t\"gx_filters\":[\n{separator.join(str(f) for f in self.__filters[FILTER_GX])}\n\t],\n" \
               f"\t\"gy_filters\":[\n{separator.join(str(f) for f in self.__filters[FILTER_GY])}\n\t],\n" \
               f"\t\"gz_filters\":[\n{separator.join(str(f) for f in self.__filters[FILTER_GZ])}\n\t]\n" \
               f"}}"

    def __enter__(self):
        if not self.init():
            raise Exception("accelerometer init error")
        return self

    def __default_settings(self) -> None:
        self.__filters.clear()
        for _ in range(6):
            _filter = RealTimeFilter()
            _filter.k_arg = 0.1
            _filter.kalman_error = 0.9
            _filter.mode = 2
            self.__filters.append([_filter])
        self.acceleration_range_raw = 2
        self.gyroscope_range_raw = 250

    def reset(self) -> None:
        for filter_list in self.__filters:
            for f in filter_list:
                f.clean_up()
        self.__gyro_clib = Vec3(0.0)
        self.__accel_clib = Vec3(0.0)
        self.__last_orientation = Vec3(0.0)
        self.__last_acceleration = Vec3(0.0)
        self.acceleration_range_raw = 2
        self.gyroscope_range_raw = 250

    def __read_acceleration_data(self) -> Tuple[bool, Vec3]:

        acceleration = Vec3(0.0)

        scl = 1.0 / self.acceleration_scale * GRAVITY_CONSTANT
        try:
            if self.__use_filtering:
                acceleration.x = self.__filter_ax(float(self.__read_unsafe(ACCEL_X_OUT_H)) * scl)
                acceleration.y = self.__filter_ay(float(self.__read_unsafe(ACCEL_Y_OUT_H)) * scl)
                acceleration.z = self.__filter_az(float(self.__read_unsafe(ACCEL_Z_OUT_H)) * scl)
            else:
                acceleration.x = float(self.__read_unsafe(ACCEL_X_OUT_H)) * scl
                acceleration.y = float(self.__read_unsafe(ACCEL_Y_OUT_H)) * scl
                acceleration.z = float(self.__read_unsafe(ACCEL_Z_OUT_H)) * scl
        except Exception as _ex:
            print(f"acceleration data read error\n{_ex.args}")
            return False, acceleration
        return True, acceleration

    def __read_gyro_data(self) -> Tuple[bool, Vec3]:

        orientation = Vec3(0.0)

        scl = 1.0 / self.gyroscope_scale

        try:
            if self.__use_filtering:
                orientation.x = self.__filter_gx(float(self.__read_unsafe(GYRO_X_OUT_H)) * scl)
                orientation.y = self.__filter_gy(float(self.__read_unsafe(GYRO_Y_OUT_H)) * scl)
                orientation.z = self.__filter_gz(float(self.__read_unsafe(GYRO_Z_OUT_H)) * scl)
            else:
                orientation.x = float(self.__read_unsafe(GYRO_X_OUT_H)) * scl
                orientation.y = float(self.__read_unsafe(GYRO_Y_OUT_H)) * scl
                orientation.z = float(self.__read_unsafe(GYRO_Z_OUT_H)) * scl
        except Exception as _ex:
            print(f"gyroscope data read error\n{_ex.args}")
            return False, orientation

        return True, orientation

    def __read_unsafe(self, addr: int) -> np.int16:
        # Accelerometer and Gyro value are 16-bit
        high = self.bus.read_byte_data(self.address, addr)
        low = self.bus.read_byte_data(self.address, addr + 1)
        # concatenate higher and lower value
        value = (high << 8) | low
        # to get signed value from mpu6050
        if value >= 0x8000:
            value -= 65536
        return value

    def __filter_value(self, val: float, filter_id: int) -> float:
        for _filter in self.__filters[filter_id]:
            val = _filter.filter(val)
        return val

    def __filter_ax(self, val: float) -> float:
        return self.__filter_value(val, FILTER_AX)

    def __filter_ay(self, val: float) -> float:
        return self.__filter_value(val, FILTER_AY)

    def __filter_az(self, val: float) -> float:
        return self.__filter_value(val, FILTER_AZ)

    def __filter_gx(self, val: float) -> float:
        return self.__filter_value(val, FILTER_GX)

    def __filter_gy(self, val: float) -> float:
        return self.__filter_value(val, FILTER_GY)

    def __filter_gz(self, val: float) -> float:
        return self.__filter_value(val, FILTER_GZ)

    @property
    def bus(self):
        return self.__i2c_bus

    @property
    def address(self) -> int:
        return self.__address

    @property
    def filters_ax(self) -> List[RealTimeFilter]:
        return self.__filters[FILTER_AX]

    @property
    def filters_ay(self) -> List[RealTimeFilter]:
        return self.__filters[FILTER_AY]

    @property
    def filters_az(self) -> List[RealTimeFilter]:
        return self.__filters[FILTER_AZ]

    @property
    def filters_gx(self) -> List[RealTimeFilter]:
        return self.__filters[FILTER_GX]

    @property
    def filters_gy(self) -> List[RealTimeFilter]:
        return self.__filters[FILTER_GY]

    @property
    def filters_gz(self) -> List[RealTimeFilter]:
        return self.__filters[FILTER_GZ]

    @property
    def use_filtering(self) -> bool:
        return self.__use_filtering

    @use_filtering.setter
    def use_filtering(self, val: bool) -> None:
        if self.__use_filtering == val:
            return
        self.__use_filtering = val
        if val:
            for channel_filters in self.__filters:
                for f in channel_filters:
                    f.clean_up()

    @property
    def acceleration_range_raw(self) -> int:
        """
        Диапазон измеряемых ускорений
        ACCEL_SCALE_MODIFIER_2G = 16384.0
        ACCEL_SCALE_MODIFIER_4G = 8192.0
        ACCEL_SCALE_MODIFIER_8G = 4096.0
        ACCEL_SCALE_MODIFIER_16G = 2048.0
        """
        return self.__acceleration_range_raw  # HardwareAccelerometer.__acc_ranges[self.__acceleration_range]

    @acceleration_range_raw.setter
    def acceleration_range_raw(self, accel_range: int) -> None:
        """
        Диапазон измеряемых ускорений
        ACCEL_SCALE_MODIFIER_2G = 16384.0
        ACCEL_SCALE_MODIFIER_4G = 8192.0
        ACCEL_SCALE_MODIFIER_8G = 4096.0
        ACCEL_SCALE_MODIFIER_16G = 2048.0
        """
        if accel_range not in Accelerometer.__acc_ranges:
            return
        self.__acceleration_range = accel_range
        self.__acceleration_range_raw = Accelerometer.__acc_ranges[self.__acceleration_range]
        self.bus.write_byte_data(self.address, ACCEL_CONFIG, 0x00)
        self.bus.write_byte_data(self.address, ACCEL_CONFIG, self.__acceleration_range_raw)

    @property
    def acceleration_range(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2
        """
        return self.__acceleration_range * GRAVITY_CONSTANT

    @property
    def acceleration_scale(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2
        """
        return Accelerometer.__acc_scales[self.acceleration_range_raw]

    @property
    def gyroscope_range_raw(self) -> int:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG = 0x00
        GYRO_RANGE_500DEG = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        return self.__gyroscope_range_raw  # HardwareAccelerometer.__acc_ranges[self.__acceleration_range]

    @gyroscope_range_raw.setter
    def gyroscope_range_raw(self, gyro_range: int) -> None:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG = 0x00
        GYRO_RANGE_500DEG = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        if gyro_range not in Accelerometer.__gyro_ranges:
            return
        self.__gyroscope_range = gyro_range
        self.__gyroscope_range_raw = Accelerometer.__gyro_ranges[self.__gyroscope_range]
        self.bus.write_byte_data(self.address, GYRO_CONFIG, 0x00)
        self.bus.write_byte_data(self.address, GYRO_CONFIG, self.__gyroscope_range_raw)

    @property
    def gyroscope_range(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2
        """
        return float(self.__gyroscope_range)

    @property
    def gyroscope_scale(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2
        """
        return Accelerometer.__gyro_scales[self.gyroscope_range_raw]

    @property
    def hardware_filter_range_raw(self) -> int:
        """
        Документация???
        """
        return self.__hardware_filter_range_raw

    @hardware_filter_range_raw.setter
    def hardware_filter_range_raw(self, filter_range: int) -> None:
        """
        Документация???
        """
        if filter_range not in Accelerometer.__filter_ranges:
            return
        self.__hardware_filter_range_raw = filter_range
        ext_sync_set = self.bus.read_byte_data(self.__address, MPU_CONFIG) & 0b00111000
        self.bus.write_byte_data(self.__address, MPU_CONFIG, ext_sync_set | self.__hardware_filter_range_raw)

    @property
    def angles_velocity(self) -> Vec3:
        return self.__last_orientation

    @property
    def angles(self) -> Vec3:
        return self.__angles_integrator.curr_val

    @property
    def acceleration(self) -> Vec3:
        return self.__last_acceleration

    @property
    def velocity(self) -> Vec3:
        return self.__velocity_integrator.curr_val

    @property
    def position(self) -> Vec3:
        return self.__position_integrator.curr_val

    @property
    def accel_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self.__velocity_integrator.time_val

    @property
    def accel_dt(self) -> float:
        """
        Прошедшее время между последним изменрением ускорения и предыдущим
        """
        return self.__velocity_integrator.time_delta

    @property
    def gyro_t(self) -> float:
        """
        Последнее время, когда были измерены угловые скорости
        """
        return self.__angles_integrator.time_val

    @property
    def gyro_dt(self) -> float:
        """
        Прошедшее время между последним изменрением скорости измениния углов и предыдущим
        """
        return self.__angles_integrator.time_delta

    def load_settings(self, json_settings_file: str) -> bool:
        json_file = None

        with open(json_settings_file, "wt") as output_file:
            json_file = json.load(output_file)
            if json_file is None:
                return False
        flag = False

        if "address" in json_file:
            prev_address = self.__address
            self.__address = int(json_file["address"])
            if not self.init():
                print("incorrect device address in HardwareAccelerometerSettings")
                self.__address = prev_address
                self.init()
                return flag
            flag |= True

        try:
            if "acceleration_range_raw" in json_file:
                self.acceleration_range_raw = int(json_file["acceleration_range_raw"])
                flag |= True
        except Exception as _ex:
            print("acceleration_range_raw read error")
            self.acceleration_range_raw = ACCEL_RANGE_2G

        try:
            if "gyroscope_range_raw" in json_file:
                self.gyroscope_range_raw = int(json_file["gyroscope_range_raw"])
                flag |= True
        except Exception as _ex:
            print("gyroscope_range_raw read error")
            self.acceleration_range_raw = GYRO_RANGE_250DEG

        try:
            if "hardware_filter_range_raw" in json_file:
                self.hardware_filter_range_raw = int(json_file["hardware_filter_range_raw"])
                flag |= True
        except Exception as _ex:
            print("hardware_filter_range_raw read error")

        try:
            if "use_filtering" in json_file:
                self.use_filtering = bool(json_file["use_filtering"])
                flag |= True
        except Exception as _ex:
            print("use_filtering read error")
        if "ax_filters" in json_file:
            for filter_id, filter_ in enumerate(json_file["ax_filters"]):
                try:
                    if filter_id == len(self.__filters[FILTER_AX]):
                        self.__filters[FILTER_AX].append(RealTimeFilter())
                        self.__filters[FILTER_AX][-1].load_settings(filter_)
                        continue
                    self.__filters[FILTER_AX][filter_id].load_settings(filter_)
                except Exception as _ex:
                    print(f"Accelerometer load settings error :: incorrect ax_filters\nfiter_id: {filter_id}\nfilter:\n{filter_}")
                    continue
            flag |= True

        if "ay_filters" in json_file:
            for filter_id, filter_ in enumerate(json_file["ay_filters"]):
                try:
                    if filter_id == len(self.__filters[FILTER_AY]):
                        self.__filters[FILTER_AY].append(RealTimeFilter())
                        self.__filters[FILTER_AY][-1].load_settings(filter_)
                        continue
                    self.__filters[FILTER_AY][filter_id].load_settings(filter_)
                except Exception as _ex:
                    print(f"Accelerometer load settings error :: incorrect ay_filters\nfiter_id: {filter_id}\nfilter:\n{filter_}")
                    continue
            flag |= True

        if "az_filters" in json_file:
            for filter_id, filter_ in enumerate(json_file["az_filters"]):
                try:
                    if filter_id == len(self.__filters[FILTER_AZ]):
                        self.__filters[FILTER_AZ].append(RealTimeFilter())
                        self.__filters[FILTER_AZ][-1].load_settings(filter_)
                        continue
                    self.__filters[FILTER_AZ][filter_id].load_settings(filter_)
                except Exception as _ex:
                    print(f"Accelerometer load settings error :: incorrect az_filters\nfiter_id: {filter_id}\nfilter:\n{filter_}")
                    continue
            flag |= True

        if "gx_filters" in json_file:
            for filter_id, filter_ in enumerate(json_file["gx_filters"]):
                try:
                    if filter_id == len(self.__filters[FILTER_GX]):
                        self.__filters[FILTER_GX].append(RealTimeFilter())
                        self.__filters[FILTER_GX][-1].load_settings(filter_)
                        continue
                    self.__filters[FILTER_GX][filter_id].load_settings(filter_)
                except Exception as _ex:
                    print(f"Accelerometer load settings error :: incorrect gx_filters\nfiter_id: {filter_id}\nfilter:\n{filter_}")
                    continue
            flag |= True

        if "gy_filters" in json_file:
            for filter_id, filter_ in enumerate(json_file["gy_filters"]):
                try:
                    if filter_id == len(self.__filters[FILTER_GY]):
                        self.__filters[FILTER_GY].append(RealTimeFilter())
                        self.__filters[FILTER_GY][-1].load_settings(filter_)
                        continue
                    self.__filters[FILTER_GY][filter_id].load_settings(filter_)
                except Exception as _ex:
                    print(f"Accelerometer load settings error :: incorrect gy_filters\nfiter_id: {filter_id}\nfilter:\n{filter_}")
                    continue
            flag |= True

        if "gz_filters" in json_file:
            for filter_id, filter_ in enumerate(json_file["gz_filters"]):
                try:
                    if filter_id == len(self.__filters[FILTER_GZ]):
                        self.__filters[FILTER_GZ].append(RealTimeFilter())
                        self.__filters[FILTER_GZ][-1].load_settings(filter_)
                        continue
                    self.__filters[FILTER_GZ][filter_id].load_settings(filter_)
                except Exception as _ex:
                    print(f"Accelerometer load settings error :: incorrect gz_filters\nfiter_id: {filter_id}\nfilter:\n{filter_}")
                    continue
            flag |= True

        self.reset()

        return flag

    def save_settings(self, json_settings_file: str) -> None:
        with open(json_settings_file, "wt") as output_file:
            print(self, file=output_file)

    def init(self) -> bool:
        try:
            self.__i2c_bus = smbus.SMBus(1)
            # or bus = smbus.SMBus(0) for older version boards
        except NameError as _ex:
            print(f"SM Bus init error!!!\n{_ex.args}")
            return False
        try:
            # Write to power management register
            self.bus.write_byte_data(self.address, PWR_MGMT_1, 1)

            # write to sample rate register
            self.bus.write_byte_data(self.address, SAMPLE_RATE_DIV, 7)

            # Write to Configuration register
            self.bus.write_byte_data(self.address, MPU_CONFIG, 0)

            # Write to Gyro configuration register
            self.bus.write_byte_data(self.address, GYRO_CONFIG, 24)

            # Write to interrupt enable register
            self.bus.write_byte_data(self.address, INT_ENABLE, 1)
        except AttributeError as ex_:
            print(f"Accelerometer init error {ex_.args}")
            return False

        self.__default_settings()

        return True

    def calibrate(self, calib_time: float = 2.0) -> None:
        n_measurement = 0.0
        self.__gyro_clib = Vec3(0.0)
        self.__accel_clib = Vec3(0.0)
        t = time.perf_counter()
        while time.perf_counter() - t < calib_time:
            n_measurement += 1.0
            flag, val = self.__read_gyro_data()
            if not flag:
                self.__gyro_clib = Vec3(0.0)
                self.__accel_clib = Vec3(0.0)
                print("calibration failed")
                break
            self.__gyro_clib += val
            flag, val = self.__read_acceleration_data()
            if not flag:
                self.__gyro_clib = Vec3(0.0)
                self.__accel_clib = Vec3(0.0)
                print("calibration failed")
                break
            self.__accel_clib += val

        scl = 1.0 / n_measurement

        self.__gyro_clib *= scl

        self.__accel_clib *= scl

        print(f"{{\n"
              f"\"calibration_info\":\n"
              f"\t{{\n"
              f"\t\t\"n_measurements\":{n_measurement},\n"
              f"\t\t\"a_calib\"       :{self.__accel_clib},\n"
              f"\t\t\"o_calib\"       :{self.__gyro_clib}\n"
              f"\t}}\n"
              f"}}")

    def read_accel_measurements(self) -> bool:
        flag1, val = self.__read_acceleration_data()
        if flag1:
            self.__last_acceleration = val - self.__accel_clib
            self.__velocity_integrator(self.acceleration, time.perf_counter())
            self.__position_integrator(self.__velocity_integrator.curr_val, time.perf_counter())

        flag2, val = self.__read_gyro_data()
        if flag2:
            self.__last_orientation = val - self.__gyro_clib
            self.__angles_integrator(self.angles_velocity, time.perf_counter())
        return flag2 or flag1


def integrator_test(n_points: int = 1024):
    dx = 1.0 / (n_points - 1)
    x = [dx * i for i in range(n_points)]
    print(f"sum(x) = {sum(x) * dx}")
    integrator = Integrator3d()
    integrator.mode = 1
    y = []
    for xi in x:
        y.append(integrator(Vec3(xi), xi).x)

    plt.plot(x, x, 'r')
    plt.plot(x, y, 'g')
    plt.show()


def accelerometer_test():
    accelerometer = Accelerometer()

    if not accelerometer.init():
        print("accelerometer init failed")
        exit(-1)

    print(accelerometer)

    accelerometer.use_filtering = True

    accelerometer.calibrate()

    with open("../sensors_utils/still.json", 'wt') as out_put:
        print("{\n\"way_points\":[", file=out_put)
        for _ in range(2048):
            accelerometer.read_accel_measurements()
            print("\t{\n", file=out_put)
            print(f"\t\"angles_velocity\": {accelerometer.angles_velocity},", file=out_put)
            print(f"\t\"angles\"         : {accelerometer.angles},", file=out_put)
            print(f"\t\"acceleration\"   : {accelerometer.acceleration},", file=out_put)
            print(f"\t\"velocity\"       : {accelerometer.velocity},", file=out_put)
            print(f"\t\"position\"       : {accelerometer.position},", file=out_put)
            print(f"\t\"time_delta\"     : {accelerometer.accel_dt},", file=out_put)
            print(f"\t\"time\"           : {accelerometer.accel_t}", file=out_put)
            print("\t},", file=out_put)
        print("\t]\n}", file=out_put)
    with open('accelerometer_settings.json', 'wt') as out_put:
        print(accelerometer, file=out_put)


if __name__ == "__main__":
    integrator_test()
    accelerometer_test()

