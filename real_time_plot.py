from typing import Tuple, List, Callable
import matplotlib.pyplot as plt
import numpy as np
import time


class LoopTimer:
    """
    Интервальный таймер, который можно использоватьв вконтнксте with
    """
    __slots__ = "__timeout", "__loop_time", "__time"

    def __init__(self, timeout: float = 1.0):
        if timeout < 0:
            self.__timeout = 1.0
        else:
            self.__timeout = timeout
        self.__loop_time: float = 0.0
        self.__time: float = 0.0

    def __str__(self):
        return f"{{\n" \
               f"\t\"timeout\":        {self.timeout:-1.3f},\n" \
               f"\t\"time\":           {self.time:-1.3f},\n" \
               f"\t\"last_loop_time\": {self.last_loop_time:-1.3f}\n" \
               f"}}"

    def __enter__(self):
        self.__loop_time = time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__loop_time = time.perf_counter() - self.__loop_time
        if self.__loop_time < self.__timeout:
            time.sleep(self.__timeout - self.__loop_time)
            self.__time += self.__timeout
        self.__time += self.__loop_time

    @property
    def time(self) -> float:
        return self.__time

    @property
    def last_loop_time(self) -> float:
        return self.__loop_time

    @property
    def timeout(self) -> float:
        return self.__timeout

    @timeout.setter
    def timeout(self, val: float) -> None:
        if val < 0.0:
            return
        self.__timeout = val


class PlotAnimator:
    """
    Анимированный граффик на три кривые
    """
    def __init__(self, fig_title: str = "figure"):
        plt.ion()
        self._buffer_cap = 128
        self._figure, self._ax = plt.subplots()
        self._figure.suptitle(fig_title, fontsize=16)
        self._line_1, = self._ax.plot([], [], 'r')
        self._line_2, = self._ax.plot([], [], 'g')
        self._line_3, = self._ax.plot([], [], 'b')
        self._ax.legend(['$a_{x}$', '$a_{y}$', '$a_{z}$'], loc='upper left')
        self._ax.set_xlabel("$t,[sec]$")
        self._ax.set_ylabel("$a(t),[{m} / {sec^{2}}]$")
        self._ax.set_autoscaley_on(True)
        self._ax.grid()
        self._t_data: List[float] = []
        self._x_data: List[float] = []
        self._y_data: List[float] = []
        self._z_data: List[float] = []
        self._src: Callable[..., Tuple[float, float, float]] = lambda: (-1.0, 0.0, 1.0)
        self._timer = LoopTimer()
        self._timer.timeout = 10.0 / self._buffer_cap

    def __call__(self, src: Callable[..., Tuple[float, float, float]] = None):

        if src is not None:
            self._src = src

        while plt.fignum_exists(self._figure.number):
            with self._timer:
                self._read_src(self._timer.time)
                self._update_plot(self._t_data,
                                  self._x_data,
                                  self._y_data,
                                  self._z_data)

    def _update_plot(self, t_data: List[float], x_data: List[float], y_data: List[float], z_data: List[float]):
        self._line_1.set_xdata(t_data)
        self._line_1.set_ydata(x_data)

        self._line_2.set_xdata(t_data)
        self._line_2.set_ydata(y_data)

        self._line_3.set_xdata(t_data)
        self._line_3.set_ydata(z_data)

        self._ax.relim()
        self._ax.autoscale_view()

        # self._figure.canvas.draw()
        self._figure.canvas.flush_events()

    def _read_src(self, _curr_time: float):
        if self._src is None:
            return False
        self._t_data.append(_curr_time)
        x, y, z = self._src()
        self._x_data.append(x)
        self._y_data.append(y)
        self._z_data.append(z)
        if len(self._t_data) > self._buffer_cap:
            del self._x_data[0]
            del self._y_data[0]
            del self._z_data[0]
            del self._t_data[0]
        return True

    @property
    def axis(self):
        return self._ax

    @property
    def figure(self):
        return self._figure

    @property
    def x_label(self) -> str:
        return self._ax.get_xlabel()

    @x_label.setter
    def x_label(self, label: str) -> None:
        self._ax.set_xlabel(label)

    @property
    def y_label(self) -> str:
        return self._ax.get_ylabel()

    @y_label.setter
    def y_label(self, label: str) -> None:
        self._ax.set_ylabel(label)


if __name__ == "__main__":
    def cos_data() -> Tuple[float, float, float]:
        t = time.perf_counter()
        return np.cos(t), np.cos(t + 0.5 * np.pi), np.cos(t + np.pi)

    d = PlotAnimator()
    d(cos_data)
