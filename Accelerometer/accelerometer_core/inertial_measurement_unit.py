# from accelerometer_core.accelerometer import Accelerometer
# from accelerometer_core.utilities import LoopTimer
# from accelerometer_core.utilities import Vector3
import time
import msvcrt

from .utilities.loop_timer import LoopTimer
from .accelerometer import Accelerometer
from .utilities.vector3 import Vector3
from typing import List, Tuple
import sys


# messages
BEGIN_MODE_MESSAGE   = 0
RUNNING_MODE_MESSAGE = 1
END_MODE_MESSAGE     = 2

# modes
CALIBRATION_MODE   = 0
BASIS_COMPUTE_MODE = 1
INTEGRATE_MODE     = 2
STOP_MODE          = 3
EXIT_MODE          = 4
START_UP_MODE      = 5
ANY_MODE           = -1


def progres_bar(val: float, max_chars: int = 55, char_progress: str = '#', char_stand_by: str = '.' ):
    filler_l = int(min(max(0.0, val), 1.0) * max_chars)  # max_chars - title chars count
    filler_r = max_chars - filler_l
    sys.stdout.write(f'\r|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|')
    if filler_r == 0:
         sys.stdout.write('\n')


# TODO Подумать как можно организовать ввод с клавиатуры без cv2.waitKey(timeout)
#  вроде Keyboard либа может решить эту проблему
# TODO проверить адекватность работы LoopTimer
# TODO что сделать с синхронизацией, если например камера работает в одном потоке,
#  а мы запрашиваем изображение или ещё что из другого потока
class IMU:
    def __init__(self):  # , forward: Vector3 = None):
        super().__init__()
        self._accelerometer: Accelerometer
        try:
            self._accelerometer = Accelerometer()
        except RuntimeError as err:
            print(err.args)
            exit(0)
        self._timer: LoopTimer = LoopTimer(0.01)
        self._mode_time = 0.0
        self._d_time    = 1e-6
        # время простоя перед запуском
        self._start_time:   float = 1.0
        # время калибровки
        self._calib_time:     float = 2.0
        # время ...
        self._trust_acc_time: float = 0.1
        # self._timer: LoopTimer = LoopTimer(0.001)
        self._vel: Vector3   = Vector3(0.0, 0.0, 0.0)
        self._pos: Vector3   = Vector3(0.0, 0.0, 0.0)
        self._messages: List[Tuple[int, int]] = []
        self._curr_mode: int = -1
        self._prev_mode: int = -1
        self._callbacks =  {CALIBRATION_MODE: self._calibrate,
                            BASIS_COMPUTE_MODE: self._compute_basis,
                            INTEGRATE_MODE: self._integrate,
                            STOP_MODE: self._pause,
                            EXIT_MODE: self._exit,
                            START_UP_MODE: self._start}
        self._emit_message(START_UP_MODE, BEGIN_MODE_MESSAGE)

    @property
    def start_time(self) -> float:
        return self._start_time

    @start_time.setter
    def start_time(self, value: float) -> None:
        self._start_time = min(max(0.125, value), 60)

    @property
    def calib_time(self) -> float:
        return self._calib_time

    @calib_time.setter
    def calib_time(self, value: float) -> None:
        self._calib_time = min(max(0.125, value), 60)

    @property
    def trust_acc_time(self) -> float:
        """
        Интервал времени для проверки наличия изменения в измерении вектора ускорения
        Если по истечению времени изменений не произошло, то считаем, что акселерометр неподвижен
        """
        return self._trust_acc_time

    @trust_acc_time.setter
    def trust_acc_time(self, value: float) -> None:
        """
        Интервал времени для проверки наличия изменения в измерении вектора ускорения
        Если по истечению времени изменений не произошло, то считаем, что акселерометр неподвижен
        """
        # with self._lock:
        self._trust_acc_time = min(max(0.05, value), 1.0)

    @property
    def k_gravity(self) -> float:
        """
        Параметр комплиментарного фильтра для определения углов поворота
        """
        return self._accelerometer.k_accel

    @k_gravity.setter
    def k_gravity(self, value: float) -> None:
        """
        Параметр комплиментарного фильтра для определения углов поворота
        """
        # with self._lock:
        self._accelerometer.k_accel = value

    @property
    def omega(self) -> Vector3:
        """
        Угловые скорости
        """
        return self._accelerometer.omega

    @property
    def angles(self) -> Vector3:
        """
        Углы поворота
        """
        return self._accelerometer.angle

    @property
    def acceleration_calib(self) -> Vector3:
        """
        Калибровочные значения ускорения свободного падения
        """
        return self._accelerometer.acceleration_calib

    @property
    def omega_calib(self) -> Vector3:
        """
        Калибровочные значения угловых скоростей
        """
        return self._accelerometer.omega_calib

    @property
    def acceleration(self) -> Vector3:
        """
        Текущее ускорение в собственной системе координат
        """
        return self._accelerometer.acceleration

    @property
    def velocity(self) -> Vector3:
        """
        Текущая скорость в мировой системе координат
        """
        return self._vel

    @property
    def position(self) -> Vector3:
        """
        Текущее положение в мировой системе координат
        """
        return self._pos

    @property
    def delta_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self._accelerometer.delta_t

    @property
    def curr_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self._accelerometer.curr_t

    @property
    def prev_t(self) -> float:
        """
        Последнее время, когда было измерено ускорение
        """
        return self._accelerometer.prev_t

    def calibrate(self, timeout: float = None, forward: Vector3 = None):
        """
        Калибровка акселерометра
        """
        if self._curr_mode == CALIBRATION_MODE:
            return
        self._calib_time = self._calib_time if timeout is None else timeout
        self._emit_message(self._curr_mode, END_MODE_MESSAGE)
        self._emit_message(CALIBRATION_MODE, BEGIN_MODE_MESSAGE)

    def rebuild_basis(self):
        pass

    def integrate(self):
        """
        Чтение данных акселерометра
        """
        self._emit_message(self._curr_mode, END_MODE_MESSAGE)
        self._emit_message(INTEGRATE_MODE, BEGIN_MODE_MESSAGE)

    def pause(self):
        if self._curr_mode != STOP_MODE:
            self._emit_message(STOP_MODE, BEGIN_MODE_MESSAGE)
        return

    def resume(self):
        if self._curr_mode == STOP_MODE:
            self._emit_message(STOP_MODE, END_MODE_MESSAGE)
        return

    def exit(self):
        self._emit_message(EXIT_MODE, BEGIN_MODE_MESSAGE)
        self._emit_message(self._curr_mode, END_MODE_MESSAGE)

    def _emit_message(self, mode_info, mode_state):
        # Если сообщение для всех режимов
        if mode_info == -1:
            self._messages.insert(0, (mode_info, mode_state))
            return
        # Если сообщение для ткущего режима
        if mode_info == self._curr_mode:
            self._messages.insert(0, (mode_info, mode_state))
            return
        #
        self._prev_mode = self._curr_mode
        self._curr_mode = mode_info
        self._messages.insert(0, (mode_info, mode_state))

    def _integrate(self, message: int) -> bool:
        if message == 0:
            self._mode_time = 0.0
            print(f"\n|----------Accelerometer read and integrate...----------|\n"
                    f"|-------------------Please stand by...------------------|")
            return True

        if message == 1:
            self._mode_time += self._d_time

            progres_bar((self._mode_time / 3.0) % 1.0, 55, '|', '_')

            if not self._accelerometer.read_measurements():
                return False

            dt    = self.delta_t

            if (self._accelerometer.acceleration - self._accelerometer.acceleration_prev).magnitude() > \
                    self._accelerometer.acceleration_noize_level:
                self._mode_time = 0.0
            else:
                self._mode_time += self.delta_t

            r, u, f =  self._accelerometer.basis.right_up_front

            a = self._accelerometer.acceleration_local_space

            self._vel += (r * a.x + u * a.y + f * a.z) * dt if self._mode_time >= self._trust_acc_time else Vector3(0.0, 0.0, 0.0)
            # интегрирование пути
            self._pos += (r * self._vel.x + u * self._vel.y + f * self._vel.z) * dt
            # sys.stdout.write(f'\n|"omega":{self.omega}|')
            # sys.stdout.write(f'|"angle":{self.angles}|\n')
            # sys.stdout.write(f'|"accel":{self.acceleration}|\n')
            # sys.stdout.write(f'|"vel"  :{self.velocity}|\n')
            # sys.stdout.write(f'|"pos"  :{self.position}|\n')
            # sys.stdout.write('\r\b\b\r')
        if message == 2:
            pass

    def _compute_basis(self) -> bool:
        if self._mode != BASIS_COMPUTE_MODE:
            return False
        self._mode = INTEGRATE_MODE
        # self._basis = Matrix4.build_basis(self.acceleration, self._basis.front)
        # self._ang   = Quaternion.from_rotation_matrix(self._basis).to_euler_angles()
        return True

    def _start(self, message: int) -> bool:
        if message == 0:
            print(f'\n|----------------Accelerometer start up...--------------|\n'
                  f'|-------------Please stand by and hold still...---------|')
            self._mode_time = 0
            return True

        if message == 1:
            self._mode_time += self._d_time
            progres_bar(self._mode_time / self._start_time, 55, '|', '_')
            if self._mode_time >= self._start_time:
                self.calibrate()
                return False
            return True

        if message == 2:
            self.calibrate()
            return False
        return False

    def _calibrate(self, message: int) -> bool:
        if message == 0:
            print(f"\n|--------------Accelerometer calibrating...-------------|\n"
                  f"|-------------Please stand by and hold still...---------|")
            self._mode_time = 0.0
            return True

        if message == 1:
            self._mode_time += self._d_time
            progres_bar(self._mode_time / self._calib_time, 55, '|', '_')

            if self._mode_time >= self._calib_time:
                self._accelerometer.calibrate(True, self._accelerometer.basis.front)
                self._mode_time = 0.0
                self._emit_message(self._curr_mode, END_MODE_MESSAGE)
                # print(f"|------------------Calibration is done------------------|")
                return False

            if not self._accelerometer.calibrate(False, self._accelerometer.basis.front):
                self._mode_time = 0.0
                self._emit_message(self._curr_mode, END_MODE_MESSAGE)
                # print(f"|---------------Calibration is interrupted--------------|")
                return False

        if message == 2:
            self._accelerometer.calibrate(True, self._accelerometer.basis.front)
            self._mode_time = 0.0
            self._emit_message(INTEGRATE_MODE, BEGIN_MODE_MESSAGE)
            return False
        return False

    def _wait_for_messages(self, wait_time_in_milliseconds: int = 5):
        # if not msvcrt.kbhit():
        #    return
        #    # key = msvcrt.getch()
        key_code = -1  # msvcrt.getch()  # cv.waitKey(wait_time_in_milliseconds)
        if key_code == -1:
            self._emit_message(self._curr_mode, RUNNING_MODE_MESSAGE)
            return
        # приостановка любого выполняющегося режима
        if key_code == ord('p'):
            if self._curr_mode != STOP_MODE:
                self.pause()
                return
            self.resume()
            return
        # Завершение работы режима
        if key_code == ord('q'):
            self.integrate()
            return
        # Выход из камеры
        if key_code == 27:
            self.exit()
            return
        # Включение режима калибровки
        if key_code == ord('c'):
            self.calibrate()
            return
        # Включение режима записи
        # if key_code == ord('r'):
        #    self.record_video()

    def _exit(self, message: int) -> bool:
        if message == START_UP_MODE:
            return False

        if message == RUNNING_MODE_MESSAGE:
            return False

        if message == END_MODE_MESSAGE:
            return False

        return False

    def _pause(self, message: int) -> bool:
        if message == BEGIN_MODE_MESSAGE:
            print(f"\n|---------------Accelerometer stop...---------------|")
            return True

        if message == RUNNING_MODE_MESSAGE:
            return True

        if message == END_MODE_MESSAGE:
            self._emit_message(self._prev_mode, RUNNING_MODE_MESSAGE)
            return False

        return False

    def update(self):
        with self._timer:
            if not self._timer.is_loop:
                return
            self._wait_for_messages()
            while len(self._messages) != 0:
                mode_info, mode_arg = self._messages.pop()

                if mode_info == ANY_MODE:
                    for mode_function in self._callbacks.values():
                        mode_function.__call__(mode_arg)
                    continue

                if mode_info in self._callbacks:
                    self._callbacks[mode_info].__call__(mode_arg)
                    continue

    def reset(self):
        # with self._lock:
        self._accelerometer.reset()
        self._vel = Vector3(0.0, 0.0, 0.0)
        self._pos = Vector3(0.0, 0.0, 0.0)
        self._mode_time = 0.0

    def restart(self):
        self._emit_message(self._curr_mode, END_MODE_MESSAGE)
        self._emit_message(START_UP_MODE, BEGIN_MODE_MESSAGE)
        self.reset()

    def run(self):
        """ This function running in separated thread"""
        while self._curr_mode != EXIT_MODE:
            self.update()
            self._d_time = max(self._timer.last_loop_time,  self._timer.timeout)


# mport os
# os.system("")
# LINE_UP = '\033[1A\b'
# LINE_CLEAR = '\033[2K'
# COLOR = {
#     "HEADER": "\033[95m",
#     "BLUE": "\033[94m",
#     "GREEN": "\033[92m",
#     "RED": "\033[91m",
#     "ENDC": "\033[0m",
# }

#print(COLOR["HEADER"], "Testing Green!!", COLOR["ENDC"])


