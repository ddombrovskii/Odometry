from accelerometer_recording import read_accel_log, ang_velocities, time_values, accelerations, read_imu_log
from matplotlib import pyplot as plt
from typing import Tuple
import numpy as np
import math


# TODO remove


def comp_filter(path: str, k: float, t0: float, t1: float):
    def angles_fast(_ax, _ay, _az) -> Tuple[float, float, float]:
        return math.pi + math.atan2(_az, _az),\
               math.pi + math.atan2(_ay, _az),\
               math.pi + math.atan2(_ay, _ax)
    _log = read_imu_log(path)
    ax, ay, az = accelerations(_log)
    ang_vx, ang_vy, ang_vz = ang_velocities(_log)
    t_vals = []
    
    f_ang_x = []
    f_ang_y = []
    f_ang_z = []
    
    a_ang_x = []
    a_ang_y = []
    a_ang_z = []
    
    r_ang_x = []
    r_ang_y = []
    r_ang_z = []

    for index in range(min((len(ax), len(ay), len(az), len(ang_vx), len(ang_vy), len(ang_vz)))):
        _ax, _ay, _az = angles_fast(ax[index], ay[index], az[index])
        dt = _log.way_points[index].dtime
        t_vals.append(_log.way_points[index].time)
        
        a_ang_x.append(_ax)
        a_ang_y.append(_ay)
        a_ang_z.append(_az)

        r_ang_x.append((r_ang_x[-1] + ang_vx[index] * dt))if len(r_ang_x) != 0 else r_ang_x.append(0.0)
        r_ang_y.append((r_ang_y[-1] + ang_vy[index] * dt))if len(r_ang_y) != 0 else r_ang_y.append(0.0)
        r_ang_z.append((r_ang_z[-1] + ang_vz[index] * dt))if len(r_ang_z) != 0 else r_ang_z.append(0.0)

        f_ang_x.append((f_ang_x[-1] + ang_vx[index] * dt) * k + _ax * (1.0 - k))if len(f_ang_x) != 0 else f_ang_x.append(0.0)
        f_ang_y.append((f_ang_y[-1] + ang_vy[index] * dt) * k + _ay * (1.0 - k))if len(f_ang_y) != 0 else f_ang_y.append(0.0)
        f_ang_z.append((f_ang_z[-1] + ang_vz[index] * dt) * k + _az * (1.0 - k))if len(f_ang_z) != 0 else f_ang_z.append(0.0)

    #_figure, _ax = plt.subplots(3, 1)
    #_ax[0].plot(t_vals, a_ang_x, 'r')
    ##_ax[0].plot(t_vals, r_ang_x, 'g')
    ##_ax[0].plot(t_vals, f_ang_x, 'b')
    #_ax[0].legend(['accel angle', 'integral angle', 'comp angle'], loc='upper left')
    #_ax[0].set_xlabel("$t,[sec]$")
    #_ax[0].set_ylabel("$ax,[{m}/{sec^2}]$")
    #_ax[0].set_title("x - acceleration")
    ##########################
    #_ax[1].plot(t_vals, a_ang_y, 'r')
    #_ax[1].plot(t_vals, r_ang_y, 'g')
    #_ax[1].plot(t_vals, f_ang_y, 'b')
    #_ax[1].legend(['accel angle', 'integral angle', 'comp angle'], loc='upper left')
    #_ax[1].set_xlabel("$t,[sec]$")
    #_ax[1].set_ylabel("$ay,[{m}/{sec^2}]$")
    #_ax[1].set_title("y - acceleration")
    ##########################
    #_ax[2].plot(t_vals, a_ang_z, 'r')
    #_ax[2].plot(t_vals, r_ang_z, 'g')
    #_ax[2].plot(t_vals, f_ang_z, 'b')
    #_ax[2].legend(['accel angle', 'integral angle', 'comp angle'], loc='upper left')
    #_ax[2].set_xlabel("$t,[sec]$")
    #_ax[2].set_ylabel("$az,[{m}/{sec^2}]$")
    #_ax[2].set_title("z - acceleration")
    ##########################
    # plt.show()
    sx = [0.0]
    sz = [0.0]
    t = 0
    dt = [v.dtime for v in _log.way_points]
    for index in range(len(dt)):
        if t > t1:
            break
        t +=dt[index]
        if t < t0:
            continue
        sx.append(sx[-1] + ax[index] * math.sin(r_ang_y[index] * 1.0) * dt[index])
        sz.append(sz[-1] - ax[index] * math.cos(r_ang_y[index] * 1.0) * dt[index])


    fig, axs = plt.subplots(1)
    axs.plot(sx, sz)
    axs.set_aspect('equal', 'box')
    axs.set_xlabel("x, [m]")
    axs.set_ylabel("z, [m]$")
    axs.set_title("building path")
    plt.show()


    # plt.plot(f_ang_z, f_ang_y)
    # plt.show()




if __name__ == "__main__":

    comp_filter('building_walk_drunk.json', 1.0, 35, 140)
    comp_filter('building_walk_straight.json', 1.0, 10, 90)
    comp_filter('building_way_2.json', 1.0, 15, 120)
    comp_filter('building_way_3.json', 1.0, 15, 130)
    # _log = read_record('building_way.json')
   # ax, ay, az = accelerations(_log)
   # plt.plot(ax, 'r')
   # plt.plot(ay, 'g')
   # plt.plot(az, 'b')
   # plt.show()

