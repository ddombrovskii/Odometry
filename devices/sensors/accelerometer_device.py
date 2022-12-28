from devices.sensors.accelerometer import Accelerometer
from devices.i_device import IDevice
from vmath.core.vectors import Vec3
from typing import List
import datetime as dt
import time


class AccelerometerDevice(IDevice):

    def __init__(self):

        self.__accelerometer: Accelerometer = Accelerometer()

        super().__init__()

        self.__buffer_capacity: int = 512

        self._log_file_origin: str = \
            f"accelerometer_records/accelerometer_log {dt.datetime.now().strftime('%H; %M; %S')}.json"

        self.__angle_velocities: List[Vec3] = list()

        self.__angles: List[Vec3] = list()

        self.__accelerations: List[Vec3] = list()

        self.__velocities: List[Vec3] = list()

        self.__positions: List[Vec3] = list()

        self.__time_values: List[float] = list()

        self.__time_deltas: List[float] = list()

        self.__angle_velocities.append(Vec3(0.0))

        self.__angles.append(Vec3(0.0))

        self.__accelerations.append(Vec3(0.0))

        self.__velocities.append(Vec3(0.0))

        self.__positions.append(Vec3(0.0))

        self.__time_values.append(0.0)

        self.__time_deltas.append(0.0)

    def __str__(self):
        # TODO {CommonSettings DeviceSettings, AccelerometerSettings}
        separator = ",\n"
        return f"{{\n" \
               f"\t\"buffer_cap\"          : {self.__buffer_capacity},\n" \
               f"\t\"orientations\"        :[\n{separator.join(str(item) for item in self.angle_velocities)}\n],\n" \
               f"\t\"accelerations\"       :[\n{separator.join(str(item) for item in self.accelerations)}\n]\n" \
               f"\t\"velocities\"          :[\n{separator.join(str(item) for item in self.velocities)}\n]\n" \
               f"\t\"positions\"           :[\n{separator.join(str(item) for item in self.positions)}\n]\n" \
               f"\t\"time_values\"         :[\n{separator.join(str(item) for item in self.time_values)}\n],\n" \
               f"\t\"time_deltas\"         :[\n{separator.join(str(item) for item in self.time_deltas)}\n]\n" \
               f"\n}}"

    __repr__ = __str__

    def __build_way_point(self) -> None:

        self.__time_values.append(self.__accelerometer.accel_t)
        self.__time_deltas.append(self.__accelerometer.accel_dt)

        angle_v_curr = self.accelerometer.angles_velocity
        angle_curr = self.angle + (angle_v_curr + self.angle_velocity) * 0.5 * self.time_delta

        a_curr = self.accelerometer.acceleration
        v_curr = self.velocity + (a_curr + self.acceleration) * 0.5 * self.time_delta
        s_curr = self.position + (v_curr + self.velocity)     * 0.5 * self.time_delta

        self.__angle_velocities.append(angle_v_curr)
        self.__angles.          append(angle_curr)
        self.__accelerations.   append(a_curr)
        self.__velocities.      append(v_curr)
        self.__positions.       append(s_curr)

        if len(self.__time_values) > self.buffer_cap:
            del self.__time_values     [0]
            del self.__time_deltas     [0]
            del self.__angle_velocities[0]
            del self.__angles          [0]
            del self.__accelerations   [0]
            del self.__velocities      [0]
            del self.__positions       [0]

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
               f"\t\"acceleration\":{self.acceleration},\n" \
               f"\t\"velocity\"    :{self.velocity},\n" \
               f"\t\"position\"    :{self.position},\n" \
               f"\t\"orientation\" :{self.angle_velocity},\n" \
               f"\t\"curr_time\"   :{self.time_value},\n" \
               f"\t\"delta_time\"  :{self.time_delta}\n}}"

    @property
    def accelerometer(self) -> Accelerometer:
        return self.__accelerometer

    @property
    def angle_velocity(self) -> Vec3:
        """
        Последняя измеренная скорость изменения углов
        :return: Vec3
        """
        return self.__angle_velocities[-1]

    @property
    def angle(self) -> Vec3:
        """
        Последние измеренные ускорения
        :return: Vec3
        """
        return self.__angles[-1]

    @property
    def acceleration(self) -> Vec3:
        """
        Последние измеренные ускорения
        :return: Vec3
        """
        return self.__accelerations[-1]

    @property
    def velocity(self) -> Vec3:
        """
        Последние измеренные скорости
        :return: Vec3
        """
        return self.__velocities[-1]

    @property
    def position(self) -> Vec3:
        """
        Последнее измеренное положение
        :return: Vec3
        """
        return self.__positions[-1]

    @property
    def time_value(self) -> float:
        return self.__time_values[-1]

    @property
    def time_delta(self) -> float:
        return self.__time_deltas[-1]  # - self.__time_values[self.__buffer_indent - 1]

    @property
    def angle_velocities(self) -> List[Vec3]:
        return self.__angle_velocities

    @property
    def accelerations(self) -> List[Vec3]:
        return self.__accelerations

    @property
    def velocities(self) -> List[Vec3]:
        return self.__velocities

    @property
    def positions(self) -> List[Vec3]:
        return self.__positions

    @property
    def time_values(self) -> List[float]:
        return self.__time_values

    @property
    def time_deltas(self) -> List[float]:
        return self.__time_deltas

    @property
    def buffer_cap(self) -> int:
        return self.__buffer_capacity

    @buffer_cap.setter
    def buffer_cap(self, cap: int) -> None:
        if not self.require_lock():
            return
        self.__buffer_capacity = max(16, min(65536, cap))  # 65536 = 2**16
        self.release_lock()


def accelerometer_data_recording():
    acc = AccelerometerDevice()
    acc.update_rate = 1.0 / 30.0
    acc.life_time = 300  # 1 минута на запись
    acc.enable_logging = True
    acc.start()
    acc.join()


def accelerometer_data_reading():
    acc = AccelerometerDevice()
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
