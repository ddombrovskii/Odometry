from accelerometer_settings import load_accelerometer_settings, save_accelerometer_settings
from accelerometer_recording import read_current_data, read_and_save_data, read_record,\
    accelerations, time_values, ang_velocities
from cgeo.filtering import RealTimeFilter
from accelerometer import Accelerometer
from cgeo.loop_timer import LoopTimer
import matplotlib.pyplot as plt


def read_with_time_interval_example(read_time: float = 5.0, delta_read_time: float = 0.1) -> None:
    acc = Accelerometer()
    # save_accelerometer_settings(acc, 'accelerometer_settings.json')
    load_accelerometer_settings(acc, 'settings.json')
    print(acc)
    timer = LoopTimer(delta_read_time)
    while timer.time < read_time:
        with timer:
            print(read_current_data(acc, 4))
            

def read_and_save_with_time_interval_example(file_path: str, read_time: float = 5.0,
                                             delta_read_time: float = 0.075) -> None:
    acc = Accelerometer()
    read_and_save_data(file_path, acc, read_time, delta_read_time)


def read_and_show_accel_log(log_file: str):
    filter_x = RealTimeFilter()
    filter_x.mode = 0
    filter_x.window_size = 33

    filter_y = RealTimeFilter()
    filter_y.mode = 0
    filter_y.window_size = 33

    filter_z = RealTimeFilter()
    filter_z.mode = 0
    filter_z.window_size = 33

    log = read_record(log_file)
    x, y, z = accelerations(log)
    t = time_values(log)
    x_avg = sum(x)/len(x)
    y_avg = sum(y)/len(y)
    z_avg = sum(z)/len(z)

    x = [xi - x_avg for xi in x]
    y = [yi - y_avg for yi in y]
    z = [zi - z_avg for zi in z]

    xf = [filter_x.filter(xi) for xi in x]
    yf = [filter_y.filter(yi) for yi in y]
    zf = [filter_z.filter(zi) for zi in z]

    # quant_a = +/-0.01
    print(f"a-calibrated az: {x_avg:10}, ay: {y_avg:10}, az: {z_avg:10}")

    plt.plot(t, x, ':r')
    plt.plot(t, y, ':g')
    plt.plot(t, z, ':b')

    plt.plot(t, xf, 'r')
    plt.plot(t, yf, 'g')
    plt.plot(t, zf, 'b')

    plt.show()


def read_and_show_ang_vel_log(log_file: str):
    filter_x = RealTimeFilter()
    filter_x.mode = 0
    filter_x.window_size = 33

    filter_y = RealTimeFilter()
    filter_y.mode = 0
    filter_y.window_size = 33

    filter_z = RealTimeFilter()
    filter_z.mode = 0
    filter_z.window_size = 33

    log = read_record(log_file)

    x, y, z = ang_velocities(log)

    t = time_values(log)

    x_avg = sum(x)/len(x)
    y_avg = sum(y)/len(y)
    z_avg = sum(z)/len(z)

    x = [xi - x_avg for xi in x]
    y = [yi - y_avg for yi in y]
    z = [zi - z_avg for zi in z]

    xf = [filter_x.filter(xi) for xi in x]
    yf = [filter_y.filter(yi) for yi in y]
    zf = [filter_z.filter(zi) for zi in z]

    # quant_a = +/-0.01
    print(f"a-calibrated az: {x_avg:10}, ay: {y_avg:10}, az: {z_avg:10}")

    plt.plot(t, x, ':r')
    plt.plot(t, y, ':g')
    plt.plot(t, z, ':b')

    plt.plot(t, xf, 'r')
    plt.plot(t, yf, 'g')
    plt.plot(t, zf, 'b')

    plt.show()


def mask(shift: int) -> int:
    m = 0
    for i in range(32):
        if shift <= i:
            m |= 1 << i
    return m


if __name__ == "__main__":
    # read_with_time_interval_example()
    read_and_show_ang_vel_log('still.json')
    read_and_show_accel_log('still.json')
    # # read_and_save_with_time_interval_example('still.json', read_time=300)
