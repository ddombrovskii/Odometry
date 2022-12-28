""" for raspberry
import sys
sys.path.append('/home/pi/Desktop/accelerometer/sensors_utils')
from circ_buffer import CircBuffer
"""
from devices.sensors_utils.circ_buffer import CircBuffer
from vmath.core import geometry_utils
from matplotlib import pyplot as plt
from typing import Callable
import numpy as np
import random
import math


class RealTimeFilter:
    def __init__(self):
        self.__mode = 0
        # 0 running average
        # 1 median
        # 2 kalman
        self.__window_size: int = 13
        self.__window_values: CircBuffer = CircBuffer(self.window_size)
        self.__prev_value: float = 0.0
        self.__curr_value: float = 0.0
        self.__k_arg: float = 0.08
        self.__err_measure: float = 0.9
        self.__err_estimate: float = 0.333
        self.__last_estimate: float = 0.0
        self._filter_function: Callable[[float], float]
        self.mode = 1

    def __str__(self):
        return f"\t{{\n" \
               f"\t\t\"mode\":        {self.mode},\n" \
               f"\t\t\"window_size\": {self.window_size},\n" \
               f"\t\t\"k_arg\":       {self.k_arg},\n" \
               f"\t\t\"kalman_error\":{self.kalman_error}\n" \
               f"\t}}"

    def clean_up(self):
        self.__err_estimate = 0.333
        self.__last_estimate = 0.0
        self.__prev_value = 0.0
        self.__curr_value = 0.0
        self.__window_values.clear()

    @property
    def window_size(self) -> int:
        return self.__window_size

    @window_size.setter
    def window_size(self, val: int) -> None:
        if val % 2 == 0:
            self.__window_size = 1 + math.fabs(val)
            self.__window_values = CircBuffer(self.window_size)
            return
        self.__window_size = math.fabs(val)
        self.__window_values = CircBuffer(self.window_size)

    @property
    def mode(self) -> int:
        return self.__mode

    @mode.setter
    def mode(self, val: int) -> None:
        if val == 0:
            self.__mode = int(val)
            self._filter_function = self.__run_avg_filter
            return
        if val == 1:
            self.__mode = int(val)
            self._filter_function = self.__mid_filter
            return
        if val == 2:
            self.__mode = int(val)
            self._filter_function = self.__kalman_filter
            return

    @property
    def k_arg(self) -> float:
        return self.__k_arg

    @k_arg.setter
    def k_arg(self, val: float) -> None:
        self.__k_arg = geometry_utils.clamp(0.0, 1.0, val)

    @property
    def kalman_error(self) -> float:
        return self.__err_measure

    @kalman_error.setter
    def kalman_error(self, val: float) -> None:
        self.__err_measure = geometry_utils.clamp(0.0, 1.0, val)

    def __run_avg_filter(self, value: float) -> float:
        self.__prev_value = self.__curr_value
        self.__curr_value += (value - self.__curr_value) * self.__k_arg
        return self.__curr_value

    def __mid_filter(self, value: float) -> float:
        self.__window_values.append(value)
        self.__prev_value = self.__curr_value
        self.__curr_value = self.__window_values.sorted[self.__window_values.capacity // 2]
        return self.__curr_value

    def __kalman_filter(self, value: float) -> float:
        _kalman_gain: float      = self.__err_estimate  / (self.__err_estimate  + self.__err_measure)
        _current_estimate: float = self.__last_estimate  + _kalman_gain * (value - self.__last_estimate)
        self.__err_estimate = (1.0 - _kalman_gain) * self.__err_estimate + \
                              math.fabs(self.__last_estimate - _current_estimate) * self.__k_arg
        self.__prev_value = self.__last_estimate
        self.__last_estimate = _current_estimate
        return self.__last_estimate

    def filter(self, value: float) -> float:
        return self._filter_function(value)

    def load_settings(self, settings_file):
        try:
            if "mode" in settings_file:
                self.mode = int(settings_file["mode"])
        except Exception as _ex:
            print(f"Real time filter settings read error :: incorrect mode {settings_file['mode']}")
            self.mode = 0

        try:
            if "window_size" in settings_file:
                self.window_size = int(settings_file["window_size"])
        except Exception as _ex:
            print(f"Real time filter settings read error :: incorrect window_size {settings_file['window_size']}")
            self.window_size = 13

        try:
            if "k_arg" in settings_file:
                self.k_arg = int(settings_file["k_arg"])
        except Exception as _ex:
            print(f"Real time filter settings read error :: incorrect k_arg {settings_file['k_arg']}")
            self.k_arg = 0.09

        try:
            if "kalman_error" in settings_file:
                self.kalman_error = int(settings_file["kalman_error"])
        except Exception as _ex:
            print(f"Real time filter settings read error :: incorrect kalman_error {settings_file['kalman_error']}")
            self.kalman_error = 0.8

        self.clean_up()

    def save_settings(self, settings_file: str) -> None:
        with open(settings_file, "wt") as output:
            print(self, file=output)


def noise_signal(t) -> float:
    return math.sin(t) + random.uniform(-0.1, 0.1) + random.uniform(-1, 1) * random.uniform(-1, 1)


def filter_test():
    _filter = RealTimeFilter()
    x = list(np.linspace(0, np.pi * 4, 1024))
    y = [noise_signal(t) for t in x]
    _filter.mode = 1
    mid_filter = [_filter.filter(val) for val in y]
    print(_filter)
    _filter.mode = 0
    ra_filter = [_filter.filter(val) for val in mid_filter]
    _filter.mode = 2
    kalman_filter = [_filter.filter(val) for val in y]
    print(_filter)
    fig = plt.figure()
    plt.plot(x, y, 'r')
    plt.plot(x, ra_filter, 'g')
    plt.plot(x, mid_filter, 'b')
    plt.plot(x, kalman_filter, 'k')
    plt.show()


def buffer_test():
    buffer = CircBuffer(5)
    buffer.append(1.0)
    buffer.append(2.0)
    buffer.append(3.0)
    buffer.append(4.0)
    buffer.append(5.0)
    print(buffer)
    buffer.append(6.0)
    buffer.append(7.0)
    print(buffer)
    buffer.append(8.0)
    buffer.append(9.0)
    print(buffer)
    buffer.append(10.0)
    print(buffer)


if __name__ == "__main__":
    buffer_test()
    filter_test()

