from accelerometer_core.accelerometer_recording import read_imu_log, read_accel_log
from matplotlib import pyplot as plt


def imu_log_read_test():
    """
    Пример чтения лог файла для инерциалки
    """
    a_log = read_imu_log('../accelerometer_records/the newest/building_walk_straight.json')

    avx, avy, avz = a_log.angles_velocities_x, a_log.angles_velocities_y, a_log.angles_velocities_z

    ang_x, ang_y, ang_z = a_log.angles_x, a_log.angles_y, a_log.angles_z

    ax, ay, az = a_log.accelerations_x, a_log.accelerations_y, a_log.accelerations_z

    vx, vy, vz = a_log.velocities_x, a_log.velocities_y, a_log.velocities_z

    sx, sy, sz = a_log.positions_x, a_log.positions_y, a_log.positions_z

    t = a_log.time_values

    fig, axs = plt.subplots(5)

    axs[0].plot(t, avx, 'r')
    axs[0].plot(t, avy, 'g')
    axs[0].plot(t, avz, 'b')
    axs[0].set_xlabel("t, [sec]")
    axs[0].set_ylabel("$ang_v(t), [rad/sec]$")
    axs[0].set_title("angles velocities")

    axs[1].plot(t, ang_x, 'r')
    axs[1].plot(t, ang_y, 'g')
    axs[1].plot(t, ang_z, 'b')
    axs[1].set_xlabel("t, [sec]")
    axs[1].set_ylabel("$angles(t), [rad]$")
    axs[1].set_title("angles")

    axs[2].plot(t, ax, 'r')
    axs[2].plot(t, ay, 'g')
    axs[2].plot(t, az, 'b')
    axs[2].set_xlabel("t, [sec]")
    axs[2].set_ylabel("$a(t), [m/sec^2]$")
    axs[2].set_title("accelerations")

    axs[3].plot(t, vx, 'r')
    axs[3].plot(t, vy, 'g')
    axs[3].plot(t, vz, 'b')
    axs[3].set_xlabel("t, [sec]")
    axs[3].set_ylabel("$v(t), [m/sec]$")
    axs[3].set_title("velocities")

    axs[4].plot(t, sx, 'r')
    axs[4].plot(t, sy, 'g')
    axs[4].plot(t, sz, 'b')
    axs[4].set_xlabel("t, [sec]")
    axs[4].set_ylabel("$s(t), [m/sec]$")
    axs[4].set_title("positions")

    plt.show()


def accelerometer_log_read_test():
    """
    Пример чтения лог файла для акселерометра
    """
    a_log = read_accel_log('../accelerometer_records/the newest/building_walk_straight.json')

    ax, ay, az = a_log.accelerations_x, a_log.accelerations_y, a_log.accelerations_z

    avx, avy, avz = a_log.angles_velocities_x, a_log.angles_velocities_y, a_log.angles_velocities_z

    t = a_log.time_values
    fig, axs = plt.subplots(2)
    axs[0].plot(t, ax, 'r')
    axs[0].plot(t, ay, 'g')
    axs[0].plot(t, az, 'b')
    axs[0].set_xlabel("t, [sec]")
    axs[0].set_ylabel("$a(t), [m/sec^2]$")
    axs[0].set_title("accelerations")

    axs[1].plot(t, avx, 'r')
    axs[1].plot(t, avy, 'g')
    axs[1].plot(t, avz, 'b')
    axs[1].set_xlabel("t, [sec]")
    axs[1].set_ylabel("$ang_v(t), [rad/sec]$")
    axs[1].set_title("angles velocities")
    plt.show()


if __name__ == "__main__":
    accelerometer_log_read_test()
    imu_log_read_test()
