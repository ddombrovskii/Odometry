from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'r')

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