# from accelerometer_core.Utilities.real_time_filter import RealTimeFilter
# from accelerometer_core.Utilities import Matrix3, Quaternion
# from accelerometer_core.Utilities.vector3 import Vector3
# from accelerometer_core.accelerometer_constants import *
from Utilities.real_time_filter import RealTimeFilter
from Utilities.Geometry.vector3 import Vector3
from Utilities.Geometry import Quaternion
from Utilities.Geometry import Matrix3
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

    def __init__(self, address: int = 0x68):
        self._i2c_bus = None
        self._address: int = address  # mpu 6050
        if not self._init_bus():
            raise RuntimeError("Accelerometer bus init failed...")
        self._filters: List[List[RealTimeFilter]] = []
        self._acceleration_range: int = -1  # 2
        self._acceleration_range_raw: int = -1
        self._gyroscope_range: int = -1  # 250
        self._gyroscope_range_raw: int = -1
        self._hardware_filter_range_raw: int = -1
        self._use_filtering: bool = False
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
        # калибровочные значения
        self._accel_bias: float = 0.5  # допустимый уровень шума между значениями при калибровке
        self._calib_cntr: int = 0
        self._accel_calib: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._omega_calib: Vector3 = Vector3(0.0, 0.0, 0.0)
        # угол поворота
        self._angle_curr: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._angle_prev: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._basis_curr: Matrix3 = Matrix3.identity()
        self._basis_prev: Matrix3 = Matrix3.identity()
        self._k_accel: float = 0.999
        self._default_settings()

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
               f"\t\"acceleration_calib\":         {self.acceleration_calib},\n" \
               f"\t\"omega_calib\":                {self.omega_calib},\n" \
               f"\t\"k_accel\":                    {self.k_accel},\n" \
               f"\t\"acceleration_noize_level\":   {self.acceleration_noize_level},\n" \
               f"\t\"use_filtering\":              {'true' if self.use_filtering else 'false'},\n" \
               f"\t\"ax_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_AX])}\n\t],\n" \
               f"\t\"ay_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_AY])}\n\t],\n" \
               f"\t\"az_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_AZ])}\n\t],\n" \
               f"\t\"gx_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_GX])}\n\t],\n" \
               f"\t\"gy_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_GY])}\n\t],\n" \
               f"\t\"gz_filters\":[\n{separator.join(str(f) for f in self._filters[FILTER_GZ])}\n\t]\n" \
               f"}}"

    def __enter__(self):
        return self

    def _init_bus(self) -> bool:
        try:
            self._i2c_bus = smbus.SMBus(1)
            # or bus = smbus.SMBus(0) for older version boards
        except NameError as _ex:
            print(f"SM Bus init error!!!\n{_ex.args}")
            return False
        try:
            # Write to power management register
            self.bus.write_byte_data(self.address, MPU6050_PWR_MGMT_1, 1)
            # write to sample rate register
            self.bus.write_byte_data(self.address, MPU6050_SAMPLE_RATE_DIV, 7)
            # Write to Configuration register
            self.bus.write_byte_data(self.address, MPU6050_MPU_CONFIG, 0)
            # Write to Gyro configuration register
            self.bus.write_byte_data(self.address, MPU6050_GYRO_CONFIG, 24)
            # Write to interrupt enable register
            self.bus.write_byte_data(self.address, MPU6050_INT_ENABLE, 1)
        except AttributeError as ex_:
            print(f"Accelerometer init error {ex_.args}")
            return False
        return True

    def _default_settings(self) -> None:
        self._filters.clear()
        for _ in range(6):
            _filter = RealTimeFilter()
            _filter.k_arg = 0.1
            _filter.kalman_error = 0.9
            _filter.mode = 2
            self._filters.append([_filter])
        self.acceleration_range_raw = 2
        self.gyroscope_range_raw = 250

    def _filter_value(self, val: float, filter_id: int) -> float:
        for _filter in self._filters[filter_id]:
            val = _filter.filter(val)
        return val

    def _read_i2c_raw(self) -> Tuple[bool, int, int, int, int, int, int]:
        try:
            raw_data = self.bus.read_i2c_block_data(self.address, MPU6050_ACCEL_X_OUT_H, 14)
            gx, gy, gz, t, ax, ay, az = struct.unpack('>hhhhhhh', raw_data)
        except RuntimeError:
            return False, 0, 0, 0, 0, 0, 0
        return False, gx, gy, gz, ax, ay, az

    def _read_data_i2c(self) -> Tuple[bool, Vector3, Vector3]:
        try:
            raw_data = self.bus.read_i2c_block_data(self.address, MPU6050_ACCEL_X_OUT_H, 14)
            gx, gy, gz, t, ax, ay, az = \
                tuple(map(lambda a: a if a < 0x8000 else a - 65536, struct.unpack('>hhhhhhh', raw_data)))
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
    def bus(self):
        return self._i2c_bus

    @property
    def address(self) -> int:
        return self._address

    @address.setter
    def address(self, address: int) -> None:
        prev_address: int = self.address
        self._address = address
        if not self._init_bus():
            print("incorrect device address in HardwareAccelerometerSettings")
            self._address = prev_address
            self._init_bus()

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
    def acceleration_range_raw(self) -> int:
        """
        Диапазон измеряемых ускорений
        ACCEL_SCALE_MODIFIER_2G  = 16384.0
        ACCEL_SCALE_MODIFIER_4G  = 8192.0
        ACCEL_SCALE_MODIFIER_8G  = 4096.0
        ACCEL_SCALE_MODIFIER_16G = 2048.0
        """
        return self._acceleration_range_raw

    @acceleration_range_raw.setter
    def acceleration_range_raw(self, accel_range: int) -> None:
        """
        Диапазон измеряемых ускорений
        ACCEL_SCALE_MODIFIER_2G  = 16384.0
        ACCEL_SCALE_MODIFIER_4G  = 8192.0
        ACCEL_SCALE_MODIFIER_8G  = 4096.0
        ACCEL_SCALE_MODIFIER_16G = 2048.0
        """
        if accel_range not in Accelerometer._acc_ranges:
            return
        self._acceleration_range = accel_range
        self._acceleration_range_raw = Accelerometer._acc_ranges[self._acceleration_range]
        self.bus.write_byte_data(self.address, MPU6050_ACCEL_CONFIG, 0x00)
        self.bus.write_byte_data(self.address, MPU6050_ACCEL_CONFIG, self._acceleration_range_raw)

    @property
    def acceleration_range(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return self._acceleration_range * GRAVITY_CONSTANT

    @property
    def acceleration_scale(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return Accelerometer._acc_scales[self.acceleration_range_raw]

    @property
    def gyroscope_range_raw(self) -> int:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG  = 0x00
        GYRO_RANGE_500DEG  = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        return self._gyroscope_range_raw

    @gyroscope_range_raw.setter
    def gyroscope_range_raw(self, gyro_range: int) -> None:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG  = 0x00
        GYRO_RANGE_500DEG  = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        if gyro_range not in Accelerometer._gyro_ranges:
            return
        self._gyroscope_range = gyro_range
        self._gyroscope_range_raw = Accelerometer._gyro_ranges[self._gyroscope_range]
        self.bus.write_byte_data(self.address, MPU6050_GYRO_CONFIG, 0x00)
        self.bus.write_byte_data(self.address, MPU6050_GYRO_CONFIG, self._gyroscope_range_raw)

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
        ext_sync_set = self.bus.read_byte_data(self.address, MPU6050_MPU_CONFIG) & 0b00111000
        self.bus.write_byte_data(self.address, MPU6050_MPU_CONFIG, ext_sync_set | self._hardware_filter_range_raw)

    """
    ###############################################################
    #####  Local space acceleration, omega and angle getters  #####
    ###############################################################
    """

    @property
    def acceleration_noize_level(self) -> float:
        """
        Пороговый уровень отклонения значения модуля вектора G относительно которого определяется, движемся или нет.
        """
        return self._accel_bias

    @acceleration_noize_level.setter
    def acceleration_noize_level(self, value: float) -> None:
        """
        Пороговый уровень отклонения значения модуля вектора G относительно которого определяется, движемся или нет.
        """
        self._accel_bias = min(max(0.0, value), 10.0)

    @property
    def k_accel(self) -> float:
        """
        Параметр комплиментарного фильтра для определения углов поворота.
        """
        return self._k_accel

    @k_accel.setter
    def k_accel(self, value: float) -> None:
        """
        Параметр комплиментарного фильтра для определения углов поворота.
        """
        self._k_accel = min(max(0.0, value), 1.0)

    @property
    def omega(self) -> Vector3:
        """
        Угловые скорости.
        """
        return self._omega_curr

    @property
    def omega_prev(self) -> Vector3:
        """
        Предыдущие угловые скорости.
        """
        return self._omega_prev

    @property
    def angle(self) -> Vector3:
        """
        Углы поворота (Эйлера).
        """
        return self._angle_curr

    @property
    def angle_prev(self) -> Vector3:
        """
        Предыдущие углы поворота (Эйлера).
        """
        return self._angle_prev

    @property
    def quaternion(self) -> Quaternion:
        return Quaternion.from_euler_angles(self._angle_curr.x, self._angle_curr.y, self._angle_curr.z)

    @property
    def acceleration(self) -> Vector3:
        """
        Задана в системе координат акселерометра.
        """
        return self._accel_curr

    @property
    def acceleration_prev(self) -> Vector3:
        """
        Задана в системе координат акселерометра.
        """
        return self._accel_prev

    @property
    def acceleration_calib(self) -> Vector3:
        """
        Задана в мировой системе координат.
        """
        return self._accel_calib

    @property
    def omega_calib(self) -> Vector3:
        """
        Задана в системе координат акселерометра.
        """
        return self._omega_calib

    @acceleration_calib.setter
    def acceleration_calib(self, value: Vector3) -> None:
        """
        Задана в мировой системе координат.
        """
        self._accel_calib = value

    @omega_calib.setter
    def omega_calib(self, value: Vector3) -> None:
        """
        Задана в системе координат акселерометра.
        """
        self._omega_calib = value

    """
    #########################################################
    #####  Local space to world space transform values  #####
    #########################################################
    """

    @property
    def basis(self) -> Matrix3:
        """
        Собственная система координат акселерометра.
        """
        return self._basis_curr

    @property
    def basis_prev(self) -> Matrix3:
        """
        Предыдущая собственная система координат акселерометра.
        """
        return self._basis_prev

    @property
    def acceleration_world_space(self) -> Vector3:
        """
        Задана в мировой системе координат (ускорение без G)
        """
        return Vector3(self.basis.m00 * self.acceleration.x +
                       self.basis.m10 * self.acceleration.y +
                       self.basis.m20 * self.acceleration.z - self._accel_calib.x,
                       self.basis.m01 * self.acceleration.x +
                       self.basis.m11 * self.acceleration.y +
                       self.basis.m21 * self.acceleration.z - self._accel_calib.y,
                       self.basis.m02 * self.acceleration.x +
                       self.basis.m12 * self.acceleration.y +
                       self.basis.m22 * self.acceleration.z - self._accel_calib.z)

    @property
    def acceleration_local_space(self) -> Vector3:
        """
        Задана в системе координат акселерометра (ускорение без G)
        """
        return Vector3(self.acceleration.x - (self.basis.m00 * self._accel_calib.x +
                                              self.basis.m01 * self._accel_calib.y +
                                              self.basis.m02 * self._accel_calib.z),
                       self.acceleration.y - (self.basis.m10 * self._accel_calib.x +
                                              self.basis.m11 * self._accel_calib.y +
                                              self.basis.m12 * self._accel_calib.z),
                       self.acceleration.z - (self.basis.m20 * self._accel_calib.x +
                                              self.basis.m21 * self._accel_calib.y +
                                              self.basis.m22 * self._accel_calib.z))
    """
    #################################
    #####  Time values getters  #####
    #################################
    """

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

    """
    ##########################################
    #####  Main accelerometer functions  #####
    ##########################################
    """

    def reset(self, reset_ranges: bool = False) -> None:
        """
        Сброс параметров к начальным
        :param reset_ranges: сброс диапазонов измерения
        """
        for filter_list in self._filters:
            for f in filter_list:
                f.clean_up()
        self._accel_curr = Vector3(0.0, 0.0, 0.0)
        self._accel_prev = Vector3(0.0, 0.0, 0.0)
        self._omega_curr = Vector3(0.0, 0.0, 0.0)
        self._omega_prev = Vector3(0.0, 0.0, 0.0)
        self._basis_curr = Matrix3.identity()
        self._basis_prev = Matrix3.identity()
        self._t_start = time.perf_counter()
        self._t_curr = 0.0
        self._t_prev = 0.0
        # if reset_calib_info:
        self._accel_calib = Vector3(0.0, 0.0, 0.0)
        self._omega_calib = Vector3(0.0, 0.0, 0.0)
        if reset_ranges:
            self.acceleration_range_raw = 2
            self.gyroscope_range_raw = 250

    def calibrate(self, stop_calib: bool = False, forward: Vector3 = None) -> bool:
        """
        Читает и аккумулирует калибровочные значения для углов и ускорений.
        :param stop_calib: переход в режим завершения калибровки.
        :param forward: направление вперёд. М.б. использованы показания магнетометра.
        :return: успешно ли завершилась итерация калибровки
        """
        if (self.acceleration - self.acceleration_prev).magnitude() > self.acceleration_noize_level:
            stop_calib = True

        if stop_calib:
            if self._calib_cntr == 0:
                return False
            self._accel_calib /= self._calib_cntr
            self._omega_calib /= self._calib_cntr
            self._calib_cntr = 0
            self._basis_curr = Matrix3.build_basis(self._accel_calib, forward)
            self._basis_prev = self._basis_curr
            self._accel_calib = Vector3(self.basis.m00 * self._accel_calib.x +
                                        self.basis.m10 * self._accel_calib.y +
                                        self.basis.m20 * self._accel_calib.z,
                                        self.basis.m01 * self._accel_calib.x +
                                        self.basis.m11 * self._accel_calib.y +
                                        self.basis.m21 * self._accel_calib.z,
                                        self.basis.m02 * self._accel_calib.x +
                                        self.basis.m12 * self._accel_calib.y +
                                        self.basis.m22 * self._accel_calib.z)

            self._angle_curr = self.basis.to_euler_angles()
            self._angle_prev = self._angle_curr
            return False

        if not self.read_measurements():
            return False

        self._calib_cntr += 1
        self._accel_calib += self.acceleration
        self._omega_calib += self.omega
        return True

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
