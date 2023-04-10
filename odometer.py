from Motion.motion_controller import MotionController
from Utilities import Device, BEGIN_MODE_MESSAGE, END_MODE_MESSAGE, DeviceMessage, RUNNING_MODE_MESSAGE
from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU
from Utilities.device import DISCARD_MODE_MESSAGE, START_MODE
from Cameras.camera_cv import CameraCV
from typing import List
import threading
import asyncio

COMPOSITE_MODE_ODOMETER = 10
INERTIAL_MODE_ODOMETER = 11
OPTICAL_MODE_ODOMETER = 12
STAN_BY_MODE_ODOMETER = 13


class Odometer(Device):
    class CommandsInput(threading.Thread):
        def __init__(self, input_cbk=None, name='keyboard-input-thread'):
            self.input_cbk = input_cbk
            super(Odometer.CommandsInput, self).__init__(name=name)

        def run(self):
            while True:
                value = input()
                if value == "exit":
                    break
                self.input_cbk(value)  # waits to get input + Return
            self.input_cbk("exit")

    def __init__(self):
        super().__init__()
        self._input = Odometer.CommandsInput(lambda c: self.append_command(c))
        self._commands_buffer = []
        self._camera: CameraCV = CameraCV()
        self._imu: IMU = IMU()
        self._controller: MotionController = MotionController()
        self._camera.update_time = 1.0
        self.update_time = min(self._imu.update_time, self._camera.update_time, self._controller.update_time) * 0.75
        self._controller.enable_logging = False
        self._camera.enable_logging = False
        self._imu.enable_logging = False
        self.register_callback(STAN_BY_MODE_ODOMETER, self._stand_by_mode)
        self.register_callback(OPTICAL_MODE_ODOMETER, self._optical_odometer)
        self.register_callback(INERTIAL_MODE_ODOMETER, self._inertial_odometer)
        self.register_callback(COMPOSITE_MODE_ODOMETER, self._composite_odometer)

    def on_exit(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._camera.exit()
            self._controller.exit()
            self._imu.exit()
        return END_MODE_MESSAGE

    def on_start(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._camera.begin_mode(START_MODE)
            self._imu.begin_mode(START_MODE)
            self._controller.begin_mode(START_MODE)
            return END_MODE_MESSAGE
        if message == END_MODE_MESSAGE:
            self.begin_mode(STAN_BY_MODE_ODOMETER)
            return DISCARD_MODE_MESSAGE

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
            self._controller.pause()

        if message == END_MODE_MESSAGE:
            self._camera.resume()
            self._imu.resume()
            self._controller.resume()

        return DISCARD_MODE_MESSAGE

    async def run_async(self):
        while True:
            self._execute_command()
            await self.update()
            complete = True
            complete &= self._camera.is_complete
            complete &= self._imu.is_complete
            complete &= self._controller.is_complete
            complete &= self.is_complete
            if complete:
                break
        print("done...")

    async def _async_run(self):
        tasks = [self.run_async(), self._camera.run_async(), self._imu.run_async(),  self._controller.run_async()]
        await asyncio.gather(*tasks)

    def run(self):
        t = threading.Thread(target=lambda: asyncio.run(self._async_run()))
        t.start()
        self._input.start()
        self._input.join()
        t.join()

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
            # TODO any post process
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == END_MODE_MESSAGE:
            self._camera.end_slam()
            self._imu.end_record()
            return DISCARD_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def _stand_by_mode(self, message: DeviceMessage) -> int:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self._camera.show_video()
            self._imu.integrate()
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == RUNNING_MODE_MESSAGE:
            # TODO any post process
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == END_MODE_MESSAGE:
            # self._camera.end_slam()
            # self._imu.end_record()
            return DISCARD_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def append_command(self, command: str):
        self._commands_buffer.append(command)

    def _execute_command(self) -> bool:
        if len(self._commands_buffer) == 0:
            return True
        command = self._commands_buffer.pop()
        self._tokenize_command(command)
        if command == "exit":
            self.exit()
            return False
        return True

    def _tokenize_camera_command(self, command: List[str]):
        if len(command) == 0:
            return
        if self._camera is None:
            self.send_log_message(f"Command \"camera {' '.join(v for v in command)}\" thrown. Camera is none...\n")
            return
        if command[0] == "exit":
            self._camera.exit()
            return

        if command[0] == "pause":
            self._camera.pause()
            return
        if command[0] == "reset":
            self._camera.reset()
            return

        if command[0] == "reboot":
            self._camera.reboot()
            return

        if command[0] == "video":
            self._camera.show_video()
            return

        if command[0] == "slam":
            if len(command) == 1:
                self._camera.begin_slam()
            else:
                self._camera.end_slam() if command[1] != "stop" else self._camera.show_video()
            return

        if command[0] == "record":
            if len(command) == 1:
                self._camera.record_video()
            else:
                self._camera.record_video(command[1]) if command[1] != "stop" else self._camera.show_video()
            return

        if command[0] == "calibrate":
            if len(command) == 1:
                self._camera.calibrate()
            else:
                self._camera.calibrate(command[1])
            return

        self.send_log_message(f"Unknown command \"{command[0]}\"\n")

    def _tokenize_imu_command(self, command: List[str]):
        # global imu
        if len(command) == 0:
            return
        # if command[0] == "start":
        #     if imu is None:
        #         imu = IMU()
        #         imu.run()
        #     return
        if self._imu is None:
            self.send_log_message(f"Command \"camera {' '.join(v for v in command)}\" thrown. Camera is none...\n")
            return
        if command[0] == "exit":
            self._imu.exit()
            return
        if command[0] == "pause":
            self._imu.pause()
            return
        if command[0] == "reset":
            self._imu.reset()
            return
        if command[0] == "reboot":
            self._imu.reboot()
            return
        if command[0] == "integrate":
            self._imu.integrate()
            return
        if command[0] == "record":
            if len(command) == 1:
                self._imu.begin_record()
            else:
                self._imu.begin_record(command[1]) if command[1] != "stop" else self._imu.end_record()
            return
        if command[0] == "calibrate":
            if len(command) == 1:
                self._imu.calibrate()
            else:
                try:
                    self._imu.calibrate(float(command[1]))
                except ValueError as ex:
                    self.send_log_message("Second argument of imu calibration call has to be float value of time\n")
            return
        self.send_log_message(f"\nUnknown command \"{command[0]}\"")

    def _tokenize_odometer_command(self, command: List[str]):
        if len(command) == 0:
            return

        if command[0] == "stop":
            self._imu.end_record()
            self._camera.end_slam()

        if command[0] == "inertial":
            self._imu.integrate()
            self._imu.begin_record(command[1] if len(command) == 2 else None)

        if command[0] == "visual" or command[0] == "optical":
            self._camera.begin_slam(command[1] if len(command) == 2 else None)

        if command[0] == "composite":
            self._imu.integrate()
            self._imu.begin_record(command[1] if len(command) == 2 else None)
            self._camera.begin_slam(command[2] if len(command) == 3 else None)
            return
        self.send_log_message(f"\nUnknown command \"{command[0]}\"")

    def _tokenize_command(self, command: str):
        self.send_log_message(f"command {command}\n")

        command = command.split(' ')

        if command[0] == 'camera':
            self._tokenize_camera_command(command[1:])
            return

        if command[0] == 'imu':
            self._tokenize_imu_command(command[1:])
            return

        if command[0] == 'odometer':
            self._tokenize_odometer_command(command[1:])
            return


if __name__ == "__main__":
    odometer = Odometer()
    odometer.run()
