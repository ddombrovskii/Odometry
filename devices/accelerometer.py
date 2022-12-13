from typing import Callable, Tuple, List
from vmath.core.transforms.transform import Transform
from vmath.core.matrices import Mat4
from vmath.core.vectors import Vec3
from i_device import IDevice
import datetime as dt
import numpy as np
import time

run_with_errors = True

i2c_bus = None

try:
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


def read_raw_data(device_addr: int, addr: int) -> np.int16:
    # Accelerometer and Gyro value are 16-bit
    try:
        high = i2c_bus.read_byte_data(device_addr, addr)
    except Exception as _ex:
        print(f"i2c read high error\n{_ex.args}")
        return np.int16(0)

    try:
        low = i2c_bus.read_byte_data(device_addr, addr + 1)
    except Exception as _ex:
        print(f"i2c read low error\n{_ex.args}")
        return np.int16(0)

    # concatenate higher and lower value
    value = ((high << 8) | low)

    # to get signed value from mpu6050
    if value > 32768:
        value = value - 65536
    return value


PWR_MGMT_1 = 0x6B
SAMPLE_RATE_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38

ACCEL_X_OUT_H = 0x43
ACCEL_Y_OUT_H = 0x45
ACCEL_Z_OUT_H = 0x47

GYRO_X_OUT_H = 0x3B
GYRO_Y_OUT_H = 0x3D
GYRO_Z_OUT_H = 0x3F


def euler_ode(v_0: Vec3, f_v_0: Vec3, d_time: float):
    return v_0 + f_v_0 * d_time


class WayPoint:
    def __init__(self, p: Vec3, v: Vec3, accel: Vec3, gyro: Vec3, t: float, d_t: float):
        self.__position:     Vec3 = p
        self.__velocity:     Vec3 = v
        self.__acceleration: Vec3 = accel
        self.__gyro_data:    Vec3 = gyro
        self.__time_stamp:   str = dt.datetime.now().strftime('%H; %M; %S')
        self.__curr_time:    float = t
        self.__delta_time:   float = d_t

    def __str__(self):
        return f"{{\n" \
               f"\t\"position\"    :{self.position},\n" \
               f"\t\"velocity\"    :{self.velocity},\n" \
               f"\t\"acceleration\":{self.acceleration},\n" \
               f"\t\"gyro_data\"   :{self.gyro_data},\n" \
               f"\t\"time_stamp\"  :{self.time_stamp},\n" \
               f"\t\"curr_time\"   :{self.curr_time},\n" \
               f"\t\"delta_time\"  :{self.delta_time}\n}}"

    @property
    def position(self) -> Vec3:
        return self.__position

    @property
    def velocity(self) -> Vec3:
        return self.__velocity

    @property
    def acceleration(self) -> Vec3:
        return self.__acceleration

    @property
    def gyro_data(self) -> Vec3:
        return self.__gyro_data

    @property
    def time_stamp(self) -> str:
        return self.__time_stamp

    @property
    def curr_time(self) -> float:
        return self.__curr_time

    @property
    def delta_time(self) -> float:
        return self.__delta_time


class Accelerometer(IDevice):

    def __init__(self):
        self.__way_points: List[WayPoint] = []

        self.__time_stamps: [str] = []

        self.__transforms_history_cap = 1000

        self.__transforms_history: [Mat4] = []

        self.__transform = Transform()

        self.__address = 0x68  # mpu 6050

        super().__init__()

        self._log_file_origin: str = f"accelerometer_log {dt.datetime.now().strftime('%H; %M; %S')}.txt"

    @property
    def transforms_time_stamps(self) -> [str]:
        return self.__time_stamps

    @property
    def transforms_history(self) -> [Mat4]:
        return self.__transforms_history

    @property
    def transforms_history_cap(self) -> int:
        return self.__transforms_history_cap

    @transforms_history_cap.setter
    def transforms_history_cap(self, cap: int) -> None:
        if not self.require_lock():
            return
        self.__transforms_history_cap = max(10, min(10000, cap))
        self.release_lock()

    def __repr__(self):
        if len(self.__time_stamps) == 0:
            return "NO DATA!!!"
        return f"transform at time {self.__time_stamps[len(self.__time_stamps) - 1]}\n" \
               f"{self.__transforms_history[len(self.__transforms_history) - 1].as_array}\n"

    __str__ = __repr__

    def __read_acceleration_data(self) -> Vec3:
        return Vec3(float(read_raw_data(self.__address, ACCEL_X_OUT_H)),
                    float(read_raw_data(self.__address, ACCEL_Y_OUT_H)),
                    float(read_raw_data(self.__address, ACCEL_Z_OUT_H)))

    def __read_gyro_data(self) -> Vec3:
        return Vec3(float(read_raw_data(self.__address, ACCEL_X_OUT_H)),
                    float(read_raw_data(self.__address, ACCEL_Y_OUT_H)),
                    float(read_raw_data(self.__address, ACCEL_Z_OUT_H))).normalized()

    def __build_transform(self):
        curr_t, delta_t = self.life_time, self.time_delta
        gyro:         Vec3 = self.__read_gyro_data()
        acceleration: Vec3 = self.__read_acceleration_data()

        if len(self.__way_points) in (0, 1):
            pass

        # Read Gyroscope raw value
        try:
            gyro_x: np.int16 = read_raw_data(self.__address, GYRO_X_OUT_H)
            gyro_y: np.int16 = read_raw_data(self.__address, GYRO_X_OUT_H)
            gyro_z: np.int16 = read_raw_data(self.__address, GYRO_X_OUT_H)
            self.__transform.up = Vec3(gyro_x, gyro_y, gyro_z).normalized()
        except RuntimeError as ex_:
            print(f"Accelerometer measurements reading error {ex_.args}")
            return

        curr_time: str = dt.datetime.now().strftime('%H; %M; %S')

        self.__transforms_history.append(self.__transform.transform_matrix.copy())

        self.__time_stamps.append(curr_time)

        if len(self.__transforms_history) == self.__transforms_history_cap:
            del (self.__transforms_history[0])
            del (self.__time_stamps[0])

    def _init(self) -> bool:
        try:
            # write to sample rate register
            i2c_bus.write_byte_data(self.__address, SAMPLE_RATE_DIV, 7)

            # Write to power management register
            i2c_bus.write_byte_data(self.__address, PWR_MGMT_1, 1)

            # Write to Configuration register
            i2c_bus.write_byte_data(self.__address, CONFIG, 0)

            # Write to Gyro configuration register
            i2c_bus.write_byte_data(self.__address, GYRO_CONFIG, 24)

            # Write to interrupt enable register
            i2c_bus.write_byte_data(self.__address, INT_ENABLE, 1)

        except AttributeError as ex_:
            print(f"Accelerometer init error {ex_.args}")
            return False

        return True

    def _update(self):
        self.__build_transform()

    def _logging(self) -> str:
        return self.__str__()


def accelerometer_test():
    acc = Accelerometer()
    acc.update_rate = 1
    # acc.enable_logging = True
    acc.start()
    cntr = 0

    if not acc.alive:
        return
    while cntr != 10:
        cntr += 1
        time.sleep(acc.update_rate)
        print(acc)
    acc.join()


if __name__ == "__main__":
    accelerometer_test()
