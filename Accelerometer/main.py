from Accelerometer.accelerometer_core.accelerometer_bno055 import AccelerometerBNO055
from Accelerometer.accelerometer_core.accelerometer_integrator import AccelIntegrator

# if __name__ == "__main__":
#     integrator = AccelIntegrator("accelerometer_core/accelerometer_records/the newest/building_way.json")
#     # integrator = AccelIntegrator("accelerometer_core/accelerometer_records/record_bno_test.json")
#     integrator.integrate()
#     integrator.show_results_xz()
#     integrator.show_path()
from Accelerometer.accelerometer_core.accelerometer_recording import record_imu_log

from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU, CALIBRATION_MODE
from Utilities.Device import START_MODE
from Utilities.Geometry import Vector2
import time

UART_START_MESSAGE = b'$#'
UART_END_MESSAGE = b'#$'
UART_EMPTY_MESSAGE = b'$##$'


def write_package(serial_port, message: bytes):
    """
    Пишет в UART порт сообщение в виде массива из HEX значений.  Признаками начала и конца b'$#', b'#$'
     выставляются автоматически.
    :param serial_port:
    :param message:
    """
    serial_port.write(UART_START_MESSAGE)
    serial_port.write(message)
    serial_port.write(UART_END_MESSAGE)
    print(UART_START_MESSAGE + message + UART_END_MESSAGE)


if __name__ == "__main__":
    acc = IMU()
    acc.update()
    while not acc.is_complete:
        acc.update()
    # acc.use_filtering = True
    # acc.record('record_bno_test.json')  # запись в файл
    # acc.calibrate_request()
    # record_imu_log("acc.json", acc, 20, 0.033)
    path_list = [Vector2(0, 0), Vector2(1, 270), Vector2(1, 270), Vector2(1, 270)]
    dist = 0.0
    path_list.reverse()
    position = acc.position
    target = path_list.pop()
    # write_package(acc.accelerometer.device, f"{1},{0}".encode())
    while len(path_list) != 0:
        acc.update()
        print(acc.accelerometer)
        time.sleep(0.5)
        dist += (acc.position - position).magnitude() + 0.00033
        # print(dist)
        position = acc.position
        if dist >= target.x:
            # write_package(acc.accelerometer.device, f"{1},{int(target.y)}".encode())
            dist = 0.0
            target = path_list.pop()
    # write_package(acc.accelerometer.device, f"{1},{400}".encode())
