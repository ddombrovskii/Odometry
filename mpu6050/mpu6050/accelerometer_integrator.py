from cgeo import Vec3, rot_m_to_euler_angles, Mat4

from accelerometer_recording import read_accel_log, ang_velocities, time_values, accelerations, read_imu_log
from matplotlib import pyplot as plt
from typing import Tuple
import numpy as np
import math

# TODO remove

Quaternion = Tuple[float, float, float, float]

Vector3 = Tuple[float, float, float]

Matrix3 = Tuple[float, float, float, float, float, float, float, float, float]


def quaternion(roll: float, pitch: float, yaw: float) -> Quaternion:
    # работает
    cr: float = math.cos(roll  * 0.5)
    sr: float = math.sin(roll  * 0.5)
    cp: float = math.cos(pitch * 0.5)
    sp: float = math.sin(pitch * 0.5)
    cy: float = math.cos(yaw   * 0.5)
    sy: float = math.sin(yaw   * 0.5)

    return cr * cp * cy + sr * sp * sy, \
           sr * cp * cy - cr * sp * sy, \
           cr * sp * cy + sr * cp * sy, \
           cr * cp * sy - sr * sp * cy


def inv_quaternion(q: Quaternion) -> Quaternion:
    # работает
    norm = 1.0 / math.sqrt(sum(v ** 2 for v in q))
    return q[0] * norm, -q[1] * norm, -q[2] * norm, -q[3] * norm


def quaternion_mul(q1: Quaternion, q2: Quaternion) -> Quaternion:
    # работает
    # qw, qx, qy, qz = q1
    # _qw, _qx, _qy, _qz = q2
    return q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2] - q1[3] * q2[3],\
           q1[0] * q2[1] + q1[1] * q2[0] - q1[2] * q2[3] + q1[3] * q2[2],\
           q1[0] * q2[2] + q1[1] * q2[3] + q1[2] * q2[0] - q1[3] * q2[1],\
           q1[0] * q2[3] - q1[1] * q2[2] + q1[2] * q2[1] + q1[3] * q2[0]

   # return _qw * qw - _qx * qx - _qy * qy - _qz * qz, \
   #        _qw * qx + _qx * qw + _qy * qz - _qz * qy, \
   #        _qw * qy + _qy * qw + _qz * qx - _qx * qz, \
   #        _qw * qz + _qz * qw + _qx * qy - _qy * qx


def quaternion_rot(v: Tuple[float, float, float], q: Quaternion) -> \
        Tuple[float, float, float]:
    # return v[1:] + (t[0] * q[0], t[1] * q[0], t[2] * q[0]) + cross(q[1:], (t[0] * 2.0, t[1] * 2.0, t[2] * 2.0))
    # работает
    return quaternion_mul(quaternion_mul(q, (0.0, v[0], v[1], v[2])), inv_quaternion(q))[1:]
    # return qr[1], qr[2], qr[3]


def quaternion_to_euler(q: Quaternion) -> Vector3:
    # работает
    w, x, y, z = q
    ax = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    ay = math.asin(2.0 * (w * y - z * x))
    az = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    return ax, ay, az
    # return ax % math.pi, ay % math.pi, az % math.pi
    # return math.pi + ax, math.pi + ay, math.pi + az

def rot_m_to_quaternion(rm: Matrix3) -> Quaternion:
    # работает
    m00, m01, m02 = rm[0], rm[1], rm[2]
    m10, m11, m12 = rm[3], rm[4], rm[5]
    m20, m21, m22 = rm[6], rm[7], rm[8]
    
    qw = math.sqrt(max(0.0, 1.0 + m00 + m11 + m22 ) ) * 0.5
    qx = math.sqrt(max(0.0, 1.0 + m00 - m11 - m22 ) ) * 0.5
    qy = math.sqrt(max(0.0, 1.0 - m00 + m11 - m22 ) ) * 0.5
    qz = math.sqrt(max(0.0, 1.0 - m00 - m11 + m22 ) ) * 0.5
    
    qx = math.copysign(qx, m21 - m12)
    qy = math.copysign(qy, m02 - m20)
    qz = math.copysign(qz, m10 - m01)
    
    norm = 1.0 / math.sqrt(sum(v ** 2 for v in (qw, qx, qy, qz)))

    return qw * norm, qx * norm, qy * norm, qz * norm
    # return qw, qx, qy, qz
    # m00, m01, m02 = rm[0], rm[1], rm[2]
    # m10, m11, m12 = rm[3], rm[4], rm[5]
    # m20, m21, m22 = rm[6], rm[7], rm[8]
    # tr = m00 + m11 + m22
    # if tr > 0.0:
    #     s: float = math.sqrt(tr + 1.0)
    #     ew: float = s * 0.5
    #     s = 0.5 / s
    #     ex: float = (m12 - m21) * s
    #     ey: float = (m20 - m02) * s
    #     ez: float = (m01 - m10) * s
    #     return ew, ex, ey, ez
    # i: int
    # j: int
    # k: int
    # if m11 > m00:
    #     if m22 > m11:
    #         i = 2
    #         j = 0
    #         k = 1
    #     else:
    #         i = 1
    #         j = 2
    #         k = 0
    # elif m22 > m00:
    #     i = 2
    #     j = 0
    #     k = 1
    # else:
    #     i = 0
    #     j = 1
    #     k = 2
    # quaternion = [0.0, 0.0, 0.0, 0.0]
    # s = math.sqrt((rm[i * 3 + i] - (rm[j * 3 + j] + rm[k * 3 + k])) + 1.0)
    # quaternion[i] = s * 0.5
    # if s != 0.0:
    #     s = 0.5 / s
    # quaternion[j] = (rm[i * 3 + j] + rm[j * 3 + i]) * s
    # quaternion[k] = (rm[i * 3 + k] + rm[k * 3 + i]) * s
    # quaternion[3] = (rm[j * 3 + k] - rm[k * 3 + j]) * s
    # return quaternion[0], quaternion[1], quaternion[2], quaternion[3]
    


def quaternion_to_rot_m(q: Quaternion):
    ew, ex, ey, ez = q
    xx = ex * ex * 2.0
    xy = ex * ey * 2.0
    xz = ex * ez * 2.0
    
    yy = ey * ey * 2.0
    yz = ey * ez * 2.0
    zz = ez * ez * 2.0
    
    wx = ew * ex * 2.0
    wy = ew * ey * 2.0
    wz = ew * ez * 2.0
    return (1.0 - (yy + zz), xy + wz,         xz - wy),\
           (xy - wz,         1.0 - (xx + zz), yz + wx),\
           (xz + wy,         yz - wx,         1.0 - (xx + yy))
    # работает
    # w, x, y, z = q
    # xx = x * x * 2.0
    # xy = x * y * 2.0
    # xz = x * z * 2.0
    # 
    # yy = y * y * 2.0
    # yz = y * z * 2.0
    # zz = z * z * 2.0
    # 
    # wx = w * x * 2.0
    # wy = w * y * 2.0
    # wz = w * z * 2.0
    # 
    # return (1.0 - (yy + zz), xy - wz,         xz + wy       ), \
    #        (xy + wz,         1.0 - (xx + zz), yz - wx       ), \
    #        (xz - wy,         yz + wx,         1.0 - (xx + yy))


def cross(a: Vector3, b: Vector3) -> Vector3:
    return a[2] * b[1] - a[1] * b[2],\
           a[0] * b[2] - a[2] * b[0],\
           a[1] * b[0] - a[0] * b[1]


def dot(a: Vector3, b: Vector3):
    return sum(ai * bi for ai, bi in zip(a, b))


def inv_norm(a: Vector3) -> float:
    return 1.0 / math.sqrt(sum(p * p for p in a))


def normalize(a: Vector3) -> Vector3:
    n = inv_norm(a)
    return a[0] * n, a[1] * n, a[2] * n


def build_rot_m(ey: Vector3, ez: Vector3 = None) -> Tuple[Vector3, Vector3, Vector3]:
    if ez is None:
        ez = (0.0, 0.0, 1.0)

    ey = normalize(ey)
    ez = normalize(ez)
    ex = normalize(cross(ez, ey))
    ez = normalize(cross(ey, ex))

    return (ex[0], ex[1], ex[2]),\
           (ey[0], ey[1], ey[2]),\
           (ez[0], ez[1], ez[2])


def comp_filter(path: str, k: float):
    def angles_fast(_ax, _ay, _az) -> Tuple[float, float, float]:
        return math.atan2(_ax, _az),\
               math.atan2(_ax, _ay),\
               math.atan2(_az, _ax)
        
        #return math.atan2(_az, _az), \
        #       math.atan2(_ay, _az), \
        #       math.atan2(_ay, _ax)
               
    _log = read_imu_log(path)
    ax, ay, az = accelerations(_log)
    ang_vx, ang_vy, ang_vz = ang_velocities(_log)
    # ax.reverse()
    # ay.reverse()
    # az.reverse()
    # ang_vx.reverse()
    # ang_vy.reverse()
    # ang_vz.reverse()
    t_vals  = [0.0]
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

    ex, ey, ez = build_rot_m(accel)  # строим базис для такой системы (это функция точно верная)
    # (орты базиса - столбцы матрицы поворота)
    start_q = rot_m_to_quaternion((ex[0], ey[0], ez[0],
                                   ex[1], ey[1], ez[1],
                                   ex[2], ey[2], ez[2]))

    start_angles = quaternion_to_euler(start_q)

    angle_x = [start_angles[0]]
    angle_y = [start_angles[1]]
    angle_z = [start_angles[2]]

    angle_x_q = [start_angles[0]]
    angle_y_q = [start_angles[1]]
    angle_z_q = [start_angles[2]]


    q_rot = quaternion(start_angles[0], start_angles[1], start_angles[2])
    g_calib = quaternion_rot(accel, q_rot)
    
    # accel_0 = [2.8, 9.31, 1.66]
    curr_t = 0.0
    for index in range(min((len(ax), len(ay), len(az), len(ang_vx), len(ang_vy), len(ang_vz)))):
        # _ax, _ay, _az = angles_fast(ax[index], ay[index], az[index])
        dt = _log.way_points[index].dtime
        curr_t += dt
        if curr_t < 1.0:
            continue
            
        t_vals.append(curr_t + dt)

        angle_x.append(angle_x[-1] + ang_vx[index] * dt )
        angle_y.append(angle_y[-1] + ang_vy[index] * dt )
        angle_z.append(angle_z[-1] + ang_vz[index] * dt )

        ex, ey, ez = build_rot_m((ax[index], ay[index], az[index]))
        # строим базис для такой системы (это функция точно верная)
        # (орты базиса - столбцы матрицы поворота)
        _q = rot_m_to_quaternion((ex[0], ey[0], ez[0],
                                  ex[1], ey[1], ez[1],
                                  ex[2], ey[2], ez[2]))

        _angles = quaternion_to_euler(_q)

        angle_x_q.append(_angles[0])
        angle_y_q.append(_angles[1])
        angle_z_q.append(_angles[2])

        # rotation   = inv_quaternion(quaternion(angle_x[-1], angle_y[-1], angle_z[-1]))
        rotation = inv_quaternion(quaternion(_angles[0], _angles[1], _angles[2]))
        g_current  = quaternion_rot(g_calib, rotation)
        # ex, ey, ez = quaternion_to_rot_m(rotation)

        accel_x.append(ax[index] - g_current[0])
        accel_y.append(ay[index] - g_current[1])
        accel_z.append(az[index] - g_current[2])

        rotation = inv_quaternion(quaternion(angle_x[-1], angle_y[-1], angle_z[-1]))
        ex, ey, ez = quaternion_to_rot_m(rotation)

        d_ax = (accel_x[-1] - accel_x[-2])
        d_ay = (accel_y[-1] - accel_y[-2])
        d_az = (accel_z[-1] - accel_z[-2])
        
        d_ax = 1.0 # math.copysign(d_ax, 1.0) if abs(d_ax) > 0.0001 else 0.0
        d_ay = 1.0 # math.copysign(d_ay, 1.0) if abs(d_ay) > 0.0001 else 0.0
        d_az = 1.0 # math.copysign(d_az, 1.0) if abs(d_az) > 0.0001 else 0.0

        velocity_x.append( velocity_x[-1] + (ex[0] * accel_x[-1] * d_ax + ey[0] * accel_y[-1] * d_ay + ez[0] * accel_z[-1] * d_az) * dt)
        velocity_y.append( velocity_y[-1] + (ex[1] * accel_x[-1] * d_ax + ey[1] * accel_y[-1] * d_ay + ez[1] * accel_z[-1] * d_az) * dt)
        velocity_z.append( velocity_z[-1] + (ex[2] * accel_x[-1] * d_ax + ey[2] * accel_y[-1] * d_ay + ez[2] * accel_z[-1] * d_az) * dt)
        
        path_x.append(path_x[-1] + (ez[0] * velocity_x[-1] + ez[1] * velocity_y[-1] + ez[2] * velocity_z[-1]) * dt) #(velocity_x[-1]) * dt)
        path_y.append(path_y[-1] + (ey[0] * velocity_x[-1] + ey[1] * velocity_y[-1] + ey[2] * velocity_z[-1]) * dt) #(velocity_y[-1]) * dt)
        path_z.append(path_z[-1] + (ex[0] * velocity_x[-1] + ex[1] * velocity_y[-1] + ex[2] * velocity_z[-1]) * dt) #(velocity_z[-1]) * dt)

    # plt.show()
    sx = [0.0]
    sz = [0.0]
    t = 0
    # dt = [v.dtime for v in _log.way_points]
    # for index in range(len(dt)):
    #     if t > t1:
    #         break
    #     t +=dt[index]
    #     if t < t0:
    #         continue
    #     sx.append(sx[-1] + ax[index] * math.sin(r_ang_y[index] * 1.0) * dt[index])
    #     sz.append(sz[-1] - ax[index] * math.cos(r_ang_y[index] * 1.0) * dt[index])

    fig, axs = plt.subplots(4)

    axs[0].plot(t_vals, accel_x, 'r')
    axs[0].plot(t_vals, accel_y, 'g')
    axs[0].plot(t_vals, accel_z, 'b')
    # axs[0].set_aspect('equal', 'box')
    axs[0].set_xlabel("t, [sec]")
    axs[0].set_ylabel("$a(t), [m/sec^2]$")
    axs[0].set_title("accelerations")

    axs[1].plot(t_vals, angle_x, 'r')
    axs[1].plot(t_vals, angle_y, 'g')
    axs[1].plot(t_vals, angle_z, 'b')

    axs[1].plot(t_vals, angle_x_q, ':r')
    axs[1].plot(t_vals, angle_y_q, ':g')
    axs[1].plot(t_vals, angle_z_q, ':b')
    
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
    axs[3].plot(path_x, path_y, 'r')
    axs[3].plot(path_x, path_z, 'g')
    axs[3].plot(path_y, path_z, 'b')
    axs[3].set_aspect('equal', 'box')
    axs[3].set_xlabel("t, [sec]")
    axs[3].set_ylabel("$S(t), [m]$")
    axs[3].set_title("building path")

    plt.show()


if __name__ == "__main__":
    comp_filter('building_walk_straight.json', 1.0)
    """
    Задача:
    Вектор (0, 1, 0)
    Кватернион из углов 45, 35, 25 градусов
    Повернуть вектор кватернионом и сделать обратное преобразование
    Задача работает нормально
    """
    deg_2_rad = math.pi / 180.0
    rad_2_deg = 180.0 / math.pi
    q_1 = quaternion(45 * deg_2_rad, 35 * deg_2_rad, 25 * deg_2_rad)
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
    q = quaternion(0, 0, -45 * deg_2_rad)
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

    q_rot = quaternion(start_angles[0], start_angles[1], start_angles[2])

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
