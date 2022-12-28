import time
from threading import Thread

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple, Union, List, Callable, Dict
"""

fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'r')

print(type(ln))

steps = 128

x_vals = np.linspace(0, 2 * np.pi, steps)

x_cntr = 0

dx = 0.0


def init():
    ax.set_xlim(0, 2 * np.pi)
    ax.set_ylim(-1, 1)
    return ln,


def update(_):
    global x_cntr
    global dx
    global ax
    xdata.append(dx + x_vals[x_cntr])
    ydata.append(np.sin(dx + x_vals[x_cntr]))
    ax.set_xlim(xdata[0], xdata[-1])
    if len(xdata) == steps + 1:
        del xdata[0]
        del ydata[0]
    x_cntr += 1
    if x_cntr == steps:
        dx += x_vals[-1]
        print(f"dx: {dx}")
    x_cntr %= steps
    ln.set_data(xdata, ydata)
    return ln,


ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=1000.0 * 2 * np.pi/steps)
plt.show()
"""


class Monitor:

    __cmap = {'r': 'r',
              'g': 'g',
              'b': 'b',
              'k': 'k'}

    def __init__(self, fig_title: str = "figure",
                 fig_title_font_size: int = 16,
                 sub_plots: Union[Tuple[int, int], int] = None,
                 sub_plots_names: Union[List[str], str] = None,
                 sub_plots_x_labels: Union[List[str], str] = None,
                 sub_plots_y_labels: Union[List[str], str] = None):

        self._figure = plt.figure()
        self._figure.suptitle(fig_title, fontsize=fig_title_font_size)
        self._axis = None
        self._data_sources: Dict[int, Callable[[None], Tuple[float, ...]]] = {}
        self._data_cashed: List[List[List[float]]] = []
        self._plot_lines: Dict[int, list] = {}
        self._data_cash_size = 128
        self._animator = FuncAnimation(self._figure, self.update_data, blit=True,
                                       interval=1000.0 * 2 * np.pi / (self._data_cash_size - 1))

        if sub_plots is None:
            self._axis = self.figure.subplots(1, 1)  # , constrained_layout=True)

        if isinstance(sub_plots, int):
            self._axis = self.figure.subplots(sub_plots, 1)  # , constrained_layout=True)

        if isinstance(sub_plots, tuple):
            self._axis = self.figure.subplots(sub_plots[0], sub_plots[1])  # , constrained_layout=True)

        self.axis_titles = sub_plots_names
        self.x_labels = sub_plots_x_labels
        self.y_labels = sub_plots_y_labels

    def _read_data_src(self, axis_id: int):
        src = self._data_sources[axis_id]
        data = self._data_cashed[axis_id]
        lines = self._plot_lines[axis_id]
        src_data = src(...)

        if len(data) == 0:
            for data_i in src_data:
                data.append([])
                data[-1].append(data_i)
            return

        for src_i, data_i in zip(src_data, data):
            data_i.append(src_i)
            if len(data_i) > self._data_cash_size:
                del data_i[0]

        for line_id, line in enumerate(lines):
            line.set_data(None, data[line_id])  # TODO xdata in line.set_data()...

    def update_data(self) -> None:
        for src_id in self._data_sources:
            self._read_data_src(src_id)

    def set_data_source(self, axis_id: int, src: Callable[..., Tuple[float, ...]]) -> bool:
        if axis_id >= self._axis.size:
            return False
        if axis_id < 0:
            return False
        # _ax = self._axis.flat[axis_id]
        if axis_id in self._data_sources:
            self._data_sources[axis_id] = src
            return True
        self._data_sources.update({axis_id: src})
        self._plot_lines.update({axis_id: self._axis.flat[axis_id].plot([], [],)})
        return True

    @property
    def axis_titles(self) -> List[str]:
        return [_ax.get_title() for _ax in self._axis.flat]

    @axis_titles.setter
    def axis_titles(self, titles: Union[List[str], str]) -> None:
        if titles is None:
            for _ax_id, _ax in enumerate(self._axis.flat):
                _ax.set_title(f'')
            return

        if isinstance(titles, str):
            for _ax_id, _ax in enumerate(self._axis.flat):
                _ax.set_title(f' {_ax_id}'.join(titles))
            return

        if isinstance(titles, list):
            for _ax, _ax_name in zip(self._axis.flat, titles):
                _ax.set_title(_ax_name)

    @property
    def x_labels(self) -> List[str]:
        return [_ax.get_xlabel() for _ax in self._axis.flat]

    @property
    def y_labels(self) -> List[str]:
        return [_ax.get_ylabel() for _ax in self._axis.flat]

    @x_labels.setter
    def x_labels(self, labels: Union[List[str], str]) -> None:
        if labels is None:
            for _ax in self._axis.flat:
                _ax.set_xlabel('x')
            return

        if isinstance(labels, str):
            for _ax in self._axis.flat:
                _ax.set_xlabel(labels)
            return

        if isinstance(labels, list):
            for _ax, _ax_name in zip(self._axis.flat, labels):
                _ax.set_xlabel(_ax_name)

    @y_labels.setter
    def y_labels(self, labels: Union[List[str], str]) -> None:
        if labels is None:
            for _ax in self._axis.flat:
                _ax.set_ylabel('y')
            return

        if isinstance(labels, str):
            for _ax in self._axis.flat:
                _ax.set_ylabel(labels)
            return

        if isinstance(labels, list):
            for _ax, _ax_name in zip(self._axis.flat, labels):
                _ax.set_ylabel(_ax_name)

    @property
    def axis(self):
        for _ax in self._axis.flat:
            yield _ax

    @property
    def figure(self):
        return self._figure

    def start(self) -> None:
        # self._figure.show()
        plt.show()


def cos_1(t: float) -> float:
    return np.sin(t)


def cos_2(t: float) -> float:
    return np.sin(t + np.pi * 0.5)


def cos_3(t: float) -> float:
    return np.sin(t + np.pi)


def cos_data() -> Tuple[float, float, float]:
    t = time.perf_counter()
    return cos_1(t), cos_2(t), cos_3(t)


class Animator(Thread):
    def __init__(self):
        super().__init__()
        self.time_out = 0.1
        self.animation_frame = None
        self.life_time = 10
        self._time_alive = 0.0

    def run(self):
        while True:
            if self._time_alive >= self.life_time:
                break

            if self.animation_frame is None:
                time.sleep(self.time_out)
                self._time_alive += self.time_out
                continue

            t = time.perf_counter()
            self.animation_frame()
            t = time.perf_counter() - t

            if t < self.time_out:
                time.sleep(self.time_out - t)
                self._time_alive += self.time_out
                continue

            self._time_alive += t

plt.ion()
class DynamicUpdate():
    #Suppose we know the x range
    min_x = 0
    max_x = 10

    def on_launch(self):
        #Set up plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[], 'o')
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        self.ax.set_xlim(self.min_x, self.max_x)
        #Other stuff
        self.ax.grid()
        ...

    def on_running(self, xdata, ydata):
        #Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    #Example
    def __call__(self):
        import numpy as np
        import time
        self.on_launch()
        xdata = []
        ydata = []
        for x in np.arange(0, 10, 0.05):
            xdata.append(x)
            ydata.append(np.exp(-x**2)+10*np.exp(-(x-7)**2))
            self.on_running(xdata, ydata)
            time.sleep(0.1)
        return xdata, ydata


if __name__ == "__main__":
    d = DynamicUpdate()
    d()
    exit(0)

    fig, ax = plt.subplots()

    t_start = time.perf_counter()
    t_vals = []

    x_vals = []
    y_vals = []
    z_vals = []

    x_vals_line, = ax.plot([], [], 'r')
    y_vals_line, = ax.plot([], [], 'g')
    z_vals_line, = ax.plot([], [], 'b')

    data_cap = 128

    def plot_3graphs():
        x, y, z = cos_data()
        x_vals.append(x)
        y_vals.append(y)
        z_vals.append(z)
        t_vals.append(time.perf_counter() - t_start)

        ax.set_xlim(t_vals[0], t_vals[-1])
        ax.set_ylim(-1, 1)

        if len(x_vals) > data_cap:
            del x_vals[0]
            del y_vals[0]
            del z_vals[0]
            del t_vals[0]
        x_vals_line.set_data(t_vals, x_vals)
        y_vals_line.set_data(t_vals, y_vals)
        z_vals_line.set_data(t_vals, z_vals)
        #Need both of these in order to rescale
        ax.relim()
        ax.autoscale_view()
        #We need to draw *and* flush
        fig.canvas.draw()
        fig.canvas.flush_events()

    animator = Animator()
    animator.animation_frame = plot_3graphs
    print("kurva")
    animator.start()
    print("kurva")
    plt.show()












