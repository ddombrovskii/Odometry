# from accelerometer_core import Accelerometer
# from accelerometer_core.accelerometer_recording import record_accel_log, record_imu_log
# from accelerometer_core.inertial_measurement_unit import IMU

from Accelerometer.accelerometer_core import record_imu_log, Accelerometer, record_accel_log
from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU


def imu_recording(path: str = 'imu_path.json'):
    """
    Пример записи результатов работы инерциалки в файл
    """
    a = IMU()
    a.calibrate(30.0)
    record_imu_log(path, a, 180.0, 0.001)


def accelerometer_recording(path: str = 'accelerometer_path.json'):
    """
    Пример записи результатов работы акселерометра в файл
    """
    a = Accelerometer()
    a.calibrate(30.0)
    record_accel_log(path, a, 180.0, 0.001)


if __name__ == "__main__":
    accelerometer_recording()
    imu_recording()
