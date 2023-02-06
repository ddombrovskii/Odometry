import math
import random
from typing import Tuple, List

import matplotlib.pyplot as plt
from cgeo import Vec3, Mat4, rot_m_to_euler_angles
from cgeo.filtering import RealTimeFilter

filter_1 = RealTimeFilter()
filter_1.mode = 1
filter_1.window_size = 33
filter_1.kalman_error = 0.9999
filter_1.k_arg = 0.1

filter_2 = RealTimeFilter()
filter_2.mode = 1
filter_2.window_size = 33
filter_2.kalman_error = 0.9999
filter_2.k_arg = 0.1


def acccel_x(t: float, step: float = 10, width: float = .5) -> float:
    amp = 10.0
    curv =  math.exp(-(t - 20 - 1.0 * step) ** 2 / width ** 2) * amp +\
           -math.exp(-(t - 20 - 2.0 * step) ** 2 / width ** 2) * amp +\
           -math.exp(-(t - 20 - 3.0 * step) ** 2 / width ** 2) * amp +\
            math.exp(-(t - 20 - 4.0 * step) ** 2 / width ** 2) * amp

    if abs(curv) < 1e-12:
        return 0.0 + random.uniform(-0.1, 0.1)
    return curv + random.uniform(-0.1, 0.1)


def acccel_z(t: float, step: float = 10, width: float = .5) -> float:
   return acccel_x(t + 10)


def linear_movement(t0: float = 0.0, t1: float = 80.0, n_steps: int = 10000) -> \
        Tuple[List[float], List[float], List[float], List[float], List[float], List[float], List[float]]:
    dt = (t1 - t0) / (n_steps - 1)
    a = []
    a_t = []
    v = []
    v_t = []
    s = []
    s_t = []
    t = []
    for i in range(n_steps):
        t.append(t0 + i * dt )
        a.append(filter_1.filter(acccel_z(t[-1])))
        v.append(v[-1] + a[-1] * dt) if len(v) != 0 else v.append(0.0)
        s.append(s[-1] + v[-1] * dt) if len(s) != 0 else s.append(0.0)
        a_t.append(filter_2.filter(acccel_x(t[-1])))
        v_t.append(v_t[-1] + a_t[-1] * dt) if len(v_t) != 0 else v_t.append(0.0)
        s_t.append(s_t[-1] + v_t[-1] * dt) if len(s_t) != 0 else s_t.append(0.0)

    return t, a, v, s, a_t, v_t, s_t


def points_line():
    x = [0.0, 1.0, 1.0, 2.0, 2.0, 1.0, 1.0, 0.0, 0.0]
    y = [0.0, 0.0, 1.0, 1.0, 2.0, 2.0, 1.0, 1.0, 0.0]
    plt.plot(x, y, 'r')
    plt.show()


def orientation_sim():
    accel = Vec3(1, -9, 3).normalized() * 9.81

    ey = accel.normalized()

    ex = Vec3.cross(ey, Vec3(0, 0, 1))

    ez = Vec3.cross(ex, ey)

    transform = Mat4(ex.x, ey.x, ez.x, 0.0,
                     ex.y, ey.y, ez.y, 0.0,
                     ex.z, ey.z, ez.z, 0.0,
                     0.0, 0.0, 0.0, 1.0)

    # print(transform)

    #  print(accel)

    accel_ = Vec3(ex.x * accel.x + ex.y * accel.y + ex.z * accel.z,
                  ey.x * accel.x + ey.y * accel.y + ey.z * accel.z,
                  ez.x * accel.x + ez.y * accel.y + ez.z * accel.z)
    
    #  print(accel_)

    angles = rot_m_to_euler_angles(transform)

    to_deg = 1.0/3.1415 * 180

    print(angles * to_deg)

    fast_accel = Vec3(
        90 + to_deg * math.atan2(accel.z, accel.z),
        90 + to_deg * math.atan2(accel.y, accel.z),
        90 + to_deg * math.atan2(accel.y, accel.x))

    print(fast_accel)


if __name__ == "__main__":
    n_points = 1000
    dt = 1.0 / (n_points - 1)
    t = [i * dt for i in range(n_points)]
    x_ = 0.0
    x = []
    x_curr = 0
    x_prev = 0
    for ti in t:
        x_curr = ti
        x_ += (x_prev + x_curr) * dt * 0.5
        x_prev = x_curr
        x.append(x_)

    plt.plot(t, x)
    plt.show()
    exit()

    orientation_sim()
    exit()

    t, a, v, s, a_t, v_t, s_t = linear_movement()

    _figure, _ax = plt.subplots(1, 4)
    
    _ax[0].plot(t, a, 'r')
    _ax[0].plot(t, a_t, 'g')
    _ax[0].legend([r'$a$', r'$a_t$'], loc='upper left')
    _ax[0].set_xlabel("$t,[sec]$")
    _ax[0].set_ylabel("$a(t),[{m} / {sec}^2]$")
    _ax[0].set_title("accelerations")

    _ax[1].plot(t, v, 'r')
    _ax[1].plot(t, v_t, 'g')
    _ax[1].legend([r'$v$', r'$v_t$'], loc='upper left')
    _ax[1].set_xlabel("$t,[sec]$")
    _ax[1].set_ylabel("$v(t),[{m} / {sec}]$")
    _ax[1].set_title("velocities")

    _ax[2].plot(t, s, 'r')
    _ax[2].plot(t, s_t, 'g')
    _ax[2].legend([r'$s$', r'$s_t$'], loc='upper left')
    _ax[2].set_xlabel("$t,[sec]$")
    _ax[2].set_ylabel("$s(t),[{m}]$")
    _ax[2].set_title("trajectories")

    _ax[3].plot(s, s_t, 'k')
    _ax[3].legend([r'$s$', r'$s_t$'], loc='upper left')
    _ax[3].set_xlabel("$t,[sec]$")
    _ax[3].set_ylabel("$s(t),[{m}]$")
    _ax[3].set_title("trajectories")

    #plt.plot(t, v_t,   'g')
    # plt.plot(t, s_t,   'b')
    #plt.plot(s, s_t, 'b')
    #plt.plot(s, s_t,'r')
    plt.show()