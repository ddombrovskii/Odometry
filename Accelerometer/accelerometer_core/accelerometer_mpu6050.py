from Utilities.real_time_filter import RealTimeFilter
from Utilities.Geometry.vector3 import Vector3
from Utilities.Geometry import Quaternion
from Utilities.Geometry import Matrix3
from .accelerometer_base import AccelerometerBase
from .accelerometer_constants import *
from typing import List, Tuple
import random
import struct
import math
import time

_import_success = False


class BusDummy:
    @staticmethod
    def accel_x(t: float, step: float = 10, width: float = .5) -> float:
        amp = 10.0
        val = math.exp(-(t - 20 - 1.0 * step) ** 2 / width ** 2) * amp + \
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
        self.__registers = {MPU6050_ACCEL_X_OUT_H: lambda x: 0.3333 * GRAVITY_CONSTANT,  # BusDummy.accel_x(1.25 * x),
                            MPU6050_ACCEL_Y_OUT_H: lambda x: 0.3333 * GRAVITY_CONSTANT,
                            MPU6050_ACCEL_Z_OUT_H: lambda x: 0.3333 * GRAVITY_CONSTANT}  # BusDummy.accel_z(1.25 * x)}
        self._t_start = time.perf_counter()

    def SMBus(self, a: int):
        return self

    def read_i2c_block_data(self, a, b, c):
        # TODO семь 2ух байтных чисел
        return b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

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
class Accelerometer(AccelerometerBase):
    """
        Акселерометр основанный на чипе mpu6050. Читает ускорения, угловые скорости, углы.
    """
    """
    Диапазоны измеряемых ускорений
    """
    _filter_ranges = {256: MPU6050_FILTER_BW_256,
                      188: MPU6050_FILTER_BW_188,
                      98:  MPU6050_FILTER_BW_98,
                      42:  MPU6050_FILTER_BW_42,
                      20:  MPU6050_FILTER_BW_20,
                      10:  MPU6050_FILTER_BW_10,
                      5:   MPU6050_FILTER_BW_5}
    """
    Диапазоны измеряемых ускорений
    """
    _acc_ranges = {2:  MPU6050_ACCEL_RANGE_2G,
                   4:  MPU6050_ACCEL_RANGE_4G,
                   8:  MPU6050_ACCEL_RANGE_8G,
                   16: MPU6050_ACCEL_RANGE_16G}
    """
    Модификаторы масштаба для ускорений
    """
    _acc_scales = {MPU6050_ACCEL_RANGE_2G:  MPU6050_ACCEL_SCALE_MODIFIER_2G,
                   MPU6050_ACCEL_RANGE_4G:  MPU6050_ACCEL_SCALE_MODIFIER_4G,
                   MPU6050_ACCEL_RANGE_8G:  MPU6050_ACCEL_SCALE_MODIFIER_8G,
                   MPU6050_ACCEL_RANGE_16G: MPU6050_ACCEL_SCALE_MODIFIER_16G}
    """
    Диапазоны измеряемых угловых скоростей
    """
    _gyro_ranges = {250:  MPU6050_ACCEL_RANGE_2G,
                    500:  MPU6050_ACCEL_RANGE_4G,
                    1000: MPU6050_ACCEL_RANGE_8G,
                    2000: MPU6050_ACCEL_RANGE_16G}
    """
    Модификаторы масштаба для угловых скоростей
    """
    _gyro_scales = {MPU6050_GYRO_RANGE_250DEG:  MPU6050_GYRO_SCALE_MODIFIER_250DEG,
                    MPU6050_GYRO_RANGE_500DEG:  MPU6050_GYRO_SCALE_MODIFIER_500DEG,
                    MPU6050_GYRO_RANGE_1000DEG: MPU6050_GYRO_SCALE_MODIFIER_1000DEG,
                    MPU6050_GYRO_RANGE_2000DEG: MPU6050_GYRO_SCALE_MODIFIER_2000DEG}

    def _request_for_device_connection(self) -> bool:
        try:
            self._device_connection = smbus.SMBus(1)
            # or bus = smbus.SMBus(0) for older version boards
        except NameError as _ex:
            print(f"SM Bus init error!!!\n{_ex.args}")
            return False
        try:
            # Write to power management register
            self.device.write_byte_data(self.address, MPU6050_PWR_MGMT_1, 1)
            # write to sample rate register
            self.device.write_byte_data(self.address, MPU6050_SAMPLE_RATE_DIV, 7)
            # Write to Configuration register
            self.device.write_byte_data(self.address, MPU6050_MPU_CONFIG, 0)
            # Write to Gyro configuration register
            self.device.write_byte_data(self.address, MPU6050_GYRO_CONFIG, 24)
            # Write to interrupt enable register
            self.device.write_byte_data(self.address, MPU6050_INT_ENABLE, 1)
        except AttributeError as ex_:
            print(f"Accelerometer init error {ex_.args}")
            return False
        return True

    def _request_for_device_disconnection(self) -> bool:
        return True

    def _device_read_request(self) -> Tuple[bool, Tuple[float, ...]]:
        # TODO сделать асинхронным, добавить ожидание результата со стороны BNO в течении какого-то, по истечении
        #  которого ничего не возвращать.
        try:
            raw_data = self.device.read_i2c_block_data(self.address, MPU6050_ACCEL_X_OUT_H, 14)
            gx, gy, gz, t, ax, ay, az = \
                tuple(map(lambda a: a if a < 0x8000 else a - 65536, struct.unpack('>7h', raw_data)))
        except RuntimeError:
            return False, Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)

        g_scl = 1.0 / self.acceleration_scale * GRAVITY_CONSTANT
        a_scl = 1.0 / self.gyroscope_scale / 180.0 * math.pi


    def __init__(self, address: int = 0x68):
        self._address: int = address  # mpu 6050
        self._i2c_bus = None
        super().__init__()
        self._filters: List[List[RealTimeFilter]] = []
        self._use_filtering: bool = False

    #  def __str__(self):
    #      separator = ",\n"
    #      return f"{{\n" \
    #             f"\t\"address\":                    {self.address},\n" \
    #             f"\t\"acceleration_range_raw\":     {self.acceleration_range_raw},\n" \
    #             f"\t\"acceleration_range\":         {self.acceleration_range},\n" \
    #             f"\t\"acceleration_scale\":         {self.acceleration_scale},\n" \
    #             f"\t\"gyroscope_range_raw\":        {self.gyroscope_range_raw},\n" \
    #             f"\t\"gyroscope_range\":            {self.gyroscope_range},\n" \
    #             f"\t\"gyroscope_scale\":            {self.gyroscope_scale},\n" \
    #             f"\t\"hardware_filter_range_raw\":  {self.hardware_filter_range_raw},\n" \
    #             f"\t\"acceleration_calib\":         {self.acceleration_calib},\n" \
    #             f"\t\"omega_calib\":                {self.omega_calib},\n" \
    #             f"\t\"k_accel\":                    {self.k_accel},\n" \
    #             f"\t\"acceleration_noize_level\":   {self.acceleration_noize_level},\n" \
    #             f"\t\"use_filtering\":              {'true' if self.use_filtering else 'false'},\n" \
    #             f"\t\"ax_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_AX])}\n\t],\n" \
    #             f"\t\"ay_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_AY])}\n\t],\n" \
    #             f"\t\"az_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_AZ])}\n\t],\n" \
    #             f"\t\"gx_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_GX])}\n\t],\n" \
    #             f"\t\"gy_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_GY])}\n\t],\n" \
    #             f"\t\"gz_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_GZ])}\n\t]\n" \
    #             f"}}"

    def __enter__(self):
        return self

    def _default_settings(self) -> None:
        super(Accelerometer, self)._default_settings()
        self._filters.clear()
        for _ in range(6):
            _filter = RealTimeFilter()
            _filter.k_arg = 0.1
            _filter.kalman_error = 0.9
            _filter.mode = 2
            self._filters.append([_filter])

    def _filter_value(self, val: float, filter_id: int) -> float:
        for _filter in self._filters[filter_id]:
            val = _filter.filter(val)
        return val

    def _read_i2c_raw(self) -> Tuple[bool, int, int, int, int, int, int]:
        try:
            raw_data = self.device.read_i2c_block_data(self.address, MPU6050_ACCEL_X_OUT_H, 14)
            gx, gy, gz, t, ax, ay, az = struct.unpack('>7h', raw_data)
        except RuntimeError:
            return False, 0, 0, 0, 0, 0, 0
        return False, gx, gy, gz, ax, ay, az

    def _read_data_i2c(self) -> Tuple[bool, Vector3, Vector3]:
        try:
            raw_data = self.device.read_i2c_block_data(self.address, MPU6050_ACCEL_X_OUT_H, 14)
            gx, gy, gz, t, ax, ay, az = \
                tuple(map(lambda a: a if a < 0x8000 else a - 65536, struct.unpack('>7h', raw_data)))
        except RuntimeError:
            return False, Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)

        g_scl = 1.0 / self.acceleration_scale * GRAVITY_CONSTANT
        a_scl = 1.0 / self.gyroscope_scale / 180.0 * math.pi

        if not self._use_filtering:
            return True, \
                   Vector3(float(ax) * a_scl, float(ay) * a_scl, float(az) * a_scl), \
                   Vector3(float(gx) * g_scl, float(gy) * g_scl, float(gz) * g_scl)

        return True, \
               Vector3(self._filter_value(float(ax) * a_scl, FILTER_AX),
                       self._filter_value(float(ay) * a_scl, FILTER_AY),
                       self._filter_value(float(az) * a_scl, FILTER_AZ)), \
               Vector3(self._filter_value(float(gx) * g_scl, FILTER_GX),
                       self._filter_value(float(gy) * g_scl, FILTER_GY),
                       self._filter_value(float(gz) * g_scl, FILTER_GZ))

    """
    ###############################################
    #####  I2C parameters setter and getters  #####
    ###############################################
    """
    @property
    def address(self) -> int:
        return self._address

    @address.setter
    def address(self, address: int) -> None:
        prev_address: int = self.address
        self._address = address
        if not self._request_for_device_disconnection():
            print("incorrect device address in HardwareAccelerometerSettings")
            self._address = prev_address
            self._request_for_device_disconnection()

    """
    #####################################################
    ##### Programmable filters setters and getters  #####
    #####################################################
    """

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

    """
    ###################################################
    #####  MPU6050 parameters setter and getters  #####
    ###################################################
    """

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
    def acceleration_range_key(self) -> int:
        """
        Диапазон измеряемых ускорений
        ACCEL_SCALE_MODIFIER_2G  = 16384.0
        ACCEL_SCALE_MODIFIER_4G  = 8192.0
        ACCEL_SCALE_MODIFIER_8G  = 4096.0
        ACCEL_SCALE_MODIFIER_16G = 2048.0
        """
        return self._accel_range_key

    @acceleration_range_key.setter
    def acceleration_range_key(self, accel_range: int) -> None:
        """
        Диапазон измеряемых ускорений
        ACCEL_SCALE_MODIFIER_2G  = 16384.0
        ACCEL_SCALE_MODIFIER_4G  = 8192.0
        ACCEL_SCALE_MODIFIER_8G  = 4096.0
        ACCEL_SCALE_MODIFIER_16G = 2048.0
        """
        if accel_range not in Accelerometer._acc_ranges:
            return
        self._accel_range_key = accel_range
        self._accel_range_val = Accelerometer._acc_ranges[self._accel_range_key]
        self.device.write_byte_data(self.address, MPU6050_ACCEL_CONFIG, 0x00)
        self.device.write_byte_data(self.address, MPU6050_ACCEL_CONFIG, self._accel_range_val)

    @property
    def acceleration_scale(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return Accelerometer._acc_scales[self._accel_range_val]

    @property
    def gyroscope_range_val(self) -> int:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG  = 0x00
        GYRO_RANGE_500DEG  = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        return self._gyro_range_val

    @gyroscope_range_val.setter
    def gyroscope_range_val(self, gyro_range: int) -> None:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG  = 0x00
        GYRO_RANGE_500DEG  = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        if gyro_range not in Accelerometer._gyro_ranges:
            return
        self._gyro_range_key = gyro_range
        self._gyro_range_val = Accelerometer._gyro_ranges[self._gyro_range_key]
        self.device.write_byte_data(self.address, MPU6050_GYRO_CONFIG, 0x00)
        self.device.write_byte_data(self.address, MPU6050_GYRO_CONFIG, self._gyro_range_val)

    @property
    def gyroscope_range(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return float(self._gyroscope_range)

    @property
    def gyroscope_scale(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return Accelerometer._gyro_scales[self.gyroscope_range_raw]

    """
    ###############################################################
    #####  Local space acceleration, omega and angle getters  #####
    ###############################################################
    """
    @property
    def quaternion(self) -> Quaternion:
        return Quaternion.from_euler_angles(self._angle_curr.x, self._angle_curr.y, self._angle_curr.z)

    def read_measurements(self) -> bool:
        """
        Пишет данные без учёта калибровочных параметров для G!!!
        """
        self._t_prev = self._t_curr
        self._t_curr = time.perf_counter() - self._t_start

        flag, accel, gyro = self._read_data_i2c()

        if flag:
            self._accel_prev = self._accel_curr
            self._accel_curr = accel
            self._omega_prev = self._omega_curr
            self._omega_curr = gyro - self._omega_calib

        u: Vector3 = (self.basis.up + Vector3.cross(self.omega, self.basis.up) * self.delta_t).normalized()
        u = (u * (1.0 - self.k_accel) + self.k_accel * self.acceleration.normalized()).normalized()
        # u: Vector3 = ((self.basis.up * Vector3.dot(self.basis.up, self.acceleration) +
        #                Vector3.cross(self.omega, self.basis.up) * self.delta_t) * self._k_accel +
        #               self.acceleration * (1.0 - self._k_accel))

        f: Vector3 = (self.basis.front + Vector3.cross(self.omega, self.basis.front) * self.delta_t)
        r = Vector3.cross(f, u)
        f = Vector3.cross(u, r)
        # f = f.normalized()
        # u = u.normalized()
        # r = r.normalized()
        self._basis_prev = self._basis_curr
        self._basis_curr = Matrix3.build_transform(r, u, f)
        self._angle_prev = self._angle_curr
        self._angle_curr = self.basis.to_euler_angles()
        return flag  # flag2 or flag1
