from Odometry.vmath.core.transforms.transform import Transform
from Odometry.vmath.core.matrices import Mat4
from Odometry.vmath.core.vectors import Vec3
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

PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47


class Accelerometer(IDevice):

    def __init__(self):

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

    def __read_raw_data(self, addr: int) -> np.int16:
        # Accelerometric and Gyro value are 16-bit
        high = i2c_bus.read_byte_data(self.__address, addr)
        low = i2c_bus.read_byte_data(self.__address, addr + 1)

        # concatenate higher and lower value
        value = ((high << 8) | low)

        # to get signed value from mpu6050
        if value > 32768:
            value = value - 65536
        return value

    def __build_transform(self):
        # Read Gyroscope raw value
        try:
            gyro_x: np.int16 = self.__read_raw_data(ACCEL_XOUT_H)
            gyro_y: np.int16 = self.__read_raw_data(ACCEL_YOUT_H)
            gyro_z: np.int16 = self.__read_raw_data(ACCEL_ZOUT_H)
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
            i2c_bus.write_byte_data(self.__address, SMPLRT_DIV, 7)

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
