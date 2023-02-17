from accelerometer_recording import read_accel_log, ang_velocities, time_values, accelerations, read_imu_log
from matplotlib import pyplot as plt
from typing import Tuple
import numpy as np
import math

from mpu6050.math.quaternion_math import *


def read_csv(path: str):
    ax = []
    ay = []
    az = []

    gx = []
    gy = []
    gz = []

    mx = []
    my = []
    mz = []
    with open(path) as in_file:
        for line in in_file:
            if len(line) == 0:
                continue
            try:
                line = line.split(',')
                #if len(line) == 10:
                #    continue
                ax.append(float(line[4]))
                ay.append(float(line[5]))
                az.append(float(line[6]))

                gx.append(float(line[1]))
                gy.append(float(line[2]))
                gz.append(float(line[3]))

                mx.append(float(line[7]))
                my.append(float(line[8]))
                mz.append(float(line[9]))
            except:
                continue
    return (ax, ay, az), (gx, gy, gz), (mx, my, mz)
            


def comp_filter(path: str):
    # _log = read_imu_log(path)
    # ax, ay, az = accelerations(_log)
    # ang_vx, ang_vy, ang_vz = ang_velocities(_log)
    (ax, ay, az), (ang_vx, ang_vy, ang_vz), (mx, my, mz) = read_csv("math/movement_test.csv")
     

    t_vals = [0.0]
    accel_0 = [2.8, 9.31, 1.66]
    # accel_0 = [-1.46, 9.4, 0.52]  # reverced

    accel_x = [0.0]
    accel_y = [0.0]
    accel_z = [0.0]

    velocity_x = [0.0]
    velocity_y = [0.0]
    velocity_z = [0.0]

    path_x = [0.0]
    path_y = [0.0]
    path_z = [0.0]

    accel = (ax[50], ay[50], az[50])

    cur_dir = (mx[50], my[50], mz[50])

    ex, ey, ez = build_rot_m(accel, cur_dir)  # строим базис для такой системы (это функция точно верная)
    # (орты базиса - столбцы матрицы поворота)
    start_q = rot_m_to_quaternion((ex[0], ey[0], ez[0], ex[1], ey[1], ez[1], ex[2], ey[2], ez[2]))

    start_angles = (0,0,0) #quaternion_to_euler(start_q)

    angle_x = [start_angles[0]]
    angle_y = [start_angles[1]]
    angle_z = [start_angles[2]]

    accel_x_q = [start_angles[0]]
    accel_y_q = [start_angles[1]]
    accel_z_q = [start_angles[2]]

    q_rot = quaternion_from_angles(start_angles[0], start_angles[1], start_angles[2])
    g_calib = quaternion_rot(accel, q_rot)

    # accel_0 = [2.8, 9.31, 1.66]
    curr_t = 0.0
    for index in range(min((len(ax), len(ay), len(az), len(ang_vx), len(ang_vy), len(ang_vz)))):
        # _ax, _ay, _az = angles_fast(ax[index], ay[index], az[index])
        dt = 0.01 # _log.way_points[index].dtime
        curr_t += dt
        # if curr_t < 1.0:
        #    continue

        t_vals.append(curr_t + dt)

        angle_x.append(angle_x[-1] + ang_vx[index] * dt)
        angle_y.append(angle_y[-1] + ang_vy[index] * dt)
        angle_z.append(angle_z[-1] + ang_vz[index] * dt)

        # angle_x[-1] %= math.pi
        # angle_y[-1] %= math.pi
        # angle_z[-1] %= math.pi
        # acceleration = (ax[index], ay[index], az[index])
        # ex, ey, ez = build_rot_m(acceleration)
        # #  строим базис для такой системы (это функция точно верная)
        # #  (орты базиса - столбцы матрицы поворота)
        # _q = rot_m_to_quaternion((ex[0], ey[0], ez[0],
        #                           ex[1], ey[1], ez[1],
        #                           ex[2], ey[2], ez[2]))
        # _angles = quaternion_to_euler(_q)
        acceleration = quaternion_rot((ax[index], ay[index], az[index]),
                                      quaternion_from_angles(angle_x[-1], angle_y[-1], angle_z[-1]))
        # angle_x.append(_angles[0])
        # angle_y.append(_angles[1])
        # angle_z.append(_angles[2])

        accel_x.append(acceleration[0])  # - g_calib[0])
        accel_y.append(acceleration[1])  # - g_calib[1])
        accel_z.append(acceleration[2])  # - g_calib[2])

        accel_x_q.append(ax[index])
        accel_y_q.append(ay[index])
        accel_z_q.append(az[index])

        velocity_x.append(velocity_x[-1] + accel_x[-1] * dt)
        velocity_y.append(velocity_y[-1] + accel_y[-1] * dt)
        velocity_z.append(velocity_z[-1] + accel_z[-1] * dt)

        path_x.append(path_x[-1] + velocity_x[-1] * dt)
        path_y.append(path_y[-1] + velocity_y[-1] * dt)
        path_z.append(path_z[-1] + velocity_z[-1] * dt)

        # cur_dir = direction((path_x[-1], path_y[-1], path_z[-1]), (path_x[-2], path_y[-2], path_z[-2]))
    # plt.show()
    sx = [0.0]
    sz = [0.0]
    t = 0

    fig, axs = plt.subplots(4)

    axs[0].plot(t_vals, accel_x, 'r')
    axs[0].plot(t_vals, accel_y, 'g')
    axs[0].plot(t_vals, accel_z, 'b')
    # axs[0].plot(t_vals, accel_x_q, ':r')
    # axs[0].plot(t_vals, accel_y_q, ':g')
    # axs[0].plot(t_vals, accel_z_q, ':b')
    # axs[0].set_aspect('equal', 'box')
    axs[0].set_xlabel("t, [sec]")
    axs[0].set_ylabel("$a(t), [m/sec^2]$")
    axs[0].set_title("accelerations")

    axs[1].plot(t_vals, angle_x, 'r')
    axs[1].plot(t_vals, angle_y, 'g')
    axs[1].plot(t_vals, angle_z, 'b')

    # axs[1].set_aspect('equal', 'box')
    axs[1].set_xlabel("t, [sec]")
    axs[1].set_ylabel("$angle, [rad]$")
    axs[1].set_title("angles")

    axs[2].plot(t_vals, velocity_x, 'r')
    axs[2].plot(t_vals, velocity_y, 'g')
    axs[2].plot(t_vals, velocity_z, 'b')
    # axs[2].set_aspect('equal', 'box')
    axs[2].set_xlabel("t, [sec]")
    axs[2].set_ylabel("$v(t), [m/sec]$")
    axs[2].set_title("velosities")

    # axs[3].plot(t_vals, path_x, 'r')
    # axs[3].plot(t_vals, path_y, 'g')
    axs[3].plot(t_vals, path_x, 'r')
    axs[3].plot(t_vals, path_y, 'g')
    axs[3].plot(t_vals, path_z, 'b')
    # axs[3].set_aspect('equal', 'box')
    axs[3].set_xlabel("t, [sec]")
    axs[3].set_ylabel("$S(t), [m]$")
    axs[3].set_title("building path")

    plt.show()


if __name__ == "__main__":
    comp_filter('building_walk_straight.json')#, 1.0)
    """
    Задача:
    Вектор (0, 1, 0)
    Кватернион из углов 45, 35, 25 градусов
    Повернуть вектор кватернионом и сделать обратное преобразование
    Задача работает нормально
    """
    deg_2_rad = math.pi / 180.0
    rad_2_deg = 180.0 / math.pi
    q_1 = quaternion_from_angles(45 * deg_2_rad, 35 * deg_2_rad, 25 * deg_2_rad)
    v = (0, 1, 0)
    v_ = quaternion_rot(v, q_1)
    print(f"v_rot    : {v_}")  # v_rot    : (0.34618861305875415, 0.8122618069191612, -0.46945095719241614)
    print(f"v_inv_rot: {quaternion_rot(v_, inv_quaternion(q_1))}")  # v_inv_rot: (1e-17, 1.0000000000000004, 0.0)
    angles = quaternion_to_euler(q_1)
    print(f"roll: {angles[0] * rad_2_deg}, pitch: {angles[1] * rad_2_deg}, yaw: {angles[2] * rad_2_deg}")  # (45,35,25)
    """
    Задача:
    Есть направление вектора eY и eZ. Построить ортонормированный базис, сохраняя направление eY
    Задача работает нормально
    """
    y_dir = (7.07, 7.07, 0)  # пусть это начальное ускорение в состоянии покоя
    z_dir = (0.0, 0.0, 1.0)
    q = quaternion_from_angles(0, 0, -45 * deg_2_rad)
    ex, ey, ez = quaternion_to_rot_m(q)  # совпадает с матрицей поворота на 45 градусов по оси Z
    print("quaternion to rot m")
    print(f"{ex[0]:>2.3f}, {ey[0]:>2.3f}, {ez[0]:>2.3f}\n"
          f"{ex[1]:>2.3f}, {ey[1]:>2.3f}, {ez[1]:>2.3f}\n"
          f"{ex[2]:>2.3f}, {ey[2]:>2.3f}, {ez[2]:>2.3f}\n")
    ex, ey, ez = build_rot_m(y_dir, z_dir)  # строим базис для такой системы (это функция точно верная)
    # (орты базиса - столбцы матрицы поворота)
    start_q = rot_m_to_quaternion((ex[0], ey[0], ez[0],
                                   ex[1], ey[1], ez[1],
                                   ex[2], ey[2], ez[2]))
    start_angles = quaternion_to_euler(start_q)  # quaternion_to_euler - работает корректно, см. задачу выше

    q_rot = quaternion_from_angles(start_angles[0], start_angles[1], start_angles[2])

    q_ex, q_ey, q_ez = quaternion_to_rot_m(q_rot)

    print("rot m from vectors")
    print(f"{ex[0]:>2.3f}, {ey[0]:>2.3f}, {ez[0]:>2.3f}\n"
          f"{ex[1]:>2.3f}, {ey[1]:>2.3f}, {ez[1]:>2.3f}\n"
          f"{ex[2]:>2.3f}, {ey[2]:>2.3f}, {ez[2]:>2.3f}\n")

    print("rot m from quaternion")
    print(f"{q_ex[0]:>2.3f}, {q_ey[0]:>2.3f}, {q_ez[0]:>2.3f}\n"
          f"{q_ex[1]:>2.3f}, {q_ey[1]:>2.3f}, {q_ez[1]:>2.3f}\n"
          f"{q_ex[2]:>2.3f}, {q_ey[2]:>2.3f}, {q_ez[2]:>2.3f}\n")
    # последние две матрицы должны совпасть

    # g_calib = quaternion_rot(accel_0, (q_rot))

    g_calib = (ex[0] * y_dir[0] + ex[1] * y_dir[1] + ex[2] * y_dir[2],
               ey[0] * y_dir[0] + ey[1] * y_dir[1] + ey[2] * y_dir[2],
               ez[0] * y_dir[0] + ez[1] * y_dir[1] + ez[2] * y_dir[2])

    print(g_calib)
    # q = quaternion(0.0, 0.0,  math.pi * 0.25)
    # ex, ey, ez = quaternion_to_rot_m(q)
    # q_ = rot_m_to_quaternion((ex[0], ey[0], ez[0],
    #                           ex[1], ey[1], ez[1],
    #                           ex[2], ey[2], ez[2]))
    # 
    # a = quaternion_to_euler(q)
    # v = (0, 10, 0)
    # print(f"q  : {q}")
    # print(f"q_ : {q_}")
    # print(f"a  : {a}")
    # 
    # vr = quaternion_rot(v, q)
    # print(f"qr   : {vr}")
    # ivr = quaternion_rot(vr, inv_quaternion(q))
    # print(f"qr^-1: {ivr}")

    #
    # comp_filter('building_walk_straight.json', 1.0)
    # comp_filter('building_way_2.json', 1.0, 15, 120)
    # comp_filter('building_way_3.json', 1.0, 15, 130)
    # _log = read_record('building_way.json')
# ax, ay, az = accelerations(_log)
# plt.plot(ax, 'r')
# plt.plot(ay, 'g')
# plt.plot(az, 'b')
# plt.show()
