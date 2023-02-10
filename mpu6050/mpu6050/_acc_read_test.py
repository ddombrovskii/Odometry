from accelerometer import Accelerometer
from accelerometer_recording import read_accel, read_imu, imu_ang_velocities, imu_time_values, record_imu_log, read_imu_log
from inertial_measurement_unit import IMU
import time
from matplotlib import pyplot as plt

if __name__ == "__main__":
    time.sleep(30)
    a = IMU()
    record_imu_log('building_walk_drunk.json', a,  180.0, 0.001)
    a_log = read_imu_log('building_walk_drunk.json')
    avx, avy, avz = imu_ang_velocities(a_log)
    t = imu_time_values(a_log)
    fig, axs = plt.subplots(1)
    axs.plot(t, avx, 'r')
    axs.plot(t, avy, 'g')
    axs.plot(t, avz, 'b')

    plt.show()
