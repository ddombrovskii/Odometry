from accelerometer_recording import read_imu_log
from matplotlib import pyplot as plt
import os, sys
os.system("")
LINE_UP = '\033[1A'
LINE_CLEAR = '\033[2K'
COLOR = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
}

# print(COLOR["HEADER"], "Testing Green!!", COLOR["ENDC"])

if __name__ == "__main__":
    log_src = "accelerometer_records/record_bno_test.json"
    log_file = read_imu_log(log_src, order=0)
    fig, axes = plt.subplots(4, 1)

    axes[0].plot(log_file.time_values, log_file.accelerations_x, 'r')
    axes[0].plot(log_file.time_values, log_file.accelerations_y, 'g')
    axes[0].plot(log_file.time_values, log_file.accelerations_z, 'b')
    axes[0].legend({"ax", "ay", "az"})
    # axes[0].set_aspect('equal', 'box')
    axes[0].set_xlabel("time, [sec]")
    axes[0].set_ylabel("A, [m]")
    axes[0].set_title("accelerations - local space")

    axes[1].plot(log_file.time_values, log_file.velocities_x, 'r')
    axes[1].plot(log_file.time_values, log_file.velocities_y, 'g')
    axes[1].plot(log_file.time_values, log_file.velocities_z, 'b')
    axes[1].legend({"vx", "vy", "vz"})
    # axes[1].set_aspect('equal', 'box')
    axes[1].set_xlabel("time, [sec]")
    axes[1].set_ylabel("V, [m]")
    axes[1].set_title("velocity - world space")

    axes[2].plot(log_file.positions_x, log_file.positions_z, 'b')
    axes[2].legend({"sx", "sy", "sz"})
    axes[2].set_aspect('equal', 'box')
    axes[2].set_xlabel("time, [sec]")
    axes[2].set_ylabel("S, [m]")
    axes[2].set_title("position - world space")

    axes[3].plot(log_file.time_values, log_file.angles_x, 'r')
    axes[3].plot(log_file.time_values, log_file.angles_y, 'g')
    axes[3].plot(log_file.time_values, log_file.angles_z, 'b')
    axes[3].legend({"vx", "vy", "vz"})
    # axes[1].set_aspect('equal', 'box')
    axes[3].set_xlabel("time, [sec]")
    axes[3].set_ylabel("V, [m]")
    axes[3].set_title("angles - world space")

    plt.show()

