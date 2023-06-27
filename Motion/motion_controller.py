from Utilities import Device, DeviceMessage, RUNNING_MODE_MESSAGE, BEGIN_MODE_MESSAGE
from Utilities.Geometry import Vector2
from Motion.motor_controller import MotorController
from Utilities.Device.device import DISCARD_MODE_MESSAGE
from typing import List, Tuple

MANUAL_MODE = 7
WALK_ALONG_TRAJECTORY_MODE = 8
SLAVE_MODE = 9


class MotionController(Device):
    def __init__(self, pin_r: int = None, pin_l: int = None, pin_r_pwm: int = None, pin_l_pwm: int = None,
                 pwm_f=400):
        super().__init__()
        self.softness: float = 0.01
        self._r_motor: MotorController = MotorController(dir_pin=17 if pin_r is None else pin_r,
                                                         pwm_pin=16 if pin_r_pwm is None else pin_r_pwm, freq=pwm_f)
        self._l_motor: MotorController = MotorController(dir_pin=18 if pin_l is None else pin_l,
                                                         pwm_pin=19 if pin_l_pwm is None else pin_l_pwm, freq=pwm_f)
        # print(self._r_motor)
        # print(self._l_motor)
        self._way_points: List[Vector2] = []
        self._way_points_src: str = None
        self._p1 = None
        self._p2 = None
        self._p3 = None
        self._t  = 0.0
        self._angle: float = 0.0
        self.update_time = 1.0 / 60
        self.register_callback(MANUAL_MODE,  self._on_manual_control)
        self.register_callback(WALK_ALONG_TRAJECTORY_MODE,  self._on_trajectory)

    @property
    def zero_threshold(self) -> Tuple[float, float]:
        return self._l_motor.zero_threshold, self._r_motor.zero_threshold

    @zero_threshold.setter
    def zero_threshold(self, val: Tuple[float, float]) -> None:
        self._l_motor.zero_threshold, self._r_motor.zero_threshold = val[0], val[1]

    @property
    def l_motor(self) -> MotorController:
        return self._l_motor

    @property
    def r_motor(self) -> MotorController:
        return self._r_motor

    def manual(self):
        self.begin_mode(MANUAL_MODE)

    def move_along_trajectory(self, file_src: str = None):
        self.begin_mode(WALK_ALONG_TRAJECTORY_MODE)
        self._way_points_src = "" if file_src is None else file_src

    def on_start(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self.manual()
            return RUNNING_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def _on_manual_control(self, message: DeviceMessage) -> int:
        # print(f"|l: {self.l_motor.pwm_ff:5} | r: {self.r_motor.pwm_ff:5}|")
        if message.is_begin:
            self.r_motor.pwm_ff = 0.0
            self.l_motor.pwm_ff = 0.0
            return message.run
        if message.is_running:
            alpha = (self._l_motor.pwm_ff - self._r_motor.pwm_ff) * self.softness
            self.l_motor.pwm_ff -= alpha
            self.r_motor.pwm_ff += alpha
            return message.run
        if message.is_end:
            self.r_motor.pwm_ff = 0.0
            self.l_motor.pwm_ff = 0.0
            return message.discard
        return message.discard

    def on_messages_wait(self, key_code: int) -> None:
        if not self.mode_active(MANUAL_MODE):
            return
        if key_code == 119 or key_code == 246:
            self.l_motor.pwm_ff += 0.05
            self.r_motor.pwm_ff += 0.05
            return
        if key_code == 115 or key_code == 251:
            self.l_motor.pwm_ff -= 0.05
            self.r_motor.pwm_ff -= 0.05
            return
        if key_code == 97 or key_code == 244:
            self.l_motor.pwm_ff += 0.05
            self.r_motor.pwm_ff -= 0.05
            return
        if key_code == 100 or key_code == 226:
            self.l_motor.pwm_ff -= 0.05
            self.r_motor.pwm_ff += 0.05
            return
        if key_code == 32:
            self.l_motor.pwm_ff = 0.0
            self.r_motor.pwm_ff = 0.0
        return

    def _on_trajectory(self, message: DeviceMessage) -> int:
        if message.is_begin:
            self._l_motor.pwm_ff = 0.0
            self._r_motor.pwm_ff = 0.0
            self._way_points.clear()
            with open(self._way_points_src, 'rt') as input_points:
                for line in input_points:
                    try:
                        line = line.strip()
                        line = line.split(' ')
                        self._way_points.append(Vector2(float(line[0]), float(line[1])))
                    except RuntimeError as err:
                        continue
                    self._way_points.reverse()
            if len(self._way_points) < 3:
                self.manual()
                return message.end
            self._p1 = self._way_points.pop()
            self._p2 = self._way_points.pop()
            self._p3 = self._way_points.pop()
            return message.run

        if message.is_running:
            if self._t >= 1.0:
                self._t = 0.0
                self._p1 = self._p2
                self._p2 = self._p3
                if len(self._way_points) == 0:
                    return message.end
                self._p3 = self._way_points.pop()
                self._angle = Vector2.cross((self._p2 - self._p1).normalized(),
                                            (self._p3 - self._p2).normalized())
                self.l_motor.pwm_ff -= self._angle
                self.r_motor.pwm_ff += self._angle

            if abs(self._angle) < 0.05:
                alpha = (self.l_motor.pwm_ff - self.r_motor.pwm_ff) * self.softness
                self.l_motor.pwm_ff -= alpha
                self.r_motor.pwm_ff += alpha

            self._t += self.update_time
            return message.run

        if message.is_end:
            self._l_motor.pwm_ff = 0.0
            self._r_motor.pwm_ff = 0.0
            return message.discard
        return message.discard


if __name__ == "__main__":
    import cv2 as cv
    cv.namedWindow("accelerometer", cv.WINDOW_NORMAL)
    imu = MotionController()
    imu.run()
