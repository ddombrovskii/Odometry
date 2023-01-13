from mpu6050 import Accelerometer


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


if __name__ == "__main__":
    accelerometer_test()
