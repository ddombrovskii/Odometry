from Utilities.loop_timer import LoopTimer
from typing import Tuple, List, Callable
from matplotlib import pyplot as plt
import numpy as np
import time


def _color_code(red: int, green: int, blue: int) -> str:
    return f"#{''.join('{:02X}'.format(max(min(a, 255), 0)) for a in (red, green, blue))}"


def _color_map_quad(map_amount: int = 3) -> List[str]:
    colors = []
    dx = 1.0 / (map_amount - 1)
    for i in range(map_amount):
        xi = i * dx
        colors.append(_color_code(int(255 * max(1.0 - (2.0 * xi - 1.0) ** 2, 0)),
                                  int(255 * max(1.0 - (2.0 * xi - 2.0) ** 2, 0)),
                                  int(255 * max(1.0 - (2.0 * xi - 0.0) ** 2, 0))))
    return colors


def _color_map_lin(map_amount: int = 3) -> List[str]:
    colors = []
    dx = 1.0 / (map_amount - 1)
    for i in range(map_amount):
        xi = i * dx
        colors.append(_color_code(int(255 * max(1.0 - 2.0 * xi, 0.0)),
                                  int(255 * (1.0 - abs(2.0 * xi - 1.0))),
                                  int(255 * max(2.0 * xi - 1, 0.0))))
    return colors


class AnimatedPlot:
    """
    Анимированный график на три кривые
    """
    def __init__(self, n_lines: int = 3, fig_title: str = "figure"):
        plt.ion()
        self._figure, self._ax = plt.subplots()
        self._figure.suptitle(fig_title, fontsize=16)
        self._buffer_cap: int = 128
        cmap = _color_map_lin(n_lines)
        self._lines = [self._ax.plot([], [], color=f"{c}")[0] for c in cmap]
        self._ax.legend([f'$line_{i}$' for i in range(n_lines)], loc='upper left')
        self._ax.set_xlabel("$t,[sec]$")
        self._ax.set_ylabel("$a(t),[{m} / {sec^{2}}]$")
        self._ax.set_autoscaley_on(True)
        self._ax.grid()
        self._t_data: List[float] = []
        self._values_lines: List[List[float]] = [[]for _ in range(n_lines)]
        self._src: Callable[..., Tuple[float, ...]] = lambda: (-1.0, 0.0, 1.0)
        self._timer = LoopTimer()
        self._time = 0.0
        self._timer.timeout = 12.5 / self._buffer_cap

    def __call__(self, src: Callable[..., Tuple[float, ...]] = None):
        if src is not None:
            self._src = src
        while plt.fignum_exists(self._figure.number):
            with self._timer:
                self._time += self._timer.timeout
                self._read_src(self._time)
                self._update_plot()

    def _update_plot(self):
        for line, line_vals in zip(self._lines, self._values_lines):
            line.set_xdata(self._t_data)
            line.set_ydata(line_vals)
        self._ax.relim()
        self._ax.autoscale_view()
        # self._figure.canvas.draw()
        self._figure.canvas.flush_events()

    def _read_src(self, _curr_time: float):
        if self._src is None:
            return False
        self._t_data.append(_curr_time)
        try:
            args = self._src()
        except Exception as _ex:
            print(f"src function call error:\n{_ex.args}")
            args = [0 for _ in range(len(self._lines))]

        for value, line in zip(args, self._values_lines):
            line.append(value)

        if len(self._t_data) > self._buffer_cap:
            del self._t_data[0]
            for line in self._values_lines:
                del line[0]

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

    @property
    def label(self) -> List[str]:
        # TODO доделать
        return []

    @label.setter
    def label(self, labels: List[str]) -> None:
        self._ax.legend(labels, loc='upper left')


if __name__ == "__main__":
    n = 1000
    dx = 1 / (n - 1)
    x = [dx * i for i in range(1000)]
    """
    r = [max(1.0 - (2.0 * xi - 1.0) ** 2, 0) for xi in x]
    g = [max(1.0 - (2.0 * xi - 2.0) ** 2, 0) for xi in x]
    b = [max(1.0 - (2.0 * xi - 0.0) ** 2, 0) for xi in x]
    """
    r = [max(-2.0 * xi + 1, 0.0) for xi in x]
    g = [1 - abs((2.0 * xi - 1.0)) for xi in x]
    b = [max(2.0 * xi - 1, 0.0) for xi in x]

    plt.plot(x, r, 'r')
    plt.plot(x, g, 'g')
    plt.plot(x, b, 'b')
    plt.show()

    def cos_data() -> Tuple[float, float, float, float, float]:

        t = time.perf_counter()

        return np.cos(t), np.cos(t + 0.333 * np.pi), np.cos(t + 0.666 * np.pi),\
               np.cos(t + 0.666 * np.pi) * 0.4, np.cos(t + 0.666 * np.pi) * 0.1

    d = AnimatedPlot(5)

    d(cos_data)
