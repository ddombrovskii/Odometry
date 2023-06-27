from Motion.motion_controller import MotionController
from Utilities import Device, BEGIN_MODE_MESSAGE, END_MODE_MESSAGE, DeviceMessage, RUNNING_MODE_MESSAGE
from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU
from Utilities.Device.device import DISCARD_MODE_MESSAGE, START_MODE
from typing import List
import threading
import time

COMPOSITE_MODE_ODOMETER = 10
INERTIAL_MODE_ODOMETER = 11
OPTICAL_MODE_ODOMETER = 12
STAN_BY_MODE_ODOMETER = 13


class InertialOdometer(Device):
    class CommandsInput(threading.Thread):
        def __init__(self, input_cbk=None, name='keyboard-input-thread'):
            self.input_cbk = input_cbk
            super(InertialOdometer.CommandsInput, self).__init__(name=name)

        def run(self):
            while True:
                time.sleep(0.3333)
                value = input()
                if value == "exit":
                    break
                self.input_cbk(value)  # waits to get input + Return
            self.input_cbk("exit")

    def __init__(self):
        super().__init__()
        self._input = InertialOdometer.CommandsInput(lambda c: self.append_command(c))
        self._commands_buffer = []
        self._imu: IMU = IMU()
        self._controller: MotionController = MotionController()
        self.update_time = min(self._imu.update_time, self._controller.update_time) * 0.75
        self._controller.enable_logging = False
        self._imu.enable_logging = True
        self.register_callback(STAN_BY_MODE_ODOMETER, self._stand_by_mode)
        self.register_callback(INERTIAL_MODE_ODOMETER, self._inertial_odometer)

    def on_exit(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._controller.exit()
            self._imu.exit()
        return END_MODE_MESSAGE

    def on_start(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._imu.begin_mode(START_MODE)
            self._controller.begin_mode(START_MODE)
            return END_MODE_MESSAGE
        if message == END_MODE_MESSAGE:
            self.begin_mode(STAN_BY_MODE_ODOMETER)
            return DISCARD_MODE_MESSAGE

    def on_reboot(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._imu.reboot()
        return END_MODE_MESSAGE

    def on_reset(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._imu.reset()
        return END_MODE_MESSAGE

    def on_pause(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._imu.pause()
            self._controller.pause()

        if message == END_MODE_MESSAGE:
            self._imu.resume()
            self._controller.resume()

        return DISCARD_MODE_MESSAGE

    def _run(self):
        while True:
            self._execute_command()
            self.update()
            self._imu.update()
            # self._controller.update()
            complete = True
            complete &= self._imu.is_complete
            # complete &= self._controller.is_complete
            complete &= self.is_complete
            if complete:
                break
        print("done...")

    def run(self):
        process = threading.Thread(target=lambda: self._run())
        process.start()
        self._input.start()
        self._input.join()
        process.join()

    def _inertial_odometer(self, message: DeviceMessage) -> int:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self._imu.begin_record()
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == RUNNING_MODE_MESSAGE:
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == END_MODE_MESSAGE:
            self._imu.end_record()
            return DISCARD_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def _stand_by_mode(self, message: DeviceMessage) -> int:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            # self._imu.integrate()
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == RUNNING_MODE_MESSAGE:
            # TODO any post process
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == END_MODE_MESSAGE:
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

    def _tokenize_imu_command(self, command: List[str]):
        # global imu
        if len(command) == 0:
            return
        if self._imu is None:
            self.send_log_message(f"IMU Error::\"imu {' '.join(v for v in command)}\" thrown. Camera is none...\n")
            return
        if command[0] == "exit":
            self._imu.exit()
            return
        if command[0] == "pause":
            self._imu.resume()
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
                self.send_log_message(f"Begin recording IMU in file : {self._imu.tmp_file_name}")
            else:
                if command[1] != "stop":
                    self._imu.begin_record(command[1])
                    self.send_log_message(f"Begin recording IMU in file : {command[1]}")
                else:
                    self._imu.end_record()
                    self.send_log_message(f"End of recording")

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

        if command[0] == "record":
            self._imu.integrate()
            self._imu.begin_record(command[1] if len(command) == 2 else None)

        self.send_log_message(f"\nUnknown command \"{command[0]}\"")

    def _tokenize_command(self, command: str):
        self.send_log_message(f"command {command}\n")

        command = command.split(' ')
        if command[0] == 'help' or command[0] == 'info':
            self.send_log_message(f"|____________________________Inertial odometer info_____________________________|\n"
                                  f"|_______________________________IMU_commands_list_______________________________|\n"
                                  f"|_Command_code__|____Command_args____|___________Command_description____________|\n"
                                  f"| imu pause     |                    | Приостанавливает/возобновляет работу IMU |\n"
                                  f"| imu reset     |                    | Делает полный сброс IMU                  |\n"
                                  f"| imu reboot    |                    | Перезапускает IMU                        |\n"
                                  f"| imu integrate |                    | Режим интегрирования пути IMU            |\n"
                                  f"| imu record    | file_name or empty | Запись в файл измерений IMU              |\n"
                                  f"|_imu_calibrate_|_file_name_or_empty_|_Калибровка_IMU___________________________|\n"
                                  f"|_______________________________________________________________________________|\n"
                                  f"|_____________________________Common_commands_list______________________________|\n"
                                  f"| help/info     |                    | Информация о командах                    |\n"
                                  f"|_exit__________|____________________|_Завершение_работы________________________|\n"
                                  )
        if command[0] == 'imu':
            self._tokenize_imu_command(command[1:])
            return

        if command[0] == 'odometer':
            self._tokenize_odometer_command(command[1:])
            return


if __name__ == "__main__":
    odometer = InertialOdometer()
    # odometer._tokenize_command("odometer imu run test_record.json")
    odometer.run()
