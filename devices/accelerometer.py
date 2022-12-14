from typing import Callable, Tuple, List
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

        self.__measurements_samples: int =  8

        self.__way_points_buffer_cap: int = 1024

        self.__address = 0x68  # mpu 6050

        super().__init__()

        self._log_file_origin: str = f"accelerometer_log {dt.datetime.now().strftime('%H; %M; %S')}.txt"

    @property
    def way_points_buffer_cap(self) -> int:
        return self.__way_points_buffer_cap

    @way_points_buffer_cap.setter
    def way_points_buffer_cap(self, cap: int) -> None:
        if not self.require_lock():
            return
        self.__way_points_buffer_cap = max(10, min(10000, cap))
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

    def __build_way_point(self) -> WayPoint:

        curr_t, delta_t = self.life_time, time.perf_counter() - self.life_time

        gyro: Vec3 = self.__read_gyro_data()

        acceleration: Vec3 = self.__read_acceleration_data()

        if len(self.__way_points) == 0:
            return WayPoint(Vec3(0), Vec3(0), acceleration, gyro, curr_t, delta_t)

        last_wp = self.__way_points[-1]

        velocity = last_wp.delta_time * last_wp.acceleration + last_wp.velocity

        position = last_wp.delta_time * velocity + last_wp.position

        return WayPoint(position, velocity, acceleration, gyro, curr_t, delta_t)

    def __build_way_points(self) -> List[WayPoint]:
        update_rate: float = self.update_rate * (self.__measurements_samples - 1)  /  self.__measurements_samples

        current_t: float = 0.0

        delta_t: float = update_rate / self.__measurements_samples

        way_points = []

        for _ in range(self.__measurements_samples):
            if current_t >= update_rate:
                break

            t = time.perf_counter()
            way_points.append(self.__build_way_point())
            t = time.perf_counter() - t

            if t > delta_t:
                current_t += t
                continue

            time.sleep(delta_t - t)
            current_t += delta_t

        return way_points

    def __build_transform(self):
        curr_t, delta_t = self.life_time, self.time_delta
        gyro:         Vec3 = self.__read_gyro_data()
        acceleration: Vec3 = self.__read_acceleration_data()

        if len(self.__way_points) == 0:
            self.__way_points.append(WayPoint(Vec3(0), Vec3(0), acceleration, gyro, curr_t, delta_t))
            return

        last_wp = self.__way_points[-1]
        velocity = last_wp.delta_time * last_wp.acceleration + last_wp.velocity
        position = last_wp.delta_time * velocity             + last_wp.position
        self.__way_points.append(WayPoint(position, velocity, acceleration, gyro, curr_t, delta_t))
        return

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


#if __name__ == "__main__":
    # if 1 in (1, 2, 3):
    #    print('1...')
 #   accelerometer_test()

def median_filter_1d(array_data: np.ndarray, filter_size: int = 15, do_copy: bool = False,
                     range_start: int = 0, range_end: int = -1) -> np.ndarray:
    if filter_size % 2 != 1:
        raise Exception("Median filter length must be odd.")

    if array_data.ndim != 1:
        raise Exception("Input must be one-dimensional.")

    if do_copy:
        result = np.zeros_like(array_data)
    else:
        result = array_data

    if range_start == range_end:
        return result

    if range_end < 0:
        range_end = array_data.size

    if range_end < range_start:
        range_end, range_start = range_start, range_end

    range_end = min(range_end, array_data.size)

    range_start = max(range_start, 0)

    import bisect

    values_window = []

    half_filter_size = filter_size // 2

    for i in range(range_start, range_end):
        for j in range(i - half_filter_size, i + half_filter_size):
            if j < 0:
                bisect.insort(values_window, 0)
                continue
            if j >= array_data.size:
                bisect.insort(values_window, 0)
                continue
            bisect.insort(values_window, array_data[j])

        result[i] = values_window[len(values_window)//2]

        values_window.clear()

    return result


def _test ():
    import pylab as p
    x = np.linspace (0, 1, 101)
    x[3::10] = 1.5
    #p.plot (x)
   # y_  =  median_filter_1d (x, 5)
    y__ =  median_filter_1d  (x,  5, range_start = -20, range_end=60)
    #print(f"shape: {y_.shape},  size: {y_.size}")
    print(f"shape: {y__.shape}, size: {y__.size}")
   # p.plot (y_)
    p.plot (y__)
    p.show ()


if __name__ == '__main__':
    _test ()