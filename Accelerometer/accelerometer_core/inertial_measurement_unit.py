from accelerometer_core.accelerometer import Accelerometer
from accelerometer_core.utilities import LoopTimer
from accelerometer_core.utilities import Vector3
import threading
import sys

CALIBRATION_MODE   = 0
BASIS_COMPUTE_MODE = 1
INTEGRATE_MODE     = 2
STOP_MODE          = 3
EXIT_MODE          = 4
WARM_UP_MODE       = 5


def progres_bar(val: float, max_chars: int = 55, char_progress: str = '#', char_stand_by: str = '.' ):
    filler_l = int(min(max(0.0, val), 1.0) * max_chars)  # max_chars - title chars count
    filler_r = max_chars - filler_l
    sys.stdout.write(f'\r|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|')
    if filler_r == 0:
         sys.stdout.write('\n')


class IMU:  #(threading.Thread):
    def __init__(self):  # , forward: Vector3 = None):
        super().__init__()
        self._lock = threading.Lock()
        self._accelerometer: Accelerometer
        try:
            self._accelerometer = Accelerometer()
        except RuntimeError as err:
            print(err.args)
            exit(0)
        self._time = 0.0
        self._dtime = 1e-6
        # время простоя перед запуском
        self._warm_up_time:   float = 1.0
        # время калибровки
        self._calib_time:     float = 2.0
        # время ...
        self._trust_acc_time: float = 0.1
        self._timer: LoopTimer = LoopTimer(0.001)
        self._mode: int = WARM_UP_MODE
        self._prev_mode: int = -1
        self._vel: Vector3   = Vector3(0.0, 0.0, 0.0)
        self._pos: Vector3   = Vector3(0.0, 0.0, 0.0)
        self._command: str = ""

    @property
    def warm_up_time(self) -> float:
        return self._warm_up_time

    @warm_up_time.setter
    def warm_up_time(self, value: float) -> None:
        # with self._lock:
        self._warm_up_time = min(max(0.125, value), 60)

    @property
    def calib_time(self) -> float:
        return self._calib_time

    @calib_time.setter
    def calib_time(self, value: float) -> None:
        # with self._lock:
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

    def calibrate(self, timeout: float = None, forward: Vector3 = None) -> bool:
        """
        Калибровка акселерометра
        """
        if self._mode == CALIBRATION_MODE:
            return False
        if self._mode == WARM_UP_MODE:
            return False
        # with self._lock:
        self._calib_time = self._calib_time if timeout is None else timeout
        self._mode = CALIBRATION_MODE
        if forward is None:
            return True
        return True

    def rebuild_basis(self) -> bool:
        if self._mode == CALIBRATION_MODE:
            return False
        # with self._lock:
        self._mode = BASIS_COMPUTE_MODE
        return True

    def read(self) -> bool:
        """
        Чтение данных акселерометра
        """
        if self._mode == CALIBRATION_MODE:
            return False
        # with self._lock:
        self._mode = INTEGRATE_MODE
        return True

    def _integrate(self) -> bool:

        if self._mode != INTEGRATE_MODE:
            return False

        if self._time == 0.0:
            print(f"\n|----------Accelerometer read and integrate...----------|\n"
                    f"|-------------------Please stand by...------------------|")

        progres_bar((self._time / 3.0) % 1.0, 55, '|', '_')

        if not self._accelerometer.read_measurements():
            return False

        dt    = self.delta_t

        self._time += self._dtime

        if (self._accelerometer.acceleration - self._accelerometer.acceleration_prev).magnitude() > \
                self._accelerometer.acceleration_noize_level:
            self._time = 0.0
        else:
            self._time += self.delta_t
            if self._time >= self._trust_acc_time:
                self._mode = BASIS_COMPUTE_MODE

        r, u, f =  self._accelerometer.basis.right_up_front

        a = self._accelerometer.acceleration_local_space

        self._vel += (r * a.x + u * a.y + f * a.z) * dt if self._time >= self._trust_acc_time else Vector3(0.0, 0.0, 0.0)
        # интегрирование пути
        self._pos += (r * self._vel.x + u * self._vel.y + f * self._vel.z) * dt
        #sys.stdout.write(f'\n|"omega":{self.omega}|')
        #sys.stdout.write(f'|"angle":{self.angles}|\n')
        #sys.stdout.write(f'|"accel":{self.acceleration}|\n')
        #sys.stdout.write(f'|"vel"  :{self.velocity}|\n')
        #sys.stdout.write(f'|"pos"  :{self.position}|\n')
        #sys.stdout.write('\r\b\b\r')

    def _compute_basis(self) -> bool:
        if self._mode != BASIS_COMPUTE_MODE:
            return False
        self._mode = INTEGRATE_MODE
        # self._basis = Matrix4.build_basis(self.acceleration, self._basis.front)
        # self._ang   = Quaternion.from_rotation_matrix(self._basis).to_euler_angles()
        return True

    def _calibrate(self) -> bool:
        if self._mode != CALIBRATION_MODE:
            return False
        if self._time == 0.0:
            print(f"\n|--------------Accelerometer calibrating...-------------|\n"
                  f"|-------------Please stand by and hold still...---------|")

        progres_bar(self._time / self._calib_time, 55, '|', '_')
        # докалибровались
        if self._time >= self._calib_time:
            self._accelerometer.calibrate(True, self._accelerometer.basis.front)
            self._mode = BASIS_COMPUTE_MODE
            self._time = 0.0
            print(f"|------------------Calibration is done------------------|")
            return False

        # тряхнулись в процессе калибровки
        if not self._accelerometer.calibrate(False, self._accelerometer.basis.front):
            self._mode = BASIS_COMPUTE_MODE
            self._time = 0.0
            print(f"|---------------Calibration is interrupted--------------|")
            return False
        self._time += self._dtime
        return True

    def _warm_up(self) -> bool:
        if self._mode != WARM_UP_MODE:
            return False

        if self._time == 0:
            print(f'\n|----------------Accelerometer start up...--------------|\n'
                  f'|-------------Please stand by and hold still...---------|')

        progres_bar(self._time / self._warm_up_time, 55, '|', '_')

        if self._time >= self._warm_up_time:
            self._mode = CALIBRATION_MODE
            self._time = 0.0
            print(f"|--------------------Warm up is done--------------------|")
            return False

        self._time += self._dtime

        return True

    def update(self):
        with self._timer:
            if self._mode == STOP_MODE:
                return
            if self._warm_up():
                return
            if self._calibrate():
                return
            if self._compute_basis():
                return
            self._integrate()

    def reset(self):
        # with self._lock:
        self._accelerometer.reset()
        self._vel = Vector3(0.0, 0.0, 0.0)
        self._pos = Vector3(0.0, 0.0, 0.0)
        self._time = 0.0

    def suspend(self):
        # with self._lock:
        self._prev_mode = self._mode
        self._mode = STOP_MODE

    def resume(self):
        # with self._lock:
        self._mode = self._prev_mode
        self._prev_mode = -1

    def stop(self):
        # with self._lock:
        self._mode = EXIT_MODE

    def restart(self):
        # with self._lock:
        self._prev_mode = -1
        self.reset()
        self.calibrate()

    def run(self):
        """ This function running in separated thread"""
        while self._mode != EXIT_MODE:
            self.update()
            self._dtime = max(self._timer.last_loop_time,  self._timer.timeout)


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


if __name__ == "__main__":

    # sys.stdout.write('123\n')
    # sys.stdout.write('123\n')
    # sys.stdout.write('123\n')
    # sys.stdout.write(LINE_UP)
    # sys.stdout.write('456\n')
    # a = input()
    # print("ty kurva")

    imu = IMU()
    imu.run()