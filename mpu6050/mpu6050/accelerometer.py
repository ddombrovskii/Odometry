from cgeo.numeric_methods import Integrator3d
from cgeo.filtering import RealTimeFilter
from typing import List, Tuple
from cgeo.vectors import Vec3
from constatnts import *
import numpy as np
import time


class BusDummy:
    def __init__(self):
        pass

    def SMBus(self, a: int):
        return self

    def write_byte_data(self, a: int, b: int, c: int):
        pass

    def read_byte_data(self, a: int, b: int):
        return 0


try:
    import smbus
# TODO add board version check
except ImportError as ex:
    smbus = BusDummy()
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

        self.__use_filtering: bool = True

        self.__angles_integrator: Integrator3d = Integrator3d()

        self.__velocity_integrator: Integrator3d = Integrator3d()

        self.__position_integrator: Integrator3d = Integrator3d()

        self.__gyro_calib: Vec3 = Vec3(0.0)
        self.__accel_calib: Vec3 = Vec3(0.0)

        self.__angles_velocity: Vec3 = Vec3(0.0)
        self.__accelerations: Vec3 = Vec3(0.0)

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

    def __read_bus(self, addr: int, skip_2_bits: bool = False) -> np.int16:
        # Accelerometer and Gyro value are 16-bit
        high = self.bus.read_byte_data(self.address, addr)
        low = self.bus.read_byte_data(self.address, addr + 1)
        # concatenate higher and lower value
        if skip_2_bits:
            value = (high << 8) | (low & 252)
        else:
            value = (high << 8) | low
        # to get signed value from mpu6050
        if value >= 0x8000:
            value -= 65536
        return value

    def __filter_value(self, val: float, filter_id: int) -> float:
        for _filter in self.__filters[filter_id]:
            val = _filter.filter(val)
        return val

    def __read_acceleration_data(self) -> Tuple[bool, Vec3]:

        acceleration = Vec3(0.0)

        scl = 1.0 / self.acceleration_scale * GRAVITY_CONSTANT

        try:
            if self.__use_filtering:
                acceleration.x = self.__filter_value(float(self.__read_bus(ACCEL_X_OUT_H)) * scl, FILTER_AX)
                acceleration.y = self.__filter_value(float(self.__read_bus(ACCEL_Y_OUT_H)) * scl, FILTER_AY)
                acceleration.z = self.__filter_value(float(self.__read_bus(ACCEL_Z_OUT_H)) * scl, FILTER_AZ)
            else:
                acceleration.x = float(self.__read_bus(ACCEL_X_OUT_H)) * scl
                acceleration.y = float(self.__read_bus(ACCEL_Y_OUT_H)) * scl
                acceleration.z = float(self.__read_bus(ACCEL_Z_OUT_H)) * scl
        except Exception as _ex:
            print(f"acceleration data read error\n{_ex.args}")
            return False, acceleration
        return True, acceleration

    def __read_gyro_data(self) -> Tuple[bool, Vec3]:

        orientation = Vec3(0.0)

        scl = 1.0 / self.gyroscope_scale

        try:
            if self.__use_filtering:
                orientation.x = self.__filter_value(float(self.__read_bus(GYRO_X_OUT_H)) * scl, FILTER_GX)
                orientation.y = self.__filter_value(float(self.__read_bus(GYRO_Y_OUT_H)) * scl, FILTER_GY)
                orientation.z = self.__filter_value(float(self.__read_bus(GYRO_Z_OUT_H)) * scl, FILTER_GZ)
            else:
                orientation.x = float(self.__read_bus(GYRO_X_OUT_H)) * scl
                orientation.y = float(self.__read_bus(GYRO_Y_OUT_H)) * scl
                orientation.z = float(self.__read_bus(GYRO_Z_OUT_H)) * scl
        except Exception as _ex:
            print(f"gyroscope data read error\n{_ex.args}")
            return False, orientation

        return True, orientation

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
    def angles_velocity_calibration(self) -> Vec3:
        return self.__gyro_calib

    @property
    def acceleration_calibration(self) -> Vec3:
        return self.__accel_calib

    @angles_velocity_calibration.setter
    def angles_velocity_calibration(self, val: Vec3) -> None:
        self.__gyro_calib = val

    @acceleration_calibration.setter
    def acceleration_calibration(self, val: Vec3) -> None:
        self.__accel_calib = val

    @property
    def angles_velocity(self) -> Vec3:
        return self.__angles_velocity

    @property
    def angles(self) -> Vec3:
        return self.__angles_integrator.curr_val

    @property
    def acceleration(self) -> Vec3:
        return self.__accelerations

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

    def reset(self, reset_ranges: bool = False, reset_calibration: bool = False) -> None:
        for filter_list in self.__filters:
            for f in filter_list:
                f.clean_up()
        self.__angles_velocity = Vec3(0.0)
        self.__accelerations = Vec3(0.0)
        if reset_ranges:
            self.acceleration_range_raw = 2
            self.gyroscope_range_raw = 250
        if reset_calibration:
            self.__gyro_calib = Vec3(0.0)
            self.__accel_calib = Vec3(0.0)

    def calibrate(self, calib_time: float = 2.0) -> None:
        n_measurement = 0.0
        self.__gyro_calib = Vec3(0.0)
        self.__accel_calib = Vec3(0.0)
        t = time.perf_counter()
        while time.perf_counter() - t < calib_time:
            n_measurement += 1.0
            flag, val = self.__read_gyro_data()
            if not flag:
                self.__gyro_calib = Vec3(0.0)
                self.__accel_calib = Vec3(0.0)
                print("calibration failed")
                break
            self.__gyro_calib += val
            flag, val = self.__read_acceleration_data()
            if not flag:
                self.__gyro_calib = Vec3(0.0)
                self.__accel_calib = Vec3(0.0)
                print("calibration failed")
                break
            self.__accel_calib += val

        scl = 1.0 / n_measurement

        self.__gyro_calib *= scl

        self.__accel_calib *= scl

        print(f"{{\n"
              f"\"calibration_info\":\n"
              f"\t{{\n"
              f"\t\t\"n_measurements\":{n_measurement},\n"
              f"\t\t\"a_calib\"       :{self.__accel_calib},\n"
              f"\t\t\"o_calib\"       :{self.__gyro_calib}\n"
              f"\t}}\n"
              f"}}")

    def read_accel_measurements(self) -> bool:
        flag1, val = self.__read_acceleration_data()
        if flag1:
            self.__accelerations = val - self.acceleration_calibration
            self.__velocity_integrator(self.acceleration, time.perf_counter())
            self.__position_integrator(self.__velocity_integrator.curr_val, time.perf_counter())

        flag2, val = self.__read_gyro_data()
        if flag2:
            self.__angles_velocity = val - self.angles_velocity_calibration
            self.__angles_integrator(self.angles_velocity, time.perf_counter())
        return flag2 or flag1
