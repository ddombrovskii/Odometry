from accelerometer_settings import load_accelerometer_settings, save_accelerometer_settings
from accelerometer_recording import read_current_data, read_and_save_data, load_accel_record, \
    accelerations, time_values, ang_velocities, velocities, positions
from cgeo.filtering import RealTimeFilter
from accelerometer import Accelerometer
from cgeo.loop_timer import LoopTimer
import matplotlib.pyplot as plt


# TODO refactor or remove idgf...


def read_with_time_interval_example(read_time: float = 5.0, delta_read_time: float = 0.033) -> None:
    acc = Accelerometer()
    acc.use_filtering = False
    # save_accelerometer_settings(acc, 'accelerometer_settings.json')
    load_accelerometer_settings(acc, 'settings.json')
    print(acc)
    timer = LoopTimer(delta_read_time)
    while timer.time < read_time:
        with timer:
            print(read_current_data(acc, 4))
            

def read_and_save_with_time_interval_example(file_path: str, read_time: float = 5.0,
                                             delta_read_time: float = 0.005) -> None:
    acc = Accelerometer()
    # load_accelerometer_settings(acc, 'settings.json')
    read_and_save_data(file_path, acc, read_time, delta_read_time, mode=3)


def read_and_show_velocity_log(log_file: str, show_filtered: bool = False):
    log = load_accel_record(log_file)
    x, y, z = velocities(log)
    t = time_values(log)

    if show_filtered:
        _figure, _ax = plt.subplots(2)
        _ax[0].plot(t, x, 'r')
        _ax[0].plot(t, y, 'g')
        _ax[0].plot(t, z, 'b')
        _ax[0].legend([r'$a_{x}$', r'$a_{y}$', r'$a_{z}$'], loc='upper left')
        _ax[0].set_xlabel("$t,[sec]$")
        _ax[0].set_ylabel("$a(t),[{m} / {sec}^2]$")
        _ax[0].set_title("raw velocities")
        ##########################
        filter_ = RealTimeFilter()
        filter_.mode = 2
        filter_.kalman_error = 0.99
        filter_.k_arg = 0.001
        print(filter_)
        _ax[1].plot(t, [filter_.filter(xi) for xi in x], 'r')
        filter_.clean_up()
        _ax[1].plot(t, [filter_.filter(xi) for xi in y], 'g')
        filter_.clean_up()
        _ax[1].plot(t, [filter_.filter(xi) for xi in z], 'b')
        _ax[1].legend([r'$a_{x}$', r'$a_{y}$', r'$a_{z}$'], loc='upper left')
        _ax[1].set_xlabel("$t,[sec]$")
        _ax[1].set_ylabel("$v(t),[{grad} / {sec}]$")
        _ax[1].set_title("filtered velocities")
        plt.show()
        return

    _figure, _ax = plt.subplots(2)
    _ax[0].plot(t, x, 'r')
    _ax[0].plot(t, y, 'g')
    _ax[0].plot(t, z, 'b')
    _ax[0].legend([r'$a_{x}$', r'$a_{y}$', r'$a_{z}$'], loc='upper left')
    _ax[0].set_xlabel("$t,[sec]$")
    _ax[0].set_ylabel("$a(t),[{m} / {sec}^2]$")
    _ax[0].set_title("raw accelerations")
    ##########################
    _ax[1].plot(t, x, 'r')
    _ax[1].plot(t, y, 'g')
    _ax[1].plot(t, z, 'b')
    _ax[1].legend([r'$a_{x}$', r'$a_{y}$', r'$a_{z}$'], loc='upper left')
    _ax[1].set_xlabel("$t,[sec]$")
    _ax[1].set_ylabel("$v(t),[{grad} / {sec}]$")
    _ax[1].set_title("filtered accelerations")
    plt.show()



def read_and_show_accel_log(log_file: str, show_filtered: bool = False):
    log = load_accel_record(log_file)
    x, y, z = accelerations(log)
    t = time_values(log)

    if show_filtered:
        _figure, _ax = plt.subplots(2)
        _ax[0].plot(t, x, 'r')
        _ax[0].plot(t, y, 'g')
        _ax[0].plot(t, z, 'b')
        _ax[0].legend([r'$a_{x}$', r'$a_{y}$', r'$a_{z}$'], loc='upper left')
        _ax[0].set_xlabel("$t,[sec]$")
        _ax[0].set_ylabel("$a(t),[{m} / {sec}^2]$")
        _ax[0].set_title("raw accelerations")
        ##########################
        filter_ = RealTimeFilter()
        filter_.mode = 2
        filter_.kalman_error = 0.99
        filter_.k_arg = 0.001
        print(filter_)
        _ax[1].plot(t, [filter_.filter(xi) for xi in x], 'r')
        filter_.clean_up()
        _ax[1].plot(t, [filter_.filter(xi) for xi in y], 'g')
        filter_.clean_up()
        _ax[1].plot(t, [filter_.filter(xi) for xi in z], 'b')
        _ax[1].legend([r'$a_{x}$', r'$a_{y}$', r'$a_{z}$'], loc='upper left')
        _ax[1].set_xlabel("$t,[sec]$")
        _ax[1].set_ylabel("$v(t),[{grad} / {sec}]$")
        _ax[1].set_title("filtered accelerations")
        plt.show()
        return

    _figure, _ax = plt.subplots(2)
    _ax[0].plot(t, x, 'r')
    _ax[0].plot(t, y, 'g')
    _ax[0].plot(t, z, 'b')
    _ax[0].legend([r'$a_{x}$', r'$a_{y}$', r'$a_{z}$'], loc='upper left')
    _ax[0].set_xlabel("$t,[sec]$")
    _ax[0].set_ylabel("$a(t),[{m} / {sec}^2]$")
    _ax[0].set_title("raw accelerations")
    ##########################
    _ax[1].plot(t, x, 'r')
    _ax[1].plot(t, y, 'g')
    _ax[1].plot(t, z, 'b')
    _ax[1].legend([r'$a_{x}$', r'$a_{y}$', r'$a_{z}$'], loc='upper left')
    _ax[1].set_xlabel("$t,[sec]$")
    _ax[1].set_ylabel("$v(t),[{grad} / {sec}]$")
    _ax[1].set_title("filtered accelerations")
    plt.show()


def read_and_show_position_log(log_file: str, show_filtered: bool = False):
    log = load_accel_record(log_file)
    x, y, z = positions(log)
    # t = time_values(log)
    plt.plot(x, z, 'r')
    plt.show()



def read_and_show_ang_vel_log(log_file: str, show_filtered: bool  = True):
    log = load_accel_record(log_file)
    x, y, z = ang_velocities(log)
    t = time_values(log)

    if show_filtered:
        _figure, _ax = plt.subplots(2)
        _ax[0].plot(t, x, 'r')
        _ax[0].plot(t, y, 'g')
        _ax[0].plot(t, z, 'b')
        _ax[0].legend([r'$v_{\alpha}$', r'$v_{\beta}$', r'$v_{\gamma}$'], loc='upper left')
        _ax[0].set_xlabel("$t,[sec]$")
        _ax[0].set_ylabel("$v(t),[{grad} / {sec}]$")
        _ax[0].set_title("raw angles velocities")
        ##########################
        filter_ = RealTimeFilter()
        filter_.mode = 2
        filter_.window_size = 3
        filter_.mode = 2
        filter_.kalman_error = 0.5
        filter_.k_arg = 0.01
        _ax[1].plot(t, [filter_.filter(xi) for xi in x], 'r')
        filter_.clean_up()
        _ax[1].plot(t, [filter_.filter(xi) for xi in y], 'g')
        filter_.clean_up()
        _ax[1].plot(t, [filter_.filter(xi) for xi in z], 'b')
        _ax[1].legend([r'$v_{\alpha}$', r'$v_{\beta}$', r'$v_{\gamma}$'], loc='upper left')
        _ax[1].set_xlabel("$t,[sec]$")
        _ax[1].set_ylabel("$v(t),[{grad} / {sec}]$")
        _ax[1].set_title("filtered angles velocities")
        plt.show()
        return

    _figure, _ax = plt.subplots(1)
    _ax[0].plot(t, x, 'r')
    _ax[0].plot(t, y, 'g')
    _ax[0].plot(t, z, 'b')
    _ax[0].legend([r'$v_{\alpha}$', r'$v_{\beta}$', r'$v_{\gamma}$'], loc='upper left')
    _ax[0].set_xlabel("$t,[sec]$")
    _ax[0].set_ylabel("$v(t),[{grad} / {sec}]$")
    _ax[0].set_title("raw angles velocities")
    plt.show()


def mask(shift: int) -> int:
    m = 0
    for i in range(32):
        if shift <= i:
            m |= 1 << i
    return m


if __name__ == "__main__":
    #acc = Accelerometer()
    #time.sleep(60)
    #acc.calibrate(30)
    #read_and_save_data("building_way.json", acc, 180.0, 0.001, mode=4)

    #log = load_accel_record('model.json')
    #dt = [p.time for p in log.way_points]
    #plt.plot(dt)
    #plt.show()
    # read_with_time_interval_example()
    read_and_show_ang_vel_log('building_way.json')
    #read_and_save_with_time_interval_example('model.json', read_time=30)
    #read_and_show_position_log('model.json')
    # read_and_show_accel_log('model.json')
    # read_and_show_accel_log('model.json')
    #
