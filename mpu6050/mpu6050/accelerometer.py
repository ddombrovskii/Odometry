from cgeo import rot_m_to_euler_angles, Mat4
from cgeo.filtering import RealTimeFilter
from accelerometer_constants import *
from typing import List, Tuple
from cgeo.vectors import Vec3
import numpy as np
import cgeo.mutils
import random
import math
import time


_import_success = False


class BusDummy:
    @staticmethod
    def accel_x(t: float, step: float = 10, width: float = .5) -> float:
        amp = 10.0
        val =  math.exp(-(t - 20 - 1.0 * step) ** 2 / width ** 2) * amp + \
              -math.exp(-(t - 20 - 2.0 * step) ** 2 / width ** 2) * amp + \
              -math.exp(-(t - 20 - 3.0 * step) ** 2 / width ** 2) * amp + \
               math.exp(-(t - 20 - 4.0 * step) ** 2 / width ** 2) * amp

        if abs(val) < 1e-12:
            return 0.0 + random.uniform(-0.1, 0.1)
        return val + random.uniform(-0.1, 0.1)

    @staticmethod
    def accel_z(t: float, step: float = 10, width: float = .5) -> float:
        return BusDummy.accel_x(t + 10, step, width)

    def __init__(self):
        self.__registers = {ACCEL_X_OUT_H: lambda x: BusDummy.accel_x(2.5 * x),
                            ACCEL_Y_OUT_H: lambda x: 0.0,
                            ACCEL_Z_OUT_H: lambda x: BusDummy.accel_z(2.5 * x)}
        self.__t_start = time.perf_counter()

    def SMBus(self, a: int):
        return self

    def write_byte_data(self, a: int, b: int, c: int):
        pass

    def read_byte_data(self, a: int, register: int):
        if register in self.__registers:
            return self.__registers[register](time.perf_counter() - self.__t_start)
        return 0


try:
    import smbus
    _import_success = True

# TODO add board version check
except ImportError as ex:
    smbus = BusDummy()
    _import_success = False
    print(f"SM Bus import error!!!\n{ex.args}")


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
        self.__use_filtering: bool = False

        self.__t_curr: float = 0.0
        self.__t_prev: float = 0.0
        self.__t_start: float = time.perf_counter()

        self.__acceleration:  Vec3 = Vec3(0.0)
        self.__velocity:      Vec3 = Vec3(0.0)
        self.__position:      Vec3 = Vec3(0.0)
        self.__velocity_prev: Vec3 = Vec3(0.0)
        self.__acceleration_prev: Vec3 = Vec3(0.0)

        self.__velocity_ang: Vec3 = Vec3(0.0)
        self.__angles:       Vec3 = Vec3(0.0)
        self.__velocity_ang_prev:  Vec3 = Vec3(0.0)

        self.__gyro_calib:  Vec3 = Vec3(0.0)
        self.__accel_calib: Vec3 = Vec3(0.0)

        if not self.__init_bus():
            raise RuntimeError("Accelerometer init failed")

    def __str__(self):
        separator = ",\n"
        return f"{{\n" \
               f"\t\"address\":                    {self.address},\n" \
               f"\t\"acceleration_range_raw\":     {self.acceleration_range_raw},\n" \
               f"\t\"acceleration_range\":         {self.acceleration_range},\n" \
               f"\t\"acceleration_scale\":         {self.acceleration_scale},\n" \
               f"\t\"gyroscope_range_raw\":        {self.gyroscope_range_raw},\n" \
               f"\t\"gyroscope_range\":            {self.gyroscope_range},\n" \
               f"\t\"gyroscope_scale\":            {self.gyroscope_scale},\n" \
               f"\t\"hardware_filter_range_raw\":  {self.hardware_filter_range_raw},\n" \
               f"\t\"use_filtering\":              {'true' if self.use_filtering else 'false'},\n" \
               f"\t\"angles_velocity_calibration\":{self.angles_velocity_calibration},\n" \
               f"\t\"acceleration_calibration\":   {self.acceleration_calibration},\n" \
               f"\t\"ax_filters\":[\n{separator.join(str(f) for f in self.__filters[FILTER_AX])}\n\t],\n" \
               f"\t\"ay_filters\":[\n{separator.join(str(f) for f in self.__filters[FILTER_AY])}\n\t],\n" \
               f"\t\"az_filters\":[\n{separator.join(str(f) for f in self.__filters[FILTER_AZ])}\n\t],\n" \
               f"\t\"gx_filters\":[\n{separator.join(str(f) for f in self.__filters[FILTER_GX])}\n\t],\n" \
               f"\t\"gy_filters\":[\n{separator.join(str(f) for f in self.__filters[FILTER_GY])}\n\t],\n" \
               f"\t\"gz_filters\":[\n{separator.join(str(f) for f in self.__filters[FILTER_GZ])}\n\t]\n" \
               f"}}"

    def __enter__(self):
        # if not self.init():
        #    raise Exception("accelerometer init error")
        return self

    def __init_bus(self) -> bool:
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

    def __read_bus(self, addr: int) -> np.int16:
        if not _import_success:
            return self.bus.read_byte_data(self.address, addr)
        # Accelerometer and Gyro value are 16-bit
        high = self.bus.read_byte_data(self.address, addr)
        low  = self.bus.read_byte_data(self.address, addr + 1)
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

    def __read_acceleration_data(self) -> Tuple[bool, Tuple[float, float, float]]:

        scl = 1.0 / self.acceleration_scale * GRAVITY_CONSTANT

        try:
            if self.__use_filtering:
                return True, (self.__filter_value(float(self.__read_bus(ACCEL_X_OUT_H)) * scl, FILTER_AX),
                              self.__filter_value(float(self.__read_bus(ACCEL_Y_OUT_H)) * scl, FILTER_AY),
                              self.__filter_value(float(self.__read_bus(ACCEL_Z_OUT_H)) * scl, FILTER_AZ))
            return True, (float(self.__read_bus(ACCEL_X_OUT_H)) * scl,
                          float(self.__read_bus(ACCEL_Y_OUT_H)) * scl,
                          float(self.__read_bus(ACCEL_Z_OUT_H)) * scl)
        except Exception as _ex:
            print(f"acceleration data read error\n{_ex.args}")
            return False, (0.0, 0.0, 0.0)
            
    def __read_gyro_data(self) -> Tuple[bool, Tuple[float, float, float]]:
        scl = 1.0 / self.gyroscope_scale
        try:
            if self.__use_filtering:
                return True, (self.__filter_value(float(self.__read_bus(GYRO_X_OUT_H)) * scl, FILTER_GX),
                              self.__filter_value(float(self.__read_bus(GYRO_Y_OUT_H)) * scl, FILTER_GY),
                              self.__filter_value(float(self.__read_bus(GYRO_Z_OUT_H)) * scl, FILTER_GZ))
            return True, (float(self.__read_bus(GYRO_X_OUT_H)) * scl,
                          float(self.__read_bus(GYRO_Y_OUT_H)) * scl,
                          float(self.__read_bus(GYRO_Z_OUT_H)) * scl)
        except Exception as _ex:
            print(f"gyroscope data read error\n{_ex.args}")
            return False, (0.0, 0.0, 0.0)

    def __compute_start_params(self, compute_time: float = 10.0, forward: Vec3 = None):
        self.reset()
        t = time.perf_counter()
        accel = Vec3()
        n_accel_read = 0
        n_angel_read = 0
        while time.perf_counter() - t < compute_time:
            flag, val = self.__read_acceleration_data()
            if flag:
                accel.x += val[0]
                accel.y += val[1]
                accel.z += val[2]
                n_accel_read += 1
            flag, val = self.__read_gyro_data()
            if flag:
                self.__gyro_calib.x += val[0]
                self.__gyro_calib.y += val[1]
                self.__gyro_calib.z += val[2]
                n_angel_read += 1

        self.__gyro_calib.x /= n_angel_read
        self.__gyro_calib.y /= n_angel_read
        self.__gyro_calib.z /= n_angel_read
        self.__angles.x = self.__gyro_calib.x
        self.__angles.y = self.__gyro_calib.y
        self.__angles.z = self.__gyro_calib.z
        accel.x /= n_accel_read
        accel.y /= n_accel_read
        accel.z /= n_accel_read

        ey = accel.normalized()
        ex = Vec3.cross(ey, Vec3(0, 0, 1)) if forward is None else Vec3.cross(accel, forward)
        ez = Vec3.cross(ex, ey)

        self.__angles_start = rot_m_to_euler_angles(Mat4(ex.x, ey.x, ez.x, 0.0,
                                                         ex.y, ey.y, ez.y, 0.0,
                                                         ex.z, ey.z, ez.z, 0.0,
                                                         0.0, 0.0, 0.0, 1.0))

        self.__accel_calib.x = -ex.x * accel.x + ex.y * accel.y + ex.z * accel.z
        self.__accel_calib.y = -ey.x * accel.x + ey.y * accel.y + ey.z * accel.z
        self.__accel_calib.z = -ez.x * accel.x + ez.y * accel.y + ez.z * accel.z

    @property
    def bus(self):
        return self.__i2c_bus

    @property
    def address(self) -> int:
        return self.__address

    @address.setter
    def address(self, address: int) -> None:
        prev_address: int = self.address
        self.__address = address
        if not self.__init_bus():
            print("incorrect device address in HardwareAccelerometerSettings")
            self.__address = prev_address
            self.__init_bus()

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
        return self.__acceleration_range_raw

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
        return self.__gyroscope_range_raw

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
    def angles_velocity_calibration(self) -> Vec3:
        return self.__gyro_calib

    @property
    def acceleration_calibration(self) -> Vec3:
        return self.__accel_calib

    @property
    def angles_velocity(self) -> Vec3:
        return self.__velocity_ang

    @property
    def angles(self) -> Vec3:
        return self.__angles

    @property
    def acceleration(self) -> Vec3:
        return self.__acceleration

    @property
    def velocity(self) -> Vec3:
        return self.__velocity

    @property
    def position(self) -> Vec3:
        return self.__position

    @property
    def delta_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self.curr_t - self.prev_t

    @property
    def curr_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self.__t_curr

    @property
    def prev_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self.__t_prev

    def reset(self, reset_ranges: bool = False) -> None:
        for filter_list in self.__filters:
            for f in filter_list:
                f.clean_up()

        self.__acceleration  = Vec3(0.0)
        self.__velocity      = Vec3(0.0)
        self.__position      = Vec3(0.0)
        self.__velocity_prev = Vec3(0.0)
        self.__acceleration_prev = Vec3(0.0)

        self.__velocity_ang  = Vec3(0.0)
        self.__angles        = Vec3(0.0)
        self.__velocity_ang_prev = Vec3(0.0)

        self.__gyro_calib    = Vec3(0.0)
        self.__accel_calib   = Vec3(0.0)

        if reset_ranges:
            self.acceleration_range_raw = 2
            self.gyroscope_range_raw = 250

    def calibrate(self, calib_time: float = 10.0, forward: Vec3 = None) -> None:
        _use_filtering = self.use_filtering
        self.use_filtering = not _use_filtering
        # self.reset()
        self.__compute_start_params(calib_time, forward)
        self.__t_start = time.perf_counter()
        print(f"{{\n"
              f"\"calibration_info\":\n"
              f"\t{{\n"
              f"\t\t\"ang_start\"   :{self.__angles_start},\n"
              f"\t\t\"accel_calib\" :{self.__accel_calib},\n"
              f"\t\t\"ang_calib\"   :{self.__gyro_calib}\n"
              f"\t}}\n"
              f"}}")

    def angles_fast(self) -> Tuple[float, float, float]:
        return math.pi + math.atan2(self.acceleration.z, self.acceleration.z),\
               math.pi + math.atan2(self.acceleration.y, self.acceleration.z),\
               math.pi + math.atan2(self.acceleration.y, self.acceleration.x)

    def read_accel_measurements(self, kx: float = 0.95, ky: float = 1.0, kz: float = 0.95) -> bool:
        dt: float = self.delta_t * 0.5
        self.__t_prev = self.__t_curr
        self.__t_curr = time.perf_counter() - self.__t_start
        # print(dt)
        _2pi: float = math.pi * 2.0

        flag1, val = self.__read_acceleration_data()

        if flag1:
            self.__acceleration.x = val[0] - self.acceleration_calibration.x
            self.__acceleration.y = val[1] - self.acceleration_calibration.y
            self.__acceleration.z = val[2] - self.acceleration_calibration.z
            
            self.__velocity.x += (self.__acceleration_prev.x + self.__acceleration.x ) * dt 
            self.__velocity.y += (self.__acceleration_prev.y + self.__acceleration.y ) * dt 
            self.__velocity.z += (self.__acceleration_prev.z + self.__acceleration.z ) * dt 
            
            self.__acceleration_prev.x = self.__acceleration.x
            self.__acceleration_prev.y = self.__acceleration.y
            self.__acceleration_prev.z = self.__acceleration.z
            
            self.__position.x += (self.__velocity_prev.x + self.__velocity.x) * dt
            self.__position.y += (self.__velocity_prev.y + self.__velocity.y) * dt
            self.__position.z += (self.__velocity_prev.z + self.__velocity.z) * dt
            
            self.__velocity_prev.x = self.__velocity.x
            self.__velocity_prev.y = self.__velocity.y
            self.__velocity_prev.z = self.__velocity.z

        flag2, val = self.__read_gyro_data()
        if flag2:
            self.__velocity_ang.x = val[0] - self.angles_velocity_calibration.x
            self.__velocity_ang.y = val[1] - self.angles_velocity_calibration.y
            self.__velocity_ang.z = val[2] - self.angles_velocity_calibration.z
    
            self.__angles.x += (self.__velocity_ang_prev.x + self.__velocity_ang.x) * dt
            self.__angles.y += (self.__velocity_ang_prev.y + self.__velocity_ang.y) * dt
            self.__angles.z += (self.__velocity_ang_prev.z + self.__velocity_ang.z) * dt
            
            self.__velocity_ang_prev.x = self.__velocity_ang.x
            self.__velocity_ang_prev.y = self.__velocity_ang.y
            self.__velocity_ang_prev.z = self.__velocity_ang.z
            
            ax, ay, az = self.angles_fast()
            kx = cgeo.mutils.clamp(kx, 0.0, 1.0)
            ky = cgeo.mutils.clamp(ky, 0.0, 1.0)
            kz = cgeo.mutils.clamp(kz, 0.0, 1.0)
            self.__angles.x = (self.__angles.x * kx + ax * (1.0 - kx))
            self.__angles.y = (self.__angles.y * ky + ay * (1.0 - ky))
            self.__angles.z = (self.__angles.z * kz + az * (1.0 - kz))

        return flag2 or flag1
