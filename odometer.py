from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU
from Cameras.camera_cv import CameraCV
from Utilities import Device, BEGIN_MODE_MESSAGE, END_MODE_MESSAGE, DeviceMessage, RUNNING_MODE_MESSAGE

COMPOSITE_MODE_ODOMETER = 10
INERTIAL_MODE_ODOMETER = 11
OPTICAL_MODE_ODOMETER = 12


class Odometer(Device):
    def __init__(self):
        super().__init__()
        self._camera: CameraCV = CameraCV()
        self._imu: IMU = IMU()
        self.register_callback(OPTICAL_MODE_ODOMETER, self._optical_odometer)
        self.register_callback(INERTIAL_MODE_ODOMETER, self._inertial_odometer)
        self.register_callback(COMPOSITE_MODE_ODOMETER, self._composite_odometer)

    def on_exit(self, message: int) -> None:
        if message == BEGIN_MODE_MESSAGE:
            self._camera.exit()
            self._imu.exit()

    def on_start(self, message: int) -> None:
        if message == BEGIN_MODE_MESSAGE:
            self._camera._start(BEGIN_MODE_MESSAGE)
            self._imu._start(BEGIN_MODE_MESSAGE)

    def on_reboot(self, message: int) -> None:
        if message == BEGIN_MODE_MESSAGE:
            self._camera.reboot()
            self._imu.reboot()

    def on_reset(self, message: int) -> None:
        if message == BEGIN_MODE_MESSAGE:
            self._camera.reset()
            self._imu.reset()

    def on_pause(self, message: int) -> None:
        if message == BEGIN_MODE_MESSAGE:
            self._camera.pause()
            self._imu.pause()

        if message == END_MODE_MESSAGE:
            self._camera.resume()
            self._imu.resume()

    def _optical_odometer(self, message: DeviceMessage):
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self.send_message(message.mode, RUNNING_MODE_MESSAGE)
            pass

        if message.mode_arg == RUNNING_MODE_MESSAGE:
            self.send_message(message.mode, END_MODE_MESSAGE)
            pass

        if message.mode_arg == END_MODE_MESSAGE:
            pass

    def _inertial_odometer(self, message: DeviceMessage):
        pass

    def _composite_odometer(self, message: DeviceMessage):
        pass
