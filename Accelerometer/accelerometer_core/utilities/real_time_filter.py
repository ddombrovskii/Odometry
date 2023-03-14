# from accelerometer_core.utilities.circ_buffer import CircBuffer
# from circ_buffer import CircBuffer
from .circ_buffer import CircBuffer
from typing import Callable
import math


def _clamp(val: float, min_: float, max_: float) -> float:
    """
    :param val: значение
    :param min_: минимальная граница
    :param max_: максимальная граница
    :return: возвращает указанное значение val в границах от min до max
    """
    if val < min_:
        return min_
    if val > max_:
        return max_
    return val


class RealTimeFilter:
    def __init__(self):
        self.__mode = 0
        # 0 running average
        # 1 median
        # 2 kalman
        self._window_size: int = 13
        self._window_values: CircBuffer = CircBuffer(self.window_size)
        self._prev_value:    float = 0.0
        self._curr_value:    float = 0.0
        self._k_arg:         float = 0.08
        self._err_measure:   float = 0.9
        self._err_estimate:  float = 0.333
        self._last_estimate: float = 0.0
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
        self._err_estimate = 0.333
        self._last_estimate = 0.0
        self._prev_value = 0.0
        self._curr_value = 0.0
        self._window_values.clear()

    @property
    def window_size(self) -> int:
        return self._window_size

    @window_size.setter
    def window_size(self, val: int) -> None:
        if val % 2 == 0:
            self._window_size = 1 + math.fabs(val)
            self._window_values = CircBuffer(self.window_size)
            return
        self._window_size = int(math.fabs(val))
        self._window_values = CircBuffer(self.window_size)

    @property
    def mode(self) -> int:
        return self._mode

    @mode.setter
    def mode(self, val: int) -> None:
        if val == 0:
            self._mode = int(val)
            self._filter_function = self._run_avg_filter
            return
        if val == 1:
            self._mode = int(val)
            self._filter_function = self._mid_filter
            return
        if val == 2:
            self._mode = int(val)
            self._filter_function = self._kalman_filter
            return

    @property
    def k_arg(self) -> float:
        return self._k_arg

    @k_arg.setter
    def k_arg(self, val: float) -> None:
        self._k_arg = _clamp(val, 0.0, 1.0)

    @property
    def kalman_error(self) -> float:
        return self._err_measure

    @kalman_error.setter
    def kalman_error(self, val: float) -> None:
        self._err_measure = _clamp(val, 0.0, 1.0)

    def _run_avg_filter(self, value: float) -> float:
        self._prev_value = self._curr_value
        self._curr_value += (value - self._curr_value) * self._k_arg
        return self._curr_value

    def _mid_filter(self, value: float) -> float:
        self._window_values.append(value)
        self._prev_value = self._curr_value
        self._curr_value = self._window_values.sorted[self._window_values.capacity // 2]
        return self._curr_value

    def _kalman_filter(self, value: float) -> float:
        _kalman_gain: float = self._err_estimate / (self._err_estimate + self._err_measure)
        _current_estimate: float = self._last_estimate + _kalman_gain * (value - self._last_estimate)
        self._err_estimate = (1.0 - _kalman_gain) * self._err_estimate + \
                             math.fabs(self._last_estimate - _current_estimate) * self._k_arg
        self._prev_value = self._last_estimate
        self._last_estimate = _current_estimate
        return self._last_estimate

    def filter(self, value: float) -> float:
        return self._filter_function(value)

    def load_settings(self, settings_file):
        try:
            if "mode" in settings_file:
                self.mode = int(settings_file["mode"])
        except RuntimeWarning as _ex:
            print(f"Real time filter settings read error :: incorrect mode {settings_file['mode']}")
            self.mode = 0

        try:
            if "window_size" in settings_file:
                self.window_size = int(settings_file["window_size"])
        except RuntimeWarning as _ex:
            print(f"Real time filter settings read error :: incorrect window_size {settings_file['window_size']}")
            self.window_size = 13

        try:
            if "k_arg" in settings_file:
                self.k_arg = float(settings_file["k_arg"])
        except RuntimeWarning as _ex:
            print(f"Real time filter settings read error :: incorrect k_arg {settings_file['k_arg']}")
            self.k_arg = 0.09

        try:
            if "kalman_error" in settings_file:
                self.kalman_error = float(settings_file["kalman_error"])
        except RuntimeWarning as _ex:
            print(f"Real time filter settings read error :: incorrect kalman_error {settings_file['kalman_error']}")
            self.kalman_error = 0.8

        self.clean_up()

    def save_settings(self, settings_file: str) -> None:
        with open(settings_file, "wt") as output:
            print(self, file=output)
