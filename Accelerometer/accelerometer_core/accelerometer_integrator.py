from accelerometer_core.utilities import Matrix4, Vector3, Quaternion
from accelerometer_core import read_imu_log, WayPoint, GRAVITY_CONSTANT
from matplotlib import pyplot as plt
from typing import List
import numpy as np
accel_kfc = 0.999  # значение параметра комплиментарного фильтра для ускорения
velocity_k = 0.9995  # значение параметра комплиментарного фильтра для ускорения


def comp_test(k: float = 0.5):
    x = np.linspace(0, 10, 1000)
    y = x * x * 0.01 + np.sin(10 * x) * .01
    z = []
    for i in range(x.size):
        z.append(y[i] * k - y[i - 1]  * (1 - k ))
    z = np.array(z)
    plt.plot(x, y, 'r')
    plt.plot(x, z, 'g')
    plt.show()


if __name__ == "__main__":
    # comp_test()
    # exit()
    accel_log = read_imu_log("accelerometer_records/the newest/building_walk_drunk.json")
    time_values = accel_log.time_values
    time_values.insert(0, time_values[0])
    point: WayPoint = accel_log.way_points[1000]

    angles: List[Vector3] = []
    accel_basis: List[Matrix4] = [Matrix4.build_basis(point.acceleration)]
    angles.append(Quaternion.from_rotation_matrix(accel_basis[-1]).to_euler_angles())
    velocities: List[Vector3] = [Vector3(0.0, 0.0, 0.0)]
    positions:  List[Vector3] = [Vector3(0.0, 0.0, 0.0)]
    for point in accel_log.way_points:
        basis = accel_basis[-1]
        dt    = point.dtime if point.time > 1.0 else 0.0
        omega = point.angles_velocity
        accel = point.acceleration
        # r: Vector3 = (basis.right + Vector3.cross(omega, basis.right) * dt).normalized()
        # комплиментарная фильтрация и и привязка u к направлению g
        u: Vector3 = (basis.up    + Vector3.cross(omega, basis.up   ) * dt).normalized() * \
                      accel_kfc + (1.0 - accel_kfc) * accel
        f: Vector3 = (basis.front + Vector3.cross(omega, basis.front) * dt).normalized()
        r = Vector3.cross(f, u).normalized()
        f = Vector3.cross(u, r).normalized()
        # получим ускорение в мировой системе координат за вычетом ускорения свободного падения
        a: Vector3 = Vector3(r.x * accel.x + r.y * accel.y + r.z * accel.z,
                             u.x * accel.x + u.y * accel.y + u.z * accel.z - 9.6903,  # - GRAVITY_CONSTANT,
                             f.x * accel.x + f.y * accel.y + f.z * accel.z)
                             
        # angles.     append(Quaternion.from_rotation_matrix(accel_basis[-1]).to_euler_angles())
        accel_basis.append(Matrix4.build_transform(r, u, f, a))
        angles.     append(angles[-1] + point.angles_velocity * dt)
        da = abs(accel_basis[-1].origin - accel_basis[-2].origin) / dt if dt != 0 else Vector3(0,0,0)
        da = Vector3(1.0 if da.x > 1.5 else 0.0,
                     1.0 if da.y > 1.5 else 0.0,
                     1.0 if da.z > 1.5 else 0.0)
        velocities. append(velocities[-1] + a  * dt)
        velocities[-1] = velocities[-1] - a * da  * dt
        positions.  append(positions [-1] + velocities[-1] * dt)

    fig, axes = plt.subplots(5)
    axes[0].plot(time_values, [a.x for a in angles], 'r')
    axes[0].plot(time_values, [a.y for a in angles], 'g')
    axes[0].plot(time_values, [a.z for a in angles], 'b')
    axes[0].set_xlabel("t, [sec]")
    axes[0].set_ylabel("$angle(t), [rad]$")
    axes[0].set_title("angles")
    
    axes[1].plot(time_values, [a.origin.x for a in accel_basis], 'r')
    axes[1].plot(time_values, [a.origin.y for a in accel_basis], 'g')
    axes[1].plot(time_values, [a.origin.z for a in accel_basis], 'b')
    axes[1].set_xlabel("t, [sec]")
    axes[1].set_ylabel("$a(t), [m/sec^2]$")
    axes[1].set_title("accelerations - world space")

    axes[2].plot(time_values, [v.x for v in velocities], 'r')
    axes[2].plot(time_values, [v.y for v in velocities], 'g')
    axes[2].plot(time_values, [v.z for v in velocities], 'b')
    axes[2].set_xlabel("t, [sec]")
    axes[2].set_ylabel("$v(t), [m/sec]$")
    axes[2].set_title("velocities - world space")

    axes[3].plot(time_values, [p.x for p in positions], 'r')
    axes[3].plot(time_values, [p.y for p in positions], 'g')
    axes[3].plot(time_values, [p.z for p in positions], 'b')
    axes[3].set_xlabel("t, [sec]")
    axes[3].set_ylabel("$S(t), [m]$")
    axes[3].set_title("positions - world space")

    axes[4].plot([p.x for p in positions], [p.z for p in positions], 'r')
    axes[4].set_aspect('equal', 'box')
    axes[4].set_xlabel("Sx, [m]")
    axes[4].set_ylabel("Sz, [m]")
    axes[4].set_title("positions - world space")
    plt.show()
