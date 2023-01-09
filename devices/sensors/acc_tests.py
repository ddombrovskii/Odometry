import time

from devices.sensors.accelerometer import Accelerometer
from devices.sensors.accelerometer_device import AccelerometerDevice


def accelerometer_test():
    accelerometer = Accelerometer()

    print(accelerometer)

    accelerometer.use_filtering = True

    accelerometer.calibrate()

    with open("../sensors_utils/still.json", 'wt') as out_put:
        print("{\n\"way_points\":[", file=out_put)
        for _ in range(2048):
            accelerometer.read_accel_measurements()
            print("\t{\n", file=out_put)
            print(f"\t\"angles_velocity\": {accelerometer.angles_velocity},", file=out_put)
            print(f"\t\"angles\"         : {accelerometer.angles},", file=out_put)
            print(f"\t\"acceleration\"   : {accelerometer.acceleration},", file=out_put)
            print(f"\t\"velocity\"       : {accelerometer.velocity},", file=out_put)
            print(f"\t\"position\"       : {accelerometer.position},", file=out_put)
            print(f"\t\"time_delta\"     : {accelerometer.accel_dt},", file=out_put)
            print(f"\t\"time\"           : {accelerometer.accel_t}", file=out_put)
            print("\t},", file=out_put)
        print("\t]\n}", file=out_put)
    with open('accelerometer_settings.json', 'wt') as out_put:
        print(accelerometer, file=out_put)


def accelerometer_device_data_recording():
    acc = AccelerometerDevice()
    acc.update_rate = 1.0 / 30.0
    acc.life_time = 300  # 1 минута на запись
    acc.enable_logging = True
    acc.start()
    acc.join()


def accelerometer_device_data_reading():
    acc = AccelerometerDevice()
    acc.update_rate = 1.0 / 30.0
    acc.life_time = 1  # 1 минута на запись
    acc.start()
    while acc.alive:
        # print(f"{acc.velocity}")
        time.sleep(0.1)
        print(f"{{\n\t\"t\" = {acc.time_value},\n\t\"o\" = {acc.angle_velocities},\n\t\"a\" = {acc.acceleration},\n\t\"v\" ="
              f" {acc.velocity},\n\t\"p\" = {acc.position}\n}}")

    acc.join()


def accelerometer_device_test():
    accelerometer_device_data_reading()
    accelerometer_device_data_recording()


if __name__ == "__main__":
    accelerometer_test()
    # accelerometer_device_test()