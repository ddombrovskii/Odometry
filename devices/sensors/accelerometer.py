from devices.sensors_utils.real_time_filter import RealTimeFilter
from vmath.core.vectors import Vec3
from typing import List, Tuple
import numpy as np
import dataclasses
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


@dataclasses.dataclass
class AccelerometerSettings:
    address: int
    acceleration_range_raw: int
    gyroscope_range_raw: int
    hardware_filter_range_raw: int
    use_filtering: bool
    ax_filters: List[RealTimeFilter]
    ay_filters: List[RealTimeFilter]
    az_filters: List[RealTimeFilter]
    gx_filters: List[RealTimeFilter]
    gy_filters: List[RealTimeFilter]
    gz_filters: List[RealTimeFilter]


# Based on mpu 6050
class Accelerometer:
    """
    Диапазоны измеряемых ускорений
    """
    __filter_ranges = {256: FILTER_BW_256,
                       188: FILTER_BW_188,
                       98:  FILTER_BW_98,
                       42:  FILTER_BW_42,
                       20:  FILTER_BW_20,
                       10:  FILTER_BW_10,
                       5:   FILTER_BW_5}
    """
    Диапазоны измеряемых ускорений
    """
    __acc_ranges = {2:  ACCEL_RANGE_2G,
                    4:  ACCEL_RANGE_4G,
                    8:  ACCEL_RANGE_8G,
                    16: ACCEL_RANGE_16G}
    """
    Модификаторы масштаба для ускорений
    """
    __acc_scales = {ACCEL_RANGE_2G:  ACCEL_SCALE_MODIFIER_2G,
                    ACCEL_RANGE_4G:  ACCEL_SCALE_MODIFIER_4G,
                    ACCEL_RANGE_8G:  ACCEL_SCALE_MODIFIER_8G,
                    ACCEL_RANGE_16G: ACCEL_SCALE_MODIFIER_16G}
    """
    Диапазоны измеряемых угловых скоростей
    """
    __gyro_ranges = {250:  ACCEL_RANGE_2G,
                     500:  ACCEL_RANGE_4G,
                     1000: ACCEL_RANGE_8G,
                     2000: ACCEL_RANGE_16G}
    """
    Модификаторы масштаба для угловых скоростей
    """
    __gyro_scales = {GYRO_RANGE_250DEG:  GYRO_SCALE_MODIFIER_250DEG,
                     GYRO_RANGE_500DEG:  GYRO_SCALE_MODIFIER_500DEG,
                     GYRO_RANGE_1000DEG: GYRO_SCALE_MODIFIER_1000DEG,
                     GYRO_RANGE_2000DEG: GYRO_SCALE_MODIFIER_2000DEG}

    def __init__(self, address: int = 0x68):
        self.__i2c_bus = None

        self.__address: int = address  # mpu 6050

        self.__filters: List[List[RealTimeFilter]] = []

        self.__acceleration_range: int = -1  # 2

        self.__acceleration_range_raw: int = -1  # HardwareAccelerometer.__acc_ranges[self.__acceleration_range]

        self.__gyroscope_range: int = -1  # 250

        self.__gyroscope_range_raw: int = -1  # HardwareAccelerometer.__gyro_ranges[self.__gyroscope_range]

        self.__hardware_filter_range_raw: int = -1

        self.__use_filtering: bool = True

        self.__time_a_0: float = time.perf_counter()
        self.__time_a: float = 0.0
        self.__d_time_a: float = 0.0

        self.__time_g_0: float = time.perf_counter()
        self.__time_g: float = 0.0
        self.__d_time_g: float = 0.0

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
               f"\t\"ax_filters\":{{\n{separator.join(str(f) for f in self.__filters[FILTER_AX])}\t}},\n" \
               f"\t\"ay_filters\":{{\n{separator.join(str(f) for f in self.__filters[FILTER_AY])}\t}},\n" \
               f"\t\"az_filters\":{{\n{separator.join(str(f) for f in self.__filters[FILTER_AZ])}\t}},\n" \
               f"\t\"gx_filters\":{{\n{separator.join(str(f) for f in self.__filters[FILTER_GX])}\t}},\n" \
               f"\t\"gy_filters\":{{\n{separator.join(str(f) for f in self.__filters[FILTER_GY])}\t}},\n" \
               f"\t\"gz_filters\":{{\n{separator.join(str(f) for f in self.__filters[FILTER_GZ])}\t}}\n" \
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

    def __read_acceleration_data(self) -> Tuple[bool, Vec3]:

        acceleration = Vec3(0.0)

        scl = 1.0 / self.acceleration_scale * GRAVITY_CONSTANT

        self.__d_time_a = time.perf_counter() - self.__time_a - self.__time_a_0

        self.__time_a += self.__d_time_a

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

        self.__d_time_g = time.perf_counter() - self.__time_g - self.__time_g_0

        self.__time_g += self.__d_time_g

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
    def settings(self) -> AccelerometerSettings:
        return AccelerometerSettings(self.address, self.acceleration_range_raw,
                                     self.gyroscope_range_raw, self.hardware_filter_range_raw,
                                     self.use_filtering,
                                     self.__filters[FILTER_AX], self.__filters[FILTER_AY],
                                     self.__filters[FILTER_AZ], self.__filters[FILTER_GX],
                                     self.__filters[FILTER_GY], self.__filters[FILTER_GZ])

    @settings.setter
    def settings(self, settings_set: AccelerometerSettings) -> None:
        prev_address = self.__address
        self.__address = settings_set.address
        if not self.init():
            print("incorrect device address in HardwareAccelerometerSettings")
            self.__address = prev_address
            self.init()
            return
        self.acceleration_range_raw = settings_set.acceleration_range_raw
        self.gyroscope_range_raw = settings_set.gyroscope_range_raw
        self.hardware_filter_range_raw = settings_set.hardware_filter_range_raw
        self.use_filtering = settings_set.use_filtering

        self.__filters[FILTER_AX] = settings_set.ax_filters
        self.__filters[FILTER_AY] = settings_set.ay_filters
        self.__filters[FILTER_AZ] = settings_set.az_filters

        self.__filters[FILTER_GX] = settings_set.gx_filters
        self.__filters[FILTER_GY] = settings_set.gy_filters
        self.__filters[FILTER_GZ] = settings_set.gz_filters

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
    def bus(self):
        return self.__i2c_bus

    @property
    def address(self) -> int:
        return self.__address

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
    def orientation(self) -> Vec3:
        flag, val = self.__read_gyro_data()
        if flag:
            self.__last_orientation = val - self.__gyro_clib
            return self.__last_orientation
        return self.__last_orientation

    @property
    def acceleration(self) -> Vec3:
        flag, val = self.__read_acceleration_data()
        if flag:
            self.__last_acceleration = val - self.__accel_clib
            return self.__last_acceleration
        return self.__last_acceleration

    @property
    def last_orientation(self) -> Vec3:
        return self.__last_orientation

    @property
    def last_acceleration(self) -> Vec3:
        return self.__last_acceleration

    @property
    def last_accel_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self.__time_a

    @property
    def last_accel_dt(self) -> float:
        """
        Прошедшее время между последним изменрением ускорения и предыдущим
        """
        return self.__d_time_a

    @property
    def last_gyro_t(self) -> float:
        """
        Последнее время, когда были измерены угловые скорости
        """
        return self.__time_g

    @property
    def last_gyro_dt(self) -> float:
        """
        Прошедшее время между последним изменрением скорости измениния углов и предыдущим
        """
        return self.__d_time_g

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

        self.__time_a_0 = time.perf_counter()
        self.__time_a = 0.0
        self.__d_time_a = 0.0

        self.__time_g_0 = time.perf_counter()
        self.__time_g = 0.0
        self.__d_time_g = 0.0

        print(f"{{\n"
              f"\"calibration_info\":\n"
              f"\t{{\n"
              f"\t\t\"n_measurements\":{n_measurement},\n"
              f"\t\t\"a_calib\"       :{self.__accel_clib},\n"
              f"\t\t\"o_calib\"       :{self.__gyro_clib}\n"
              f"\t}}\n"
              f"}}")


if __name__ == "__main__":

    accelerometer = Accelerometer()

    if not accelerometer.init():
        print("accelerometer init failed")
        exit(-1)

    print(accelerometer)

    accelerometer.use_filtering = True

    accelerometer.calibrate()

    for _ in range(32):
        print(f"t: {accelerometer.last_accel_t}, dt: {accelerometer.last_accel_dt}")
        print(f"a: {accelerometer.acceleration}")
        time.sleep(0.1)

    for _ in range(32):
        print(f"t: {accelerometer.last_gyro_t} dt: {accelerometer.last_gyro_dt}")
        print(f"a: {accelerometer.orientation}")
        time.sleep(0.1)
