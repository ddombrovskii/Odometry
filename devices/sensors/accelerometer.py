from Odometry.devices.sensors_utils.real_time_filter import RealTimeFilter
from Odometry.devices.i_device import IDevice
from Odometry.vmath.core.vectors import Vec3
from typing import List, Tuple
import datetime as dt
import numpy as np
import time


GRAVITY_CONSTANT = 9.80665
GRAVITY_VECTOR = Vec3(0.0, -GRAVITY_CONSTANT, 0.0)
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

FILTER_BW_256 = 0x00
FILTER_BW_188 = 0x01
FILTER_BW_98 = 0x02
FILTER_BW_42 = 0x03
FILTER_BW_20 = 0x04
FILTER_BW_10 = 0x05
FILTER_BW_5 = 0x06

run_with_errors = True

i2c_bus = None

try:
    # TODO add board version check
    import smbus
except ImportError as ex:
    print(f"SM Bus import error!!!\n{ex.args}")
    if not run_with_errors:
        exit(1)

try:
    # TODO add board version check
    i2c_bus = smbus.SMBus(1)  # or bus = smbus.SMBus(0) for older version boards
except NameError as ex:
    print(f"SM Bus init error!!!\n{ex.args}")
    if not run_with_errors:
        exit(1)


def read_raw_data(device_addr: int, addr: int) -> Tuple[bool, np.int16]:
    # Accelerometer and Gyro value are 16-bit
    try:
        high = i2c_bus.read_byte_data(device_addr, addr)
    except Exception as _ex:
        print(f"i2c read high error\n{_ex.args}")
        return False, np.int16(0)

    try:
        low = i2c_bus.read_byte_data(device_addr, addr + 1)
    except Exception as _ex:
        print(f"i2c read low error\n{_ex.args}")
        return False, np.int16(0)

    # concatenate higher and lower value
    value = (high << 8) | low

    # to get signed value from mpu6050
    if value >= 0x8000:
        value -= 65536
    return True, value


class Accelerometer(IDevice):

    def __init__(self):

        self.__buffer_indent: int = 0

        self.__buffer_capacity: int = 32

        self.__address = 0x68  # mpu 6050

        self.__measurements_samples: int = 32

        self.__orientations: List[Vec3]

        self.__accelerations: List[Vec3]

        self.__velocities: List[Vec3]

        self.__positions: List[Vec3]

        self.__time_values: List[float]

        self.__time_deltas: List[float]

        self._re_alloc_buffers()

        self.__filters: List[RealTimeFilter] = []
        """
        self.__filters[0] = gyro x
        self.__filters[1] = gyro y
        self.__filters[2] = gyro z

        self.__filters[3] = acc x
        self.__filters[4] = acc y
        self.__filters[5] = acc z
        """
        for _ in range(6):
            _filter = RealTimeFilter()
            _filter.k_arg = 0.09
            _filter.kalman_error = 0.8
            _filter.mode = 2
            self.__filters.append(_filter)

        super().__init__()

        self._log_file_origin: str = \
            f"accelerometer_records/accelerometer_log {dt.datetime.now().strftime('%H; %M; %S')}.json"

    def __str__(self):
        separator = ",\n"
        return f"{{\n" \
               f"\t\"measurements_samples\": {self.__measurements_samples},\n" \
               f"\t\"buffer_cap\"          : {self.__buffer_capacity},\n" \
               f"\t\"orientations\"        :[\n{separator.join(str(item) for item in self.orientations)}\n],\n" \
               f"\t\"accelerations\"       :[\n{separator.join(str(item) for item in self.accelerations)}\n]\n" \
               f"\t\"velocities\"          :[\n{separator.join(str(item) for item in self.velocities)}\n]\n" \
               f"\t\"positions\"           :[\n{separator.join(str(item) for item in self.positions)}\n]\n" \
               f"\t\"time_values\"         :[\n{separator.join(str(item) for item in self.time_values)}\n],\n" \
               f"\t\"time_deltas\"         :[\n{separator.join(str(item) for item in self.time_deltas)}\n]\n" \
               f"\n}}"

    __repr__ = __str__

    def _buffer_index(self, index: int) -> int:
        return (index + self.__buffer_indent) % self.__buffer_capacity

    def _re_alloc_buffers(self) -> None:
        self.__orientations = [Vec3(0.0) for _ in range(self.buffer_cap)]

        self.__accelerations = [Vec3(0.0) for _ in range(self.buffer_cap)]

        self.__time_values = [0.0 for _ in range(self.buffer_cap)]

        self.__time_deltas = [0.0 for _ in range(self.buffer_cap)]

        self.__velocities = [Vec3(0.0) for _ in range(self.buffer_cap)]

        self.__positions = [Vec3(0.0) for _ in range(self.buffer_cap)]

    @property
    def acceleration_range_raw(self) -> int:
        """
        Диапазон измеряемых ускорений
        ACCEL_SCALE_MODIFIER_2G = 16384.0
        ACCEL_SCALE_MODIFIER_4G = 8192.0
        ACCEL_SCALE_MODIFIER_8G = 4096.0
        ACCEL_SCALE_MODIFIER_16G = 2048.0
        """
        return i2c_bus.read_byte_data(self.__address, ACCEL_CONFIG)

    @acceleration_range_raw.setter
    def acceleration_range_raw(self, accel_range: int) -> None:
        """
        Диапазон измеряемых ускорений
        ACCEL_SCALE_MODIFIER_2G = 16384.0
        ACCEL_SCALE_MODIFIER_4G = 8192.0
        ACCEL_SCALE_MODIFIER_8G = 4096.0
        ACCEL_SCALE_MODIFIER_16G = 2048.0
        """
        if not self.require_lock():
            return
        i2c_bus.write_byte_data(self.__address, ACCEL_CONFIG, 0x00)
        i2c_bus.write_byte_data(self.__address, ACCEL_CONFIG, accel_range)
        self.release_lock()

    @property
    def acceleration_range(self) -> float:
        """
        Диапазон измеряемых ускорений, выраженный в м/сек^2
        """
        raw_data = self.acceleration_range_raw
        if raw_data == ACCEL_RANGE_2G:
            return 2 * GRAVITY_CONSTANT
        if raw_data == ACCEL_RANGE_4G:
            return 4 * GRAVITY_CONSTANT
        if raw_data == ACCEL_RANGE_8G:
            return 8 * GRAVITY_CONSTANT
        if raw_data == ACCEL_RANGE_16G:
            return 16 * GRAVITY_CONSTANT
        return -1

    @property
    def acceleration_scale(self) -> float:
        raw_data = self.acceleration_range_raw

        if raw_data == ACCEL_RANGE_2G:
            return ACCEL_SCALE_MODIFIER_2G
        if raw_data == ACCEL_RANGE_4G:
            return ACCEL_SCALE_MODIFIER_4G
        if raw_data == ACCEL_RANGE_8G:
            return ACCEL_SCALE_MODIFIER_8G
        if raw_data == ACCEL_RANGE_16G:
            return ACCEL_SCALE_MODIFIER_16G
        return ACCEL_RANGE_2G

    @property
    def gyroscope_range_raw(self) -> int:
        """
        Диапазон измеряемых значений гироскопа
        GYRO_RANGE_250DEG = 0x00
        GYRO_RANGE_500DEG = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        return i2c_bus.read_byte_data(self.__address, GYRO_CONFIG)

    @gyroscope_range_raw.setter
    def gyroscope_range_raw(self, accel_range: int) -> None:
        """
        Диапазон измеряемых значений гироскопа
        GYRO_RANGE_250DEG = 0x00
        GYRO_RANGE_500DEG = 0x08
        GYRO_RANGE_1000DEG = 0x10
        GYRO_RANGE_2000DEG = 0x18
        """
        if not self.require_lock():
            return
        i2c_bus.write_byte_data(self.__address, GYRO_CONFIG, 0x00)
        i2c_bus.write_byte_data(self.__address, GYRO_CONFIG, accel_range)
        self.release_lock()

    @property
    def gyroscope_range(self) -> int:
        """
        Диапазон измеряемых значений гироскопа в градусах
        """
        raw_data = self.gyroscope_range_raw
        if raw_data == GYRO_RANGE_250DEG:
            return 250
        if raw_data == GYRO_RANGE_500DEG:
            return 500
        if raw_data == GYRO_RANGE_1000DEG:
            return 1000
        if raw_data == GYRO_RANGE_2000DEG:
            return 2000
        return -1

    @property
    def gyroscope_scale(self) -> float:
        # ACCEL_SCALE_MODIFIER_2G
        raw_data = self.gyroscope_range_raw
        if raw_data == GYRO_RANGE_250DEG:
            return GYRO_SCALE_MODIFIER_250DEG
        if raw_data == GYRO_RANGE_500DEG:
            return GYRO_SCALE_MODIFIER_500DEG
        if raw_data == GYRO_RANGE_1000DEG:
            return GYRO_SCALE_MODIFIER_1000DEG
        if raw_data == GYRO_RANGE_2000DEG:
            return GYRO_SCALE_MODIFIER_2000DEG
        return GYRO_RANGE_250DEG

    @property
    def hardware_filter_range_raw(self) -> int:
        """
        Документация???
        """
        ext_sync_set = i2c_bus.read_byte_data(self.__address, MPU_CONFIG) & 0b00111000
        return i2c_bus.read_byte_data(self.__address, MPU_CONFIG, ext_sync_set)

    @hardware_filter_range_raw.setter
    def hardware_filter_range_raw(self, filter_range) -> None:
        """
        Документация???
        """
        if not self.require_lock():
            return
        ext_sync_set = i2c_bus.read_byte_data(self.__address, MPU_CONFIG) & 0b00111000
        i2c_bus.write_byte_data(self.__address, MPU_CONFIG, ext_sync_set | filter_range)
        self.release_lock()

    @property
    def hardware_filter_range(self) -> int:
        """
        Документация???
        """
        filter_range = self.hardware_filter_range_raw
        if FILTER_BW_256 == filter_range:
            return 250
        if FILTER_BW_188 == filter_range:
            return 500
        if FILTER_BW_98 == filter_range:
            return 1000
        if FILTER_BW_10 == filter_range:
            return 2000
        if FILTER_BW_5 == filter_range:
            return 2000
        return -1

    @property
    def orientation(self) -> Vec3:
        flag, val = self.__read_gyro_data()
        if flag:
            return val
        return self.__orientations[self.__buffer_indent]

    @property
    def acceleration(self) -> Vec3:
        flag, val = self.__read_acceleration_data()
        if flag:
            return val
        return self.__accelerations[self.__buffer_indent]

    @property
    def velocity(self) -> Vec3:
        return self.__velocities[self.__buffer_indent]

    @property
    def position(self) -> Vec3:
        return self.__positions[self.__buffer_indent]

    @property
    def time_value(self):
        return self.__time_values[self.__buffer_indent]

    @property
    def time_delta(self):
        return self.__time_values[self.__buffer_indent] - self.__time_values[self.__buffer_indent - 1]

    @property
    def orientations(self):
        for i in range(self.__buffer_capacity):
            yield self.__orientations[self._buffer_index(i)]

    @property
    def accelerations(self):
        for i in range(self.__buffer_capacity):
            yield self.__accelerations[self._buffer_index(i)]

    @property
    def velocities(self):
        for i in range(self.__buffer_capacity):
            yield self.__velocities[self._buffer_index(i)]

    @property
    def positions(self):
        for i in range(self.__buffer_capacity):
            yield self.__positions[self._buffer_index(i)]

    @property
    def time_values(self):
        for i in range(self.__buffer_capacity):
            yield self.__time_values[self._buffer_index(i)]

    @property
    def time_deltas(self):
        for i in range(self.__buffer_capacity):
            yield self.__time_deltas[self._buffer_index(i)]

    @property
    def buffer_cap(self) -> int:
        return self.__buffer_capacity

    @buffer_cap.setter
    def buffer_cap(self, cap: int) -> None:
        if not self.require_lock():
            return
        self.__buffer_capacity = max(10, min(65536, cap))  # 65536 = 2**16
        self._re_alloc_buffers()
        self.release_lock()

    def _try_open_log_file(self, orig: str = None) -> bool:
        if super()._try_open_log_file(orig):
            self._log_file_descriptor.write("\n\"way_points\":[\n")
            return True
        return False

    def _try_close_log_file(self) -> bool:
        if self._log_file_descriptor is None:
            return True
        try:
            self._log_file_descriptor.seek(self._log_file_descriptor.tell() - 1)
            self._log_file_descriptor.write("\n]")
        except Exception as _ex:
            print(f"log file closing failed:\n{_ex.args}")
            return False or super()._try_close_log_file()
        return super()._try_close_log_file()

    def __read_acceleration_data(self) -> Tuple[bool, Vec3]:

        acceleration = Vec3(0.0)

        scl = 1.0 / self.acceleration_scale * GRAVITY_CONSTANT

        flag, value = read_raw_data(self.__address, ACCEL_X_OUT_H)

        if not flag:
            return flag, acceleration
        acceleration.x = self.__filters[3].filter(float(value) * scl)

        flag, value = read_raw_data(self.__address, ACCEL_Y_OUT_H)

        if not flag:
            return flag, acceleration
        acceleration.y = self.__filters[4].filter(float(value) * scl)

        flag, value = read_raw_data(self.__address, ACCEL_Z_OUT_H)

        if not flag:
            return flag, acceleration
        acceleration.z = self.__filters[5].filter(float(value) * scl)

        return flag, acceleration

    def __read_gyro_data(self) -> Tuple[bool, Vec3]:

        orientation = Vec3(0.0)

        scl = 1.0 / self.gyroscope_scale

        flag, value = read_raw_data(self.__address, GYRO_X_OUT_H)

        if not flag:
            return flag, orientation
        orientation.x = float(value) * scl  # self.__filters[0].filter(float(value) * scl)

        flag, value = read_raw_data(self.__address, GYRO_Y_OUT_H)

        if not flag:
            return flag, orientation
        orientation.y = float(value) * scl  # self.__filters[1].filter(float(value) * scl)

        flag, value = read_raw_data(self.__address, GYRO_Z_OUT_H)

        if not flag:
            return flag, orientation
        orientation.z = float(value) * scl  # self.__filters[2].filter(float(value) * scl)

        return flag, orientation

    def __build_way_point(self) -> None:
        curr = self.__buffer_indent
        prev = 0 if self.__buffer_indent == 0 else self.__buffer_indent - 1
        self.__time_values[curr] = time.perf_counter()
        self.__time_deltas[curr] = self.time_delta
        self.__accelerations[curr] = self.acceleration
        self.__orientations[curr] = self.orientation

        a = self.__accelerations[curr] - self.__accelerations[prev]

        v = self.__velocities[prev]

        self.__velocities[curr] = v + a * self.__time_deltas[curr]

        self.__positions[curr] = \
            self.__positions[prev] + \
            self.__velocities[prev] * self.__time_deltas[curr]

        self.__buffer_indent += 1
        self.__buffer_indent %= self.__buffer_capacity

    def _init(self) -> bool:
        try:
            # Write to power management register
            i2c_bus.write_byte_data(self.__address, PWR_MGMT_1, 1)

            # write to sample rate register
            i2c_bus.write_byte_data(self.__address, SAMPLE_RATE_DIV, 7)

            # Write to Configuration register
            i2c_bus.write_byte_data(self.__address, MPU_CONFIG, 0)

            # Write to Gyro configuration register
            i2c_bus.write_byte_data(self.__address, GYRO_CONFIG, 24)

            # Write to interrupt enable register
            i2c_bus.write_byte_data(self.__address, INT_ENABLE, 1)

        except AttributeError as ex_:
            print(f"Accelerometer init error {ex_.args}")
            return False
        for _ in range(100):
            self.__read_gyro_data()
            self.__read_acceleration_data()

        return True

    def _update(self) -> None:
        self.__build_way_point()

    def _logging(self) -> str:
        return f",\n{{\n" \
               f"\t\"acceleration\":{self.__accelerations[self.__buffer_indent]},\n" \
               f"\t\"velocity\"    :{self.__velocities[self.__buffer_indent]},\n" \
               f"\t\"position\"    :{self.__positions[self.__buffer_indent]},\n" \
               f"\t\"orientation\" :{self.__orientations[self.__buffer_indent]},\n" \
               f"\t\"curr_time\"   :{self.__time_values[self.__buffer_indent]},\n" \
               f"\t\"delta_time\"  :{self.__time_deltas[self.__buffer_indent]}\n}}"


def accelerometer_info():
    acc = Accelerometer()

    print(f"acceleration_range {acc.acceleration_range}")
    print(f"acceleration_range_raw {acc.acceleration_range_raw}")
    print(f"gyroscope_range {acc.gyroscope_range}")
    print(f"gyroscope_range_raw {acc.gyroscope_range_raw}")


def accelerometer_data_recording():
    acc = Accelerometer()
    acc.update_rate = 1.0 / 30.0
    acc.life_time = 300  # 1 минута на запись
    acc.enable_logging = True
    acc.start()
    acc.join()


def accelerometer_data_reading():
    acc = Accelerometer()
    acc.update_rate = 1.0 / 30.0
    acc.life_time = 1  # 1 минута на запись
    acc.start()
    while acc.alive:
        # print(f"{acc.velocity}")
        time.sleep(0.1)
        # print(f"{{\n\t\"t\" = {acc.time_value},\n\t\"o\" = {acc.orientation},\n\t\"a\" = {acc.acceleration},\n\t\"v\" ="
        #      f" {acc.velocity},\n\t\"p\" = {acc.position}\n}}")

    acc.join()


if __name__ == "__main__":
    #    accelerometer_data_reading()
    accelerometer_data_recording()