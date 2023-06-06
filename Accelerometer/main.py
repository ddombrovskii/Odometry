from Accelerometer.accelerometer_core.accelerometer_bno055 import AccelerometerBNO055
import time
from Accelerometer.accelerometer_core.accelerometer_integrator import AccelIntegrator

# if __name__ == "__main__":
#     integrator = AccelIntegrator("accelerometer_core/accelerometer_records/the newest/building_way.json")
#     # integrator = AccelIntegrator("accelerometer_core/accelerometer_records/record_bno_test.json")
#     integrator.integrate()
#     integrator.show_results_xz()
#     integrator.show_path()

from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU
if __name__ == "__main__":
    acc = AccelerometerBNO055()
    # acc.use_filtering = True
    # acc.record('record_bno_test.json')  # запись в файл
    # acc.calibrate_request()
    for _ in range(32):
        acc.read_request()
        print(acc)
        time.sleep(.50)
