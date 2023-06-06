from Accelerometer.accelerometer_core import GRAVITY_CONSTANT
from Utilities.Geometry import Vector3, Quaternion, Matrix3
from typing import Tuple, List, Dict
from Utilities import RealTimeFilter
import time

ACCELERATION_BIT = 0
OMEGA_BIT = 1
ANGLES_BIT = 2
QUATERNION_BIT = 3
MAGNETOMETER_BIT = 4
ACCELERATION_LINEAR_BIT = 5
CALIBRATION_BIT = 6
STATUS_BIT = 7


TIME = "\"time\""
DTIME = "\"dtime\""
ACCELERATION = "\"acceleration\""
QUATERNION = "\"quaternion\""
ACCELERATION_LIN = "\"acceleration_linear\""
VELOCITY = "\"velocity\""
POSITION = "\"position\""
ANGLES_VELOCITY = "\"angles_velocity\""
ANGLES = "\"angles\""
MAGNETOMETER = "\"magnetometer\""
DEVICE_NAME = "\"device_name\""
LOG_TIME_START = "\"log_time_start\""
WAY_POINTS = "\"way_points\""


def _device_progres_bar(val: float, label: str = "", max_chars: int = 55,
                       char_progress: str = '#', char_stand_by: str = '.') -> str:
    filler_l = int(min(max(0.0, val), 1.0) * max_chars)  # max_chars - title chars count
    filler_r = max_chars - filler_l
    if len(label) == 0:
        return f'\r|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|' if filler_r != 0 else \
            f'\r|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|\n'

    return f'\r|{label:15}|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|' if filler_r != 0 else \
        f'\r|{label:15}|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|\n'


def _is_bit_set(bytes_: int, bit_: int) -> bool:
    return (bytes_ & (1 << bit_)) != 0


def _set_bit(bytes_: int, bit_: int) -> int:
    bytes_ |= (1 << bit_)
    return bytes_


def _clear_bit(bytes_: int, bit_: int) -> int:
    bytes_ &= ~(1 << bit_)
    return bytes_


def smooth_step(value, edge0, edge1) -> float:
    x = min(max(0.0, (value - edge0) / (edge1 - edge0)), 1.0)
    return x * x * (3.0 - 2.0 * x)


class AccelerometerBase:
    RAED_SETTINGS_BITS = {
            ACCELERATION_BIT,
            OMEGA_BIT,
            ANGLES_BIT,
            QUATERNION_BIT,
            MAGNETOMETER_BIT,
            ACCELERATION_LINEAR_BIT}

    def _request_for_device_connection(self) -> bool:
        return False

    def _request_for_device_disconnection(self) -> bool:
        return False

    def _device_read_request(self) -> Tuple[bool, Tuple[float, ...]]:
        return False, (0.0, )

    def __init__(self):
        self._device_connection = None
        if not self._request_for_device_connection():
            raise RuntimeError("AccelerometerBase:: unable to establish device connection...")

        self._wait_response = False

        self._use_filter = False
        self._accel_range_key: int = -1  # 2
        self._accel_range_val: int = -1

        self._gyro_range_val: int = -1  # 250
        self._gyro_range_key: int = -1

        self._mag_range_val: int = -1  # 250
        self._mag_range_key: int = -1

        self._filter_range_val: int = -1
        self._filter_range_key: int = -1

        self._accel_curr: Vector3 = Vector3(0, 0, 0)
        self._accel_prev: Vector3 = Vector3(0, 0, 0)

        self._accel_lin_curr: Vector3 = Vector3(0, 0, 0)
        self._accel_lin_prev: Vector3 = Vector3(0, 0, 0)

        self._omega_curr: Vector3 = Vector3(0, 0, 0)
        self._omega_prev: Vector3 = Vector3(0, 0, 0)

        self._mag_curr: Vector3 = Vector3(0, 0, 0)
        self._mag_prev: Vector3 = Vector3(0, 0, 0)

        self._angle_curr: Vector3 = Vector3(0, 0, 0)
        self._angle_prev: Vector3 = Vector3(0, 0, 0)

        self._quat_curr: Quaternion = Quaternion(1.0, 0, 0, 0)
        self._quat_prev: Quaternion = Quaternion(1.0, 0, 0, 0)

        self._basis_curr: Matrix3 = Matrix3.identity()
        self._basis_prev: Matrix3 = Matrix3.identity()

        self._k_accel: float = 0.999
        self._accel_threshold: float = 0.05  # допустимый уровень шума между значениями при калибровке

        self._curr_t: float = -1.0
        self._prev_t: float = -1.0
        self._start_t: float = time.perf_counter()

        self._status: int = 0
        self._read_config: int = 0
        self._calib_cntr: int = 0

        self._filters: Dict[int, List[RealTimeFilter()]] = {}

        self._accel_calib: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._accel_calib_lin: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._omega_calib: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._mag_calib: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._accel_gain = Vector3(0.05, 0.05, 0.05)
        self._default_settings()

    def _default_settings(self):
        self.is_accel_read = True
        self.is_omega_read = True
        self.is_angles_read = True
        # self.is_magnetometer_read = True
        # self.is_quaternion_read = True

    def _set_up_filters(self):
        self._filters.clear()
        for bit in [ACCELERATION_BIT, OMEGA_BIT, ANGLES_BIT, QUATERNION_BIT, MAGNETOMETER_BIT, ACCELERATION_LINEAR_BIT]:
            if _is_bit_set(self._read_config, bit):
                if bit != ANGLES_BIT:
                    ax = RealTimeFilter()
                    ax.mode = 0
                    ay = RealTimeFilter()
                    ay.mode = 0
                    az = RealTimeFilter()
                    az.mode = 0
                else:
                    ax = RealTimeFilter()
                    ax.mode = 0
                    ay = RealTimeFilter()
                    ay.mode = 0
                    az = RealTimeFilter()
                    az.mode = 0
                self._filters.update({bit: [ax, ay, az]})

    def _filter_values(self):
        if _is_bit_set(self._read_config, ACCELERATION_BIT):
            fx, fy, fz = self._filters[ACCELERATION_BIT]
            x, y, z = self._accel_curr
            self._accel_curr = Vector3(fx.filter(x), fy.filter(y), fz.filter(z))

        if _is_bit_set(self._read_config, OMEGA_BIT):
            fx, fy, fz = self._filters[OMEGA_BIT]
            x, y, z = self._omega_curr
            self._omega_curr = Vector3(fx.filter(x), fy.filter(y), fz.filter(z))

        if _is_bit_set(self._read_config, ANGLES_BIT):
            fx, fy, fz = self._filters[ANGLES_BIT]
            x, y, z = self._angle_curr
            self._angle_curr = Vector3(fx.filter(x), fy.filter(y), fz.filter(z))

        if _is_bit_set(self._read_config, MAGNETOMETER_BIT):
            fx, fy, fz = self._filters[MAGNETOMETER_BIT]
            x, y, z = self._mag_curr
            self._mag_curr = Vector3(fx.filter(x), fy.filter(y), fz.filter(z))

        if _is_bit_set(self._read_config, ACCELERATION_LINEAR_BIT):
            fx, fy, fz = self._filters[ACCELERATION_LINEAR_BIT]
            x, y, z = self._accel_lin_curr
            self._accel_lin_curr = Vector3(fx.filter(x), fy.filter(y), fz.filter(z))

    def __str__(self):

        data = [f"\t{DTIME:22}: {str(self.delta_t)}"]

        if _is_bit_set(self._read_config, ACCELERATION_BIT):
            data.append(f"\t{ACCELERATION:22}: {str(self.acceleration)}")

        if _is_bit_set(self._read_config, OMEGA_BIT):
            data.append(f"\t{ANGLES_VELOCITY:22}: {str(self.omega)}")

        if _is_bit_set(self._read_config, ANGLES_BIT):
            data.append(f"\t{ANGLES:22}: {str(self.angles)}")

        if _is_bit_set(self._read_config, QUATERNION_BIT):
            data.append(f"\t{QUATERNION:22}: {str(self.quaternion)}")

        if _is_bit_set(self._read_config, MAGNETOMETER_BIT):
            data.append(f"\t{MAGNETOMETER:22}: {str(self.magnetometer)}")

        if _is_bit_set(self._read_config, ACCELERATION_LINEAR_BIT):
            data.append(f"\t{ACCELERATION_LIN:22}: {str(self.acceleration_linear)}")

        sep = ',\n'

        return f" {{\n{sep.join(val for val in data)}\n }}"

    def __del__(self):
        if not self._request_for_device_disconnection():
            raise RuntimeError("AccelerometerBase:: error occurs during device disconnection...")

    @property
    def use_filtering(self):
        return self._use_filter

    @use_filtering.setter
    def use_filtering(self, val: bool):
        if val:
            self._use_filter = True
            self._set_up_filters()
        else:
            self._use_filter = False

    @property
    def device(self):
        return self._device_connection
    """
    ###############################################
    #####  Acceleration measurement settings  #####
    ###############################################
    """
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
        ...

    @property
    def acceleration_range(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return self._accel_range_val * GRAVITY_CONSTANT

    @property
    def acceleration_scale(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return 1.0
    """
    ###############################################
    #####    Gyroscope measurement settings   #####
    ###############################################
    """
    @property
    def gyroscope_range_key(self) -> int:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG  = 0x00
        GYRO_RANGE_500DEG  = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        return self._gyro_range_key

    @gyroscope_range_key.setter
    def gyroscope_range_key(self, gyro_range: int) -> None:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG  = 0x00
        GYRO_RANGE_500DEG  = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        ...

    @property
    def gyroscope_range(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return float(self._gyro_range_val)

    @property
    def gyroscope_scale(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return self.gyroscope_range

    """
    ###############################################
    #####  Magnetometer measurement settings  #####
    ###############################################
    """
    @property
    def magnetometer_range_key(self) -> int:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG  = 0x00
        GYRO_RANGE_500DEG  = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        return self._mag_range_key

    @magnetometer_range_key.setter
    def magnetometer_range_key(self, gyro_range: int) -> None:
        """
        Диапазон измеряемых значений угловых скоростей гироскопа
        GYRO_RANGE_250DEG  = 0x00
        GYRO_RANGE_500DEG  = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        ...

    @property
    def magnetometer_range(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return float(self._mag_range_val)

    @property
    def magnetometer_scale(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2.
        """
        return self.gyroscope_range
    """
    ######################################################
    #####  Accelerometer measurements read settings  #####
    ######################################################
    """
    @property
    def read_config(self) -> int:
        return self._read_config

    @property
    def is_accel_read(self) -> bool:
        return _is_bit_set(self.read_config, ACCELERATION_BIT)

    @property
    def is_lin_accel_read(self) -> bool:
        return _is_bit_set(self.read_config, ACCELERATION_LINEAR_BIT)

    @property
    def is_omega_read(self) -> bool:
        return _is_bit_set(self.read_config, OMEGA_BIT)

    @property
    def is_angles_read(self) -> bool:
        return _is_bit_set(self.read_config, ANGLES_BIT)

    @property
    def is_quaternion_read(self) -> bool:
        return _is_bit_set(self.read_config, QUATERNION_BIT)

    @property
    def is_magnetometer_read(self) -> bool:
        return _is_bit_set(self.read_config, MAGNETOMETER_BIT)

    @is_accel_read.setter
    def is_accel_read(self, val: bool) -> None:
        self._read_config = _set_bit(self.read_config, ACCELERATION_BIT) if val else \
            _clear_bit(self.read_config, ACCELERATION_BIT)

    @is_lin_accel_read.setter
    def is_lin_accel_read(self, val: bool) -> None:
        self._read_config = _set_bit(self.read_config, ACCELERATION_LINEAR_BIT) if val else \
            _clear_bit(self.read_config, ACCELERATION_LINEAR_BIT)

    @is_omega_read.setter
    def is_omega_read(self, val: bool) -> None:
        self._read_config = _set_bit(self.read_config, OMEGA_BIT) if val else \
            _clear_bit(self.read_config, OMEGA_BIT)

    @is_angles_read.setter
    def is_angles_read(self, val: bool) -> None:
        self._read_config = _set_bit(self.read_config, ANGLES_BIT) if val else \
            _clear_bit(self.read_config, ANGLES_BIT)

    @is_quaternion_read.setter
    def is_quaternion_read(self, val: bool) -> None:
        self._read_config = _set_bit(self.read_config, QUATERNION_BIT) if val else \
            _clear_bit(self.read_config, QUATERNION_BIT)

    @is_magnetometer_read.setter
    def is_magnetometer_read(self, val: bool) -> None:
        self._read_config = _set_bit(self.read_config, MAGNETOMETER_BIT) if val else \
            _clear_bit(self.read_config, MAGNETOMETER_BIT)

    @property
    def config_info(self) -> str:
        config = []
        if _is_bit_set(self.read_config, ACCELERATION_BIT):
            config.append('\t\"Accelerations\": true')
        else:
            config.append('\t\"Accelerations\": false')

        if _is_bit_set(self.read_config, OMEGA_BIT):
            config.append('\t\"Omegas\": true')
        else:
            config.append('\t\"Omegas\": false')

        if _is_bit_set(self.read_config, ANGLES_BIT):
            config.append('\t\"Angles\": true')
        else:
            config.append('\t\"Angles\": false')

        if _is_bit_set(self.read_config, QUATERNION_BIT):
            config.append('\t\"Quaternion\": true')
        else:
            config.append('\t\"Quaternion\": false')

        if _is_bit_set(self.read_config, MAGNETOMETER_BIT):
            config.append('\t\"Magnetometer\": true')
        else:
            config.append('\t\"Magnetometer\": false')

        if _is_bit_set(self.read_config, ACCELERATION_LINEAR_BIT):
            config.append('\t\"LinearAccelerations\": true')
        else:
            config.append('\t\"LinearAccelerations\": false')
        sep = ',\n'
        return f" {{\n{sep.join(val for val in config)}\n }}"

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
        self._accel_curr = Vector3(0.0, 0.0, 0.0)
        self._accel_prev = Vector3(0.0, 0.0, 0.0)
        self._omega_curr = Vector3(0.0, 0.0, 0.0)
        self._omega_prev = Vector3(0.0, 0.0, 0.0)
        self._basis_curr = Matrix3.identity()
        self._basis_prev = Matrix3.identity()
        self._start_t = time.perf_counter()
        self._curr_t = 0.0
        self._prev_t = 0.0
        # if reset_calib_info:
        self._accel_calib = Vector3(0.0, 0.0, 0.0)
        self._omega_calib = Vector3(0.0, 0.0, 0.0)
        self._mag_calib = Vector3(0.0, 0.0, 0.0)
        self._wait_response = False
        if reset_ranges:
            self.acceleration_range_key = 2
            self.gyroscope_range_key = 250

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
        return self._curr_t

    @property
    def prev_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self._prev_t
    """
    ############################################
    #####  Accelerometer filtering params  #####
    ############################################
    """
    @property
    def acceleration_noize_level(self) -> float:
        """
        Пороговый уровень отклонения значения модуля вектора G относительно которого определяется, движемся или нет.
        """
        return self._accel_threshold

    @acceleration_noize_level.setter
    def acceleration_noize_level(self, value: float) -> None:
        """
        Пороговый уровень отклонения значения модуля вектора G относительно которого определяется, движемся или нет.
        """
        self._accel_threshold = min(max(0.0, value), 10.0)

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
    """
    ########################################
    #####  Accelerometer calib params  #####
    ########################################
    """
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
        self._mag_calib = value

    @property
    def magnetometer_calib(self) -> Vector3:
        """
        Задана в системе координат акселерометра.
        """
        return self._mag_calib

    @magnetometer_calib.setter
    def magnetometer_calib(self, value: Vector3) -> None:
        """
        Задана в мировой системе координат.
        """
        self._mag_calib = value

    """
    ########################################
    #####  Accelerometer measurements  #####
    ########################################
    """
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
    def angles(self) -> Vector3:
        """
        Углы поворота (Эйлера).
        """
        return self._angle_curr

    @property
    def angles_prev(self) -> Vector3:
        """
        Предыдущие углы поворота (Эйлера).
        """
        return self._angle_prev

    @property
    def quaternion(self) -> Quaternion:
        return self._quat_curr

    @property
    def acceleration(self) -> Vector3:
        """
        Ускорение. Задано в системе координат акселерометра.
        """
        return self._accel_curr

    @property
    def acceleration_prev(self) -> Vector3:
        """
        Ускорение. Задано в системе координат акселерометра.
        """
        return self._accel_prev

    @property
    def acceleration_linear(self) -> Vector3:
        return self._accel_lin_curr

    @property
    def acceleration_linear_prev(self) -> Vector3:
        return self._accel_lin_prev

    @property
    def magnetometer(self) -> Vector3:
        return self._mag_curr

    @property
    def magnetometer_prev(self) -> Vector3:
        return self._mag_prev
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
        x, y, z = self.acceleration - self.basis * Vector3(0, 0, GRAVITY_CONSTANT)
        accel = Vector3(self.basis.m00 * x + self.basis.m10 * y + self.basis.m20 * z,
                        self.basis.m01 * x + self.basis.m11 * y + self.basis.m21 * z,
                        self.basis.m02 * x + self.basis.m12 * y + self.basis.m22 * z)
        return Vector3(*(v * smooth_step(abs(v), g, 2.0 * g) for v, g in zip(accel, self._accel_gain)))

    @property
    def acceleration_local_space(self) -> Vector3:
        """
        Задана в системе координат акселерометра (ускорение без G)
        """
        accel = self.acceleration - self.basis * Vector3(0, 0, GRAVITY_CONSTANT)
        return Vector3(*(v * smooth_step(abs(v), g, 2.0 * g) for v, g in zip(accel, self._accel_gain)))

    def _set_accel(self, x: float, y: float, z: float):
        self._accel_prev = self._accel_curr
        self._accel_curr = Vector3(x, y, z)

    def _set_lin_accel(self, x: float, y: float, z: float):
        self._accel_lin_prev = self._accel_lin_curr
        self._accel_lin_curr = Vector3(x, y, z) - self._accel_calib_lin

    def _set_omega(self, x: float, y: float, z: float):
        self._omega_prev = self._omega_curr
        self._omega_curr = Vector3(x, y, z) - self._omega_calib

    def _set_angles(self, x: float, y: float, z: float):
        self._angle_prev = self._angle_curr
        self._angle_curr = Vector3(x, y, z)

    def _set_magnetometer(self, x: float, y: float, z: float):
        self._mag_prev = self._mag_curr
        self._mag_curr = Vector3(x, y, z)

    def _set_quaternion(self, w: float, x: float, y: float, z: float):
        self._quat_prev = self._quat_curr
        self._quat_curr = Quaternion(w, x, y, z)

    def _set_basis(self, basis: Matrix3):
        self._basis_prev = self._basis_curr
        self._basis_curr = basis

    def _parce_response(self, response: Tuple[float, ...]) -> None:
        stride = 0

        if len(response) < 3:
            print('EMPTY PACKAGE')
            return

        if _is_bit_set(self.read_config, ACCELERATION_BIT):
            self._set_accel(response[stride], response[stride + 1], response[stride + 2])
            stride += 3

        if stride >= len(response):
            return

        if _is_bit_set(self.read_config, OMEGA_BIT):
            self._set_omega(response[stride], response[stride + 1], response[stride + 2])
            stride += 3
        if stride >= len(response):
            return

        if _is_bit_set(self.read_config, ANGLES_BIT):
            self._set_angles(response[stride], response[stride + 1], response[stride + 2])
            stride += 3
        if stride >= len(response):
            return

        if _is_bit_set(self.read_config, QUATERNION_BIT):
            self._set_quaternion(response[stride], response[stride + 1], response[stride + 2], response[stride + 3])
            stride += 4
        if stride >= len(response):
            return

        if _is_bit_set(self.read_config, MAGNETOMETER_BIT):
            self._set_magnetometer(response[stride], response[stride + 1], response[stride + 2])
            stride += 3
        if stride >= len(response):
            return

        if _is_bit_set(self.read_config, ACCELERATION_LINEAR_BIT):
            self._set_lin_accel(response[stride], response[stride + 1], response[stride + 2])
            stride += 3
        if stride >= len(response):
            return

    def _update_time(self) -> None:
        if self._curr_t < 0:
            self._curr_t = time.perf_counter()
            self._prev_t = time.perf_counter()
        else:
            self._prev_t = self._curr_t
            self._curr_t = time.perf_counter()

    def build_basis(self, azimuth: Vector3 = None):
        cntr = 0
        cntr_fail = 0
        while True:
            cntr_fail += 1
            if self.read_request():
                cntr += 1
            if cntr_fail == 1000:
                break
            if cntr == 10:
                break
        try:
            x_axis = Vector3.cross(self.acceleration, Vector3(0, 1, 0) if azimuth is None else azimuth).normalized()
            y_axis = Vector3.cross(x_axis, self.acceleration).normalized()
            z_axis = Vector3.cross(y_axis, x_axis)
            self._set_basis(Matrix3(x_axis.x, y_axis.x, z_axis.x,
                                    x_axis.y, y_axis.y, z_axis.y,
                                    x_axis.z, y_axis.z, z_axis.z))
            angles = Matrix3.to_euler_angles(self.basis)
            self._set_angles(angles.x, angles.y, angles.z)
        except ZeroDivisionError as err:
            self._set_basis(Matrix3.identity())
            self._set_angles(0.0, 0.0, 0.0)

    def _build_basis(self):
        try:
            self._set_angles(*(self.angles + self.omega * self.delta_t))
            y_axis = (self.basis.up    + Vector3.cross(self.omega, self.basis.up)    * self.delta_t).normalized()
            z_axis = (self.basis.front + Vector3.cross(self.omega, self.basis.front) * self.delta_t).normalized()
            z_axis = (z_axis * (1.0 - self.k_accel) + self.k_accel * self.acceleration).normalized()
            x_axis = Vector3.cross(z_axis, y_axis).normalized()
            y_axis = Vector3.cross(x_axis, z_axis).normalized()
            self._set_basis(Matrix3(x_axis.x, y_axis.x, z_axis.x,
                                    x_axis.y, y_axis.y, z_axis.y,
                                    x_axis.z, y_axis.z, z_axis.z))
        except ZeroDivisionError as zero:
            self._set_basis(self._basis_curr)

    def read_request(self) -> bool:
        flag, response = self._device_read_request()
        if not flag:
            return False
        self._parce_response(response)
        self._update_time()
        if self.use_filtering:
            self._filter_values()
        self._build_basis()
        return True

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
            self._mag_calib /= self._calib_cntr
            self._accel_calib_lin /= self._calib_cntr
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

        if self.read_request():
            self._calib_cntr += 1
            self._accel_calib += self.acceleration
            self._omega_calib += self.omega
            self._mag_calib += self.magnetometer
            self._accel_calib_lin += self.acceleration_linear
        return True

    def update(self):
        while True:
            yield self.read_request()

    def record(self, file_path: str, time_out: float = 0.016, record_time: float = 180.0):
        """
        Пишет измерения акселерометра в файл с интервалом time_out на протяжении времени record_time.
        :param file_path: куда пишем
        :param time_out: время между записями
        :param record_time: общее время записи
        """
        import datetime as dt
        with open(file_path, 'wt') as record:
            t_elapsed = 0.0
            d_t = 0.0
            print(f"{{\n\"record_date\": \"{dt.datetime.now().strftime('%H; %M; %S')}\",\n", file=record)
            print("\"way_points\" :[", file=record)
            while t_elapsed <= record_time:
                d_t = time.perf_counter()
                self.update()
                print(self, file=record)
                d_t = time.perf_counter() - d_t
                print(' ,', file=record)
                if d_t > time_out:
                    t_elapsed += d_t
                    print(_device_progres_bar(t_elapsed / record_time, label='RECORDING...'), end='')
                    continue
                t_elapsed += time_out
                print(_device_progres_bar(t_elapsed / record_time, label='RECORDING...'), end='')
                time.sleep(time_out - d_t)
            record.seek(record.tell() - 3, 0)
            print("]\n}", file=record)

