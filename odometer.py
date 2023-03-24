import asyncio

from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU
from Cameras.camera_cv import CameraCV
from Utilities import Device, BEGIN_MODE_MESSAGE, END_MODE_MESSAGE, DeviceMessage, RUNNING_MODE_MESSAGE
from Utilities.device import DISCARD_MODE_MESSAGE

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

    def on_exit(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._camera.exit()
            self._imu.exit()
        return END_MODE_MESSAGE

    def on_start(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._camera._start(BEGIN_MODE_MESSAGE)
            self._imu._start(BEGIN_MODE_MESSAGE)
        return END_MODE_MESSAGE

    def on_reboot(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._camera.reboot()
            self._imu.reboot()
        return END_MODE_MESSAGE

    def on_reset(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._camera.reset()
            self._imu.reset()
        return END_MODE_MESSAGE

    def on_pause(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._camera.pause()
            self._imu.pause()

        if message == END_MODE_MESSAGE:
            self._camera.resume()
            self._imu.resume()

        return DISCARD_MODE_MESSAGE

    async def _run(self):
        while not self.is_complete:
            # обновление состояния камеры
            if not self._camera.is_complete:
                await self._camera.update()
            # обновление инерциальной системы
            if not self._imu.is_complete:
                await self._imu.update()
            # обновление работы одометра
            await self.update()

    def run(self):
        asyncio.run(self._run())

    def _optical_odometer(self, message: DeviceMessage) -> int:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self._camera.begin_slam()
            self._imu.pause()
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == RUNNING_MODE_MESSAGE:
            # TODO read value and analyze
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == END_MODE_MESSAGE:
            self._camera.end_slam()
            self._imu.resume()
            return DISCARD_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def _inertial_odometer(self, message: DeviceMessage) -> int:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self._camera.end_slam()
            self._camera.pause()
            self._imu.begin_record()
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == RUNNING_MODE_MESSAGE:
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == END_MODE_MESSAGE:
            self._camera.resume()
            self._imu.end_record()
            return DISCARD_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def _composite_odometer(self, message: DeviceMessage) -> int:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self._camera.begin_slam()
            self._imu.begin_record()
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == RUNNING_MODE_MESSAGE:
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == END_MODE_MESSAGE:
            self._camera.end_slam()
            self._imu.end_record()
            return DISCARD_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE
