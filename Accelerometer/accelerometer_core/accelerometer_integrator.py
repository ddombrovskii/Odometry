from accelerometer_core.utilities import Matrix4, Vector3, Quaternion
from accelerometer_core import read_imu_log, WayPoint, GRAVITY_CONSTANT, read_accel_log
from matplotlib import pyplot as plt
from typing import List, Tuple
import numpy as np
accel_k = 0.95  # значение параметра комплиментарного фильтра для ускорения
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


def compute_path(path_src: str, start_time: float = 0.5, calib_time: float = 5.5, forward: Vector3 = None ) -> \
        Tuple[List[float], List[Matrix4], List[Vector3], List[Vector3], List[Vector3]]:
    accel_log = read_accel_log(path_src)
    t = 0.0
    calib_t = 0.0
    calib_done = False
    c_accel = Vector3()
    c_omega = Vector3()
    c_count = 0
    time_values: List[float]   = []
    angles:      List[Vector3] = []
    accel_basis: List[Matrix4] = []  # [Matrix4.build_basis(point.acceleration)]
    velocities:  List[Vector3] = []  # [Vector3(0.0, 0.0, 0.0)]
    positions:   List[Vector3] = []  # [Vector3(0.0, 0.0, 0.0)]

    curr_accel = accel_log.way_points[0].acceleration
    prev_accel = accel_log.way_points[0].acceleration
    accel_bias = 0.05
    trust_t = 0.25
    check_t = 0.0
    for point in accel_log.way_points:
        prev_accel = curr_accel
        curr_accel = point.acceleration

        if t < start_time:
            t += point.dtime
            continue

        if calib_t < calib_time:
            calib_t += point.dtime
            if(curr_accel - prev_accel).magnitude() > accel_bias:
                calib_t = calib_time + 1.0
                continue
            c_accel += curr_accel
            c_omega += point.angles_velocity
            c_count += 1
            continue

        if not calib_done:
            c_accel /= c_count
            c_omega /= c_count
            basis: Matrix4 = Matrix4.build_basis(c_accel, forward)
            accel_basis.append(Matrix4.build_transform(basis.right, basis.up, basis.front, c_accel))
            c_accel = Vector3(basis.m00 * c_accel.x + basis.m10 * c_accel.y + basis.m20 * c_accel.z,
                              basis.m01 * c_accel.x + basis.m11 * c_accel.y + basis.m21 * c_accel.z,
                              basis.m02 * c_accel.x + basis.m12 * c_accel.y + basis.m22 * c_accel.z)
            angles.append(Quaternion.from_rotation_matrix(accel_basis[-1]).to_euler_angles())
            print(f"c_accel ls: {accel_basis[-1].origin}")
            print(f"c_accel   : {c_accel}")
            print(f"c_omega   : {c_omega}")
            print(f"c_count   : {c_count}")
            velocities.append(Vector3(0.0, 0.0, 0.0))
            positions .append(Vector3(0.0, 0.0, 0.0))
            time_values.append(0.0)
            calib_done = True

        basis = accel_basis[-1]
        dt    = point.dtime
        time_values.append(time_values[-1] + dt)
        omega = point.angles_velocity
        # r: Vector3 = (basis.right + Vector3.cross(omega, basis.right) * dt).normalized()
        # комплиментарная фильтрация и и привязка u к направлению g
        u: Vector3 = ((basis.up    + Vector3.cross(omega, basis.up   ) * dt) * \
                      accel_k + (1.0 - accel_k) * curr_accel.normalized()).normalized()
        f: Vector3 = (basis.front + Vector3.cross(omega, basis.front) * dt).normalized()
        r = Vector3.cross(f, u).normalized()
        f = Vector3.cross(u, r).normalized()
        # получим ускорение в мировой системе координат за вычетом ускорения свободного падения
        # a: Vector3 = Vector3(r.x * accel.x + r.y * accel.y + r.z * accel.z - c_accel.x,
        #                      u.x * accel.x + u.y * accel.y + u.z * accel.z - c_accel.y,  # - GRAVITY_CONSTANT,
        #                      f.x * accel.x + f.y * accel.y + f.z * accel.z - c_accel.z)
        a: Vector3 = Vector3(curr_accel.x - (r.x * c_accel.x + u.x * c_accel.y + f.x * c_accel.z),
                             curr_accel.y - (r.y * c_accel.x + u.y * c_accel.y + f.y * c_accel.z),
                             curr_accel.z - (r.z * c_accel.x + u.z * c_accel.y + f.z * c_accel.z))

        if (curr_accel - prev_accel).magnitude() < accel_bias:
            check_t += dt
        else:
            check_t = 0

        # angles.     append(Quaternion.from_rotation_matrix(accel_basis[-1]).to_euler_angles())
        accel_basis.append(Matrix4.build_transform(r, u, f, a))
        angles.     append(angles[-1] + point.angles_velocity * dt)
        # a -= Vector3(time_values[-1] * 0.0003, 0, time_values[-1] * 0.001 )
        v = (velocities[-1] + (r * a.x + u * a.y + f * a.z) * dt) if check_t <= trust_t else Vector3(0.0, 0.0, 0.0)
        # check_t = 0
        velocities. append(v)
        positions.  append(positions [-1] + (r * v.x + u * v.y + f * v.z) * dt)
    return time_values, accel_basis, angles, velocities, positions


if __name__ == "__main__":
    # comp_test()
    # exit()
    time_values, accel_basis, angles, velocities, positions =\
        compute_path("accelerometer_records/the newest/building_walk_straight.json")

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
    # axes[3].plot(time_values, [p.y for p in positions], 'g')
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
