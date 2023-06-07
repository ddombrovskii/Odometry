from Accelerometer.accelerometer_core import record_imu_log
from Accelerometer.accelerometer_core.accelerometer_bno055 import AccelerometerBNO055
import time
from Accelerometer.accelerometer_core.accelerometer_integrator import AccelIntegrator

# if __name__ == "__main__":
#     integrator = AccelIntegrator("accelerometer_core/accelerometer_records/the newest/building_way.json")
#     # integrator = AccelIntegrator("accelerometer_core/accelerometer_records/record_bno_test.json")
#     integrator.integrate()
#     integrator.show_results_xz()
#     integrator.show_path()

from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU, CALIBRATION_MODE
from Utilities import START_MODE

if __name__ == "__main__":
    acc = IMU()
    while acc.mode_active(START_MODE) or acc.mode_active(CALIBRATION_MODE):
        acc.update()
    # acc.use_filtering = True
    # acc.record('record_bno_test.json')  # запись в файл
    # acc.calibrate_request()
    record_imu_log("acc.json", acc, 20, 0.033)
    for _ in range(32):
        acc.update()
        print(acc.accelerometer)
        time.sleep(.50)
