from Odometry.devices.sensors_utils.real_time_filter import RealTimeFilter
from Odometry.devices.i_device import IDevice
from Odometry.vmath.core.vectors import Vec3
from typing import List, Tuple, Deque
import datetime as dt
import numpy as np
import time
from collections import deque

from devices.sensors.low_level_accelerometer import HardwareAccelerometer


class Accelerometer(IDevice):

    def __init__(self):

        self.__accelerometer: HardwareAccelerometer = HardwareAccelerometer()

        self.__buffer_capacity: int = 512

        self.__orientations: Deque[Vec3]

        self.__accelerations: Deque[Vec3]

        self.__velocities: Deque[Vec3]

        self.__positions: Deque[Vec3]

        self.__time_values: Deque[float]

        self.__time_deltas: Deque[float]

        self._re_alloc_buffers()

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

    def _re_alloc_buffers(self) -> None:
        self.__orientations = deque(maxlen=self.buffer_cap)  # [Vec3(0.0) for _ in range()]
        self.__accelerations = deque(maxlen=self.buffer_cap)  # [Vec3(0.0) for _ in range(self.buffer_cap)]
        self.__time_values = deque(maxlen=self.buffer_cap)  # [0.0 for _ in range(self.buffer_cap)]
        self.__time_deltas = deque(maxlen=self.buffer_cap)  # [0.0 for _ in range(self.buffer_cap)]
        self.__velocities = deque(maxlen=self.buffer_cap)  # [Vec3(0.0) for _ in range(self.buffer_cap)]
        self.__positions = deque(maxlen=self.buffer_cap)  # [Vec3(0.0) for _ in range(self.buffer_cap)]

        self.__accelerations.append(Vec3(0.0))
        self.__velocities.append(Vec3(0.0))
        self.__positions.append(Vec3(0.0))
        self.__time_values.append(0.0)
        self.__time_deltas.append(0.0)


    @property
    def orientation(self) -> Vec3:
        return self.__orientations[-1]

    @property
    def acceleration(self) -> Vec3:
        return self.__accelerations[-1]

    @property
    def velocity(self) -> Vec3:
        return self.__velocities[-1]

    @property
    def position(self) -> Vec3:
        return self.__positions[-1]

    @property
    def time_value(self):
        return self.__time_values[-1]

    @property
    def time_delta(self):
        return self.__time_deltas[-1]  # - self.__time_values[self.__buffer_indent - 1]

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

    def _build_way_point(self) -> None:

        self.__time_values.append  (self.__accelerometer.last_accel_measurement_t)
        self.__time_deltas.append  (self.__accelerometer.last_accel_measurement_dt)
        self.__accelerations.append(self.__accelerometer.acceleration)
        self.__orientations.append (self.__accelerometer.orientation)

        """
                d_t = self.__time_deltas[-1]
        
                a_curr = self.__accelerations[-1]
                a_prev = self.__accelerations[-2]
        
                v_prev = self.__velocities[-1]
                v_curr = v_prev + (a_curr + a_prev) * d_t * 0.5
        
                s_prev = self.__positions[-1]
                s_curr = s_prev + (v_prev + v_curr) * d_t * 0.5
        
        """
        v_curr = self.__velocities[-1] + (self.__accelerations[-1] + self.__accelerations[-2]) * self.__time_deltas[-1] * 0.5
        self.__velocities.append(v_curr)
        self.__positions.append(self.__positions[-1] + (self.__velocities[-1] + v_curr) * self.__time_deltas[-1] * 0.5)

    def _init(self) -> bool:

        if not self.__accelerometer.init():
            print(f"Accelerometer init error...")

            return False

        self.__accelerometer.calibrate()

        return True

    def _update(self) -> None:
        self.__build_way_point()

    def _logging(self) -> str:
        return f",\n{{\n" \
               f"\t\"acceleration\":{self.__accelerations[self.__buffer_indent]},\n" \
               f"\t\"velocity\"    :{self.__velocities   [self.__buffer_indent]},\n" \
               f"\t\"position\"    :{self.__positions    [self.__buffer_indent]},\n" \
               f"\t\"orientation\" :{self.__orientations [self.__buffer_indent]},\n" \
               f"\t\"curr_time\"   :{self.__time_values  [self.__buffer_indent]},\n" \
               f"\t\"delta_time\"  :{self.__time_deltas  [self.__buffer_indent]}\n}}"


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