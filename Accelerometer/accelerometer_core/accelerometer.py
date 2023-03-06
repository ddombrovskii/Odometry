from accelerometer_core.utilities.real_time_filter import RealTimeFilter
from accelerometer_core.utilities.vector3 import Vector3
from accelerometer_core.accelerometer_constants import *
from typing import List, Tuple
import numpy as np
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
        self.__registers = {ACCEL_X_OUT_H: lambda x: 0.3333 * GRAVITY_CONSTANT,  # BusDummy.accel_x(1.25 * x),
                            ACCEL_Y_OUT_H: lambda x: 0.3333 * GRAVITY_CONSTANT,
                            ACCEL_Z_OUT_H: lambda x: 0.3333 * GRAVITY_CONSTANT} # BusDummy.accel_z(1.25 * x)}
        self._t_start = time.perf_counter()

    def SMBus(self, a: int):
        return self

    def write_byte_data(self, a: int, b: int, c: int):
        pass

    def read_byte_data(self, a: int, register: int):
        if register in self.__registers:
            return self.__registers[register](time.perf_counter() - self._t_start)
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
    _filter_ranges = {256: FILTER_BW_256,
                      188: FILTER_BW_188,
                      98: FILTER_BW_98,
                      42: FILTER_BW_42,
                      20: FILTER_BW_20,
                      10: FILTER_BW_10,
                      5: FILTER_BW_5}
    """
    Диапазоны измеряемых ускорений
    """
    _acc_ranges = {2: ACCEL_RANGE_2G,
                   4: ACCEL_RANGE_4G,
                   8: ACCEL_RANGE_8G,
                   16: ACCEL_RANGE_16G}
    """
    Модификаторы масштаба для ускорений
    """
    _acc_scales = {ACCEL_RANGE_2G: ACCEL_SCALE_MODIFIER_2G,
                   ACCEL_RANGE_4G: ACCEL_SCALE_MODIFIER_4G,
                   ACCEL_RANGE_8G: ACCEL_SCALE_MODIFIER_8G,
                   ACCEL_RANGE_16G: ACCEL_SCALE_MODIFIER_16G}
    """
    Диапазоны измеряемых угловых скоростей
    """
    _gyro_ranges = {250: ACCEL_RANGE_2G,
                    500: ACCEL_RANGE_4G,
                    1000: ACCEL_RANGE_8G,
                    2000: ACCEL_RANGE_16G}
    """
    Модификаторы масштаба для угловых скоростей
    """
    _gyro_scales = {GYRO_RANGE_250DEG: GYRO_SCALE_MODIFIER_250DEG,
                    GYRO_RANGE_500DEG: GYRO_SCALE_MODIFIER_500DEG,
                    GYRO_RANGE_1000DEG: GYRO_SCALE_MODIFIER_1000DEG,
                    GYRO_RANGE_2000DEG: GYRO_SCALE_MODIFIER_2000DEG}

    def __init__(self, address: int = 0x68):
        self.__i2c_bus = None
        self.__address: int = address  # mpu 6050
        if not self.__init_bus():
            raise RuntimeError("Accelerometer bus init failed...")
        self._filters: List[List[RealTimeFilter]] = []
        self._acceleration_range: int = -1  # 2
        self._acceleration_range_raw: int = -1
        self._gyroscope_range: int = -1  # 250
        self._gyroscope_range_raw: int = -1
        self._hardware_filter_range_raw: int = -1
        self._use_filtering: bool = True
        # Время: текущее измеренное, предыдущее измеренное, время начала движения
        self._t_curr: float = 0.0
        self._t_prev: float = 0.0
        self._t_start: float = time.perf_counter()
        # текущее значение ускорения
        self._accel_curr: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._accel_prev: Vector3 = Vector3(0.0, 0.0, 0.0)
        # текущее значение угловой скорости
        self._omega_curr: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._omega_prev: Vector3 = Vector3(0.0, 0.0, 0.0)
        # значение ускорения в начальный момент времени
        # self._start_angles: Vector3 = Vector3(0.0, 0.0, 0.0)
        # значение углов в начальный момент времени
        # self._start_accel:        Vector3 = Vector3(0.0, 0.0, 0.0)
        # self._ang_velocity_calib: Vector3 = Vector3(0.0, 0.0, 0.0)
        # self._acceleration_calib: Vector3 = Vector3(0.0, 0.0, 0.0)
        self.__default_settings()

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
               f"\t\"ax_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_AX])}\n\t],\n" \
               f"\t\"ay_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_AY])}\n\t],\n" \
               f"\t\"az_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_AZ])}\n\t],\n" \
               f"\t\"gx_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_GX])}\n\t],\n" \
               f"\t\"gy_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_GY])}\n\t],\n" \
               f"\t\"gz_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_GZ])}\n\t]\n" \
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
        return True

    def __default_settings(self) -> None:
        self._filters.clear()
        for _ in range(6):
            _filter = RealTimeFilter()
            _filter.k_arg = 0.1
            _filter.kalman_error = 0.9
            _filter.mode = 2
            self._filters.append([_filter])
        self.acceleration_range_raw = 2
        self.gyroscope_range_raw = 250

    def __read_bus(self, addr: int) -> np.int16:
        if not _import_success:
            return self.bus.read_byte_data(self.address, addr)
        # Accelerometer and Gyro value are 16-bit
        high = self.bus.read_byte_data(self.address, addr)
        low = self.bus.read_byte_data(self.address, addr + 1)
        # concatenate higher and lower value
        value = (high << 8) | low
        # to get signed value from Accelerometer
        if value >= 0x8000:
            value -= 65536
        return value

    def __filter_value(self, val: float, filter_id: int) -> float:
        for _filter in self._filters[filter_id]:
            val = _filter.filter(val)
        return val

    def __read_acceleration_data(self) -> Tuple[bool, Vector3]:
        scl = 1.0 / self.acceleration_scale * GRAVITY_CONSTANT
        try:
            if self._use_filtering:
                return True, Vector3(self.__filter_value(float(self.__read_bus(ACCEL_X_OUT_H)) * scl, FILTER_AX),
                                     self.__filter_value(float(self.__read_bus(ACCEL_Y_OUT_H)) * scl, FILTER_AY),
                                     self.__filter_value(float(self.__read_bus(ACCEL_Z_OUT_H)) * scl, FILTER_AZ))
            return True, Vector3(float(self.__read_bus(ACCEL_X_OUT_H)) * scl,
                                 float(self.__read_bus(ACCEL_Y_OUT_H)) * scl,
                                 float(self.__read_bus(ACCEL_Z_OUT_H)) * scl)
        except Exception as _ex:
            print(f"acceleration data read error\n{_ex.args}")
            return False, Vector3(0.0, 0.0, 0.0)

    def __read_gyro_data(self) -> Tuple[bool, Vector3]:
        scl = 1.0 / self.gyroscope_scale / 180.0 * math.pi
        try:
            if self._use_filtering:
                return True, Vector3(self.__filter_value(float(self.__read_bus(GYRO_X_OUT_H)) * scl, FILTER_GX),
                                     self.__filter_value(float(self.__read_bus(GYRO_Y_OUT_H)) * scl, FILTER_GY),
                                     self.__filter_value(float(self.__read_bus(GYRO_Z_OUT_H)) * scl, FILTER_GZ))
            return True, Vector3(float(self.__read_bus(GYRO_X_OUT_H)) * scl,
                                 float(self.__read_bus(GYRO_Y_OUT_H)) * scl,
                                 float(self.__read_bus(GYRO_Z_OUT_H)) * scl)
        except Exception as _ex:
            print(f"gyroscope data read error\n{_ex.args}")
            return False, Vector3(0.0, 0.0, 0.0)

    # def __compute_start_params(self, compute_time: float = 10.0, forward: Vector3 = None, start_up_time: float = 5.0):
    #     self.reset()
    #     t = time.perf_counter()
    #     accel = Vector3()
    #     v_ang = Vector3()
    #     n_accel_read = 0
    #     n_angel_read = 0
    #     t_total = start_up_time + compute_time
    #     print(f'|----------------Accelerometer start up...--------------|\n'
    #           f'|-------------Please stand by and hold still...---------|')
    #     while time.perf_counter() - t < t_total:
    #         filler_l = int((time.perf_counter() - t) / t_total * 56)  # 56 - title chars count
    #         filler_r = 55 - filler_l
    #         sys.stdout.write(f'\r|{"":#>{str(filler_l)}}{"":.<{str(filler_r)}}|')
    #         sys.stdout.flush()
    #         if filler_r == 0:
    #             sys.stdout.write('\n\n')
    #         if time.perf_counter() - t < start_up_time:
    #             self.__read_acceleration_data()
    #             self.__read_gyro_data()
    #             continue
    #         flag, val = self.__read_acceleration_data()
    #         if flag:
    #             accel += val
    #             n_accel_read += 1
    #         flag, val = self.__read_gyro_data()
    #         if flag:
    #             v_ang += val
    #             n_angel_read += 1
    #     accel /= n_accel_read
    #     self._start_accel = accel
    #     self._acceleration = accel
    #     basis: Matrix3 = Matrix3.build_basis(accel, forward)
    #     self._start_angles       = basis.to_euler_angles()

    # def __compute_calib_params(self, compute_time: float = 10.0, forward: Vector3 = None, start_up_time: float = 5.0):
    #     self.reset()
    #     t = time.perf_counter()
    #     accel = Vector3()
    #     v_ang = Vector3()
    # 
    #     n_accel_read = 0
    #     n_angel_read = 0
    #     t_total = start_up_time + compute_time
    #     print(f'|---------------Accelerometer calibration...------------|\n'
    #           f'|-------------Please stand by and hold still...---------|')
    #     while time.perf_counter() - t < t_total:
    #         filler_l = int((time.perf_counter() - t) / t_total * 56)  # 56 - title chars count
    #         filler_r = 55 - filler_l
    #         sys.stdout.write(f'\r|{"":#>{str(filler_l)}}{"":.<{str(filler_r)}}|')
    #         sys.stdout.flush()
    #         if filler_r == 0:
    #             sys.stdout.write('\n\n')
    # 
    #         if time.perf_counter() - t < start_up_time:
    #             self.__read_acceleration_data()
    #             self.__read_gyro_data()
    #             continue
    # 
    #         flag, val = self.__read_acceleration_data()
    #         if flag:
    #             accel += val
    #             n_accel_read += 1
    #         flag, val = self.__read_gyro_data()
    #         if flag:
    #             v_ang += val
    #             n_angel_read += 1
    # 
    #     accel /= n_accel_read
    #     self._start_accel = accel
    #     self._acceleration = accel
    #     basis: Matrix3 = Matrix3.build_basis(accel, forward)
    #     self._start_angles       = basis.to_euler_angles()
    #     self._acceleration_calib = basis.transpose() * accel
    #     self._ang_velocity_calib = v_ang / n_angel_read

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
        return self._filters[FILTER_AX]

    @property
    def filters_ay(self) -> List[RealTimeFilter]:
        return self._filters[FILTER_AY]

    @property
    def filters_az(self) -> List[RealTimeFilter]:
        return self._filters[FILTER_AZ]

    @property
    def filters_gx(self) -> List[RealTimeFilter]:
        return self._filters[FILTER_GX]

    @property
    def filters_gy(self) -> List[RealTimeFilter]:
        return self._filters[FILTER_GY]

    @property
    def filters_gz(self) -> List[RealTimeFilter]:
        return self._filters[FILTER_GZ]

    @property
    def use_filtering(self) -> bool:
        return self._use_filtering

    @use_filtering.setter
    def use_filtering(self, val: bool) -> None:
        if self._use_filtering == val:
            return
        self._use_filtering = val
        if val:
            for channel_filters in self._filters:
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
        return self._acceleration_range_raw

    @acceleration_range_raw.setter
    def acceleration_range_raw(self, accel_range: int) -> None:
        """
        Диапазон измеряемых ускорений
        ACCEL_SCALE_MODIFIER_2G = 16384.0
        ACCEL_SCALE_MODIFIER_4G = 8192.0
        ACCEL_SCALE_MODIFIER_8G = 4096.0
        ACCEL_SCALE_MODIFIER_16G = 2048.0
        """
        if accel_range not in Accelerometer._acc_ranges:
            return
        self._acceleration_range = accel_range
        self._acceleration_range_raw = Accelerometer._acc_ranges[self._acceleration_range]
        self.bus.write_byte_data(self.address, ACCEL_CONFIG, 0x00)
        self.bus.write_byte_data(self.address, ACCEL_CONFIG, self._acceleration_range_raw)

    @property
    def acceleration_range(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2
        """
        return self._acceleration_range * GRAVITY_CONSTANT

    @property
    def acceleration_scale(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2
        """
        return Accelerometer._acc_scales[self.acceleration_range_raw]

    @property
    def gyroscope_range_raw(self) -> int:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG = 0x00
        GYRO_RANGE_500DEG = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        return self._gyroscope_range_raw

    @gyroscope_range_raw.setter
    def gyroscope_range_raw(self, gyro_range: int) -> None:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG = 0x00
        GYRO_RANGE_500DEG = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        if gyro_range not in Accelerometer._gyro_ranges:
            return
        self._gyroscope_range = gyro_range
        self._gyroscope_range_raw = Accelerometer._gyro_ranges[self._gyroscope_range]
        self.bus.write_byte_data(self.address, GYRO_CONFIG, 0x00)
        self.bus.write_byte_data(self.address, GYRO_CONFIG, self._gyroscope_range_raw)

    @property
    def gyroscope_range(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2
        """
        return float(self._gyroscope_range)

    @property
    def gyroscope_scale(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2
        """
        return Accelerometer._gyro_scales[self.gyroscope_range_raw]

    @property
    def hardware_filter_range_raw(self) -> int:
        """
        Документация???
        """
        return self._hardware_filter_range_raw

    @hardware_filter_range_raw.setter
    def hardware_filter_range_raw(self, filter_range: int) -> None:
        """
        Документация???
        """
        if filter_range not in Accelerometer._filter_ranges:
            return
        self._hardware_filter_range_raw = filter_range
        ext_sync_set = self.bus.read_byte_data(self.__address, MPU_CONFIG) & 0b00111000
        self.bus.write_byte_data(self.__address, MPU_CONFIG, ext_sync_set | self._hardware_filter_range_raw)

    # @property
    # def angles_velocity_calibration(self) -> Vector3:
    #     return self._ang_velocity_calib
    # 
    # @property
    # def acceleration_calibration(self) -> Vector3:
    #     """
    #     Задана в мировой системе координат
    #     """
    #     return self._acceleration_calib

    # @angles_velocity_calibration.setter
    # def angles_velocity_calibration(self, value: Vector3) -> None:
    #    self._ang_velocity_calib = value

    # @acceleration_calibration.setter
    # def acceleration_calibration(self, value: Vector3) -> None:
    #    """
    #    Задана в мировой системе координат
    #    """
    #    self._acceleration_calib = value

    @property
    def omega(self) -> Vector3:
        return self._omega_curr

    @property
    def omega_prev(self) -> Vector3:
        return self._omega_prev

    @property
    def acceleration(self) -> Vector3:
        """
        Задана в системе координат акселерометра
        """
        return self._accel_curr

    @property
    def acceleration_prev(self) -> Vector3:
        """
        Задана в системе координат акселерометра
        """
        return self._accel_prev

    # @property
    # def start_acceleration(self) -> Vector3:
    #    """
    #    Задана в системе координат акселерометра
    #    """
    #    return self._start_angles
    
    # @property
    # def start_ang_values(self) -> Vector3:
    #     return self._start_angles

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
        return self._t_curr

    @property
    def prev_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self._t_prev

    def reset(self, reset_ranges: bool = False) -> None:
        for filter_list in self._filters:
            for f in filter_list:
                f.clean_up()
        self._accel_curr = Vector3(0.0, 0.0, 0.0)
        self._accel_prev = Vector3(0.0, 0.0, 0.0)
        self._omega_curr = Vector3(0.0, 0.0, 0.0)
        self._omega_prev = Vector3(0.0, 0.0, 0.0)
        self._t_start    = time.perf_counter()
        self._t_curr     = 0.0
        self._t_prev     = 0.0
        if reset_ranges:
            self.acceleration_range_raw = 2
            self.gyroscope_range_raw = 250

    # def start_up(self, start_up_time: float = 1.5, forward: Vector3 = None) -> None:
    #     self.__compute_start_params(start_up_time, forward, 1.5)
    #     self._t_start = time.perf_counter()

    # def calibrate(self, calib_time: float = 10.0, forward: Vector3 = None) -> None:
    #    _use_filtering = self.use_filtering
    #    self.use_filtering = not _use_filtering
    #    self.__compute_calib_params(calib_time, forward)
    #    self._t_start = time.perf_counter()
    #    self.use_filtering = _use_filtering
    #    print(f"{{\n"
    #          f"\"calibration_info\":\n"
    #          f"\t{{\n"
    #          f"\t\t\"ang_start\"   :{self.start_ang_values / math.pi * 180},\n"
    #          f"\t\t\"accel_calib\" :{self._acceleration_calib},\n"
    #          f"\t\t\"ang_calib\"   :{self._ang_velocity_calib}\n"
    #          f"\t}}\n"
    #          f"}}")

    # def angles_fast(self) -> Tuple[float, float, float]:
    #     return utilities.pi + utilities.atan2(self.acceleration.z, self.acceleration.z), \
    #            utilities.pi + utilities.atan2(self.acceleration.y, self.acceleration.z), \
    #            utilities.pi + utilities.atan2(self.acceleration.y, self.acceleration.x)

    def read_accel_measurements(self) -> bool:
        """
        Пишет данные без учёта калибровочных параметров для G!!!
        """
        self._t_prev = self._t_curr
        self._t_curr = time.perf_counter() - self._t_start

        flag1, val = self.__read_acceleration_data()

        if flag1:
            self._accel_prev = self._accel_curr
            self._accel_curr = val

        flag2, val = self.__read_gyro_data()
        if flag2:
            self._omega_prev = self._omega_curr
            self._omega_curr = val

        return flag2 or flag1
