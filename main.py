from Accelerometer.accelerometer_core.inertial_measurement_unit import IMU
from Cameras.camera_cv import CameraCV
from typing import List
import threading


camera: CameraCV    = None
imu: IMU            = None
commands: List[str] = []
lock = threading.Lock()


def tokenize_camera_command(command: List[str]):
    global camera
    if len(command) == 0:
        return
    if command[0] == "start":
        if camera is None:
            camera = CameraCV()
            camera.run()
        return
    if camera is None:
        print(f"Command \"camera {' '.join(v for v in command)}\" thrown. Camera is none...")
        return
    if command[0] == "exit":
        camera.exit()
    if command[0] == "pause":
        camera.pause()
    if command[0] == "reset":
        camera.reset()
    if command[0] == "reboot":
        camera.reboot()
    if command[0] == "video":
        camera.show_video()
    if command[0] == "record":
        if len(command) == 1:
            camera.record_video()
        else:
            camera.record_video(command[1]) if command[1] != "stop" else camera.show_video()
    if command[0] == "calibrate":
        if len(command) == 1:
            camera.calibrate()
        else:
            camera.calibrate(command[1])
    print(f"Unknown command \"{command[0]}\"")


def tokenize_imu_command(command: List[str]):
    global imu
    if len(command) == 0:
        return
    if command[0] == "start":
        if imu is None:
            imu = IMU()
            imu.run()
        return
    if imu is None:
        print(f"Command \"camera {' '.join(v for v in command)}\" thrown. Camera is none...")
        return
    if command[0] == "exit":
        imu.exit()
    if command[0] == "pause":
        imu.pause()
    if command[0] == "reset":
        imu.reset()
    if command[0] == "reboot":
        imu.reboot()
    if command[0] == "integrate":
        imu.integrate()
    if command[0] == "record":
        if len(command) == 1:
            imu.begin_record()
        else:
            imu.begin_record(command[1]) if command[1] != "stop" else imu.end_record()
    if command[0] == "calibrate":
        if len(command) == 1:
            imu.calibrate()
        else:
            try:
                imu.calibrate(float(command[1]))
            except ValueError as ex:
                print("Second argument of imu calibration call has to be float value of time")

    print(f"Unknown command \"{command[0]}\"")


def tokenize_command(command: str):
    print(f"command {command}")

    command = command.split(' ')

    if command[0] == 'camera':
        tokenize_camera_command(command[1:])
        return

    if command[0] == 'imu':
        tokenize_imu_command(command[1:])
        return


class CommandsInput(threading.Thread):
    def __init__(self, input_cbk=None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(CommandsInput, self).__init__(name=name)

    def run(self):
        while True:
            value = input()
            if value == "exit":
                break
            self.input_cbk(value)  # waits to get input + Return
        self.input_cbk("exit")


if __name__ == '__main__':
    command_input = CommandsInput(tokenize_command)
    command_input.start()


