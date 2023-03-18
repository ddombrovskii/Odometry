# from accelerometer_core.accelerometer import Accelerometer
# from accelerometer_core.Utilities import LoopTimer
# from accelerometer_core.Utilities import Vector3

from Utilities.device import Device, START_MODE, BEGIN_MODE_MESSAGE, RUNNING_MODE_MESSAGE, END_MODE_MESSAGE, \
    DeviceMessage, device_progres_bar, RESET_MODE, REBOOT_MODE, DISCARD_MODE_MESSAGE
from .accelerometer import Accelerometer
from Utilities.vector3 import Vector3
import datetime as dt


# modes
CALIBRATION_MODE = 7
BASIS_COMPUTE_MODE = 8
INTEGRATE_MODE = 9
RECORDING_MODE = 10


TIME            = "time"
DTIME           = "dtime"
ACCELERATION    = "acceleration"
VELOCITY        = "velocity"
POSITION        = "position"
ANGLES_VELOCITY = "angles_velocity"
ANGLES          = "angles"
DEVICE_NAME     = "device_name"
LOG_TIME_START  = "log_time_start"
WAY_POINTS      = "way_points"


# TODO запись актуальных калибровочных данных и поиск логов калибровки при запуске
# TODO Подумать как можно организовать ввод с клавиатуры без cv2.waitKey(timeout)
#  вроде Keyboard либа может решить эту проблему
# TODO что сделать с синхронизацией, если например камера работает в одном потоке,
#  а мы запрашиваем изображение или ещё что из другого потока
class IMU(Device):
    def __init__(self):  # , forward: Vector3 = None):
        self._accelerometer: Accelerometer
        try:
            self._accelerometer = Accelerometer()
        except RuntimeError as err:
            print(err.args)
            exit(0)
        super().__init__()
        self._file_name = ""
        self._file_handle = None
        # время простоя перед запуском
        self._start_time:   float = 1.0
        # время калибровки
        self._calib_time:     float = 2.0
        # время ...
        self._trust_acc_time: float = 0.1
        self._acc_check_time: float = 0.0
        self._vel: Vector3   = Vector3(0.0, 0.0, 0.0)
        self._pos: Vector3   = Vector3(0.0, 0.0, 0.0)
        self.register_callback(RECORDING_MODE, self._record)
        self.register_callback(CALIBRATION_MODE, self._calibrate)
        self.register_callback(INTEGRATE_MODE, self._integrate)

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

    def calibrate(self, timeout: float = None, calib_results_save_path: str = None):
        """
        Калибровка акселерометра
        """
        if self.mode_active(CALIBRATION_MODE):
            return
        self.stop_all()
        self.send_message(CALIBRATION_MODE, BEGIN_MODE_MESSAGE)
        self._calib_time = self._calib_time if timeout is None else timeout
        self._file_name = f"accelerometer_calib_info_({dt.datetime.now().strftime('%H; %M; %S')}).json" \
            if calib_results_save_path is None else calib_results_save_path

    def begin_record(self, calib_results_save_path: str = None):
        """
        Калибровка акселерометра
        """
        if self.mode_active(CALIBRATION_MODE):
            return
        self.send_message(RECORDING_MODE, BEGIN_MODE_MESSAGE)
        self._file_name = f"imu_log_({dt.datetime.now().strftime('%H; %M; %S')}).json" \
            if calib_results_save_path is None else calib_results_save_path

    def rebuild_basis(self):
        pass

    def integrate(self):
        """
        Чтение данных акселерометра
        """
        self.stop_all()
        self.send_message(INTEGRATE_MODE, BEGIN_MODE_MESSAGE)

    def on_start(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self.send_log_message(f'\n|----------------Accelerometer start up...--------------|\n'
                                  f'|-------------Please stand by and hold still...---------|\n')
            return RUNNING_MODE_MESSAGE

        if message == RUNNING_MODE_MESSAGE:
            t = self.mode_active_time(START_MODE)
            self.send_log_message(device_progres_bar(t / self._start_time, "", 55, '|', '_'))
            if t >= self._start_time:
                self.calibrate()
                return END_MODE_MESSAGE  # self.send_message(START_MODE, END_MODE_MESSAGE)
            return RUNNING_MODE_MESSAGE

        return DISCARD_MODE_MESSAGE

    def on_messages_wait(self, key_code: int) -> None:
        # Завершение работы режима
        if key_code == ord('i'):
            self.integrate()
            return
        # Включение режима калибровки
        if key_code == ord('c'):
            self.calibrate()
            return

    def on_reset(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._accelerometer.reset()
            self._vel = Vector3(0.0, 0.0, 0.0)
            self._pos = Vector3(0.0, 0.0, 0.0)
            # self.send_message(RESET_MODE, END_MODE_MESSAGE)
            self.send_message(START_MODE, BEGIN_MODE_MESSAGE)
        return END_MODE_MESSAGE

    def on_reboot(self, message: int) -> None:
        if message == BEGIN_MODE_MESSAGE:
            self.stop_all()
            # self.send_message(REBOOT_MODE, END_MODE_MESSAGE)
            self.send_message(INTEGRATE_MODE, BEGIN_MODE_MESSAGE)
        return END_MODE_MESSAGE

    def _integrate(self, message: DeviceMessage) -> int:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self.send_log_message(f"\n|----------Accelerometer read and integrate...----------|\n"
                                  f"|-------------------Please stand by...------------------|\n")
            self._acc_check_time = 0.0
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == RUNNING_MODE_MESSAGE:

            self.send_log_message(device_progres_bar((self._mode_times[INTEGRATE_MODE] / 3.0) % 1.0, "", 55, '|', '_'))

            if not self._accelerometer.read_measurements():
                return RUNNING_MODE_MESSAGE

            dt = self.delta_t

            if (self._accelerometer.acceleration - self._accelerometer.acceleration_prev).magnitude() > \
                    self._accelerometer.acceleration_noize_level:
                self._acc_check_time = 0.0
            else:
                self._acc_check_time += self.delta_t

            r, u, f = self._accelerometer.basis.right_up_front

            a = self._accelerometer.acceleration_local_space

            self._vel += (r * a.x + u * a.y + f * a.z) * dt if self._acc_check_time >= self._trust_acc_time else Vector3(0.0, 0.0, 0.0)
            # интегрирование пути
            self._pos += (r * self._vel.x + u * self._vel.y + f * self._vel.z) * dt
            return RUNNING_MODE_MESSAGE

        return DISCARD_MODE_MESSAGE

    def _calibrate(self, message: DeviceMessage) -> int:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self.send_log_message(f"\n|--------------Accelerometer calibrating...-------------|\n"
                                  f"|-------------Please stand by and hold still...---------|\n")
            self._accelerometer.reset()
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == RUNNING_MODE_MESSAGE:
            t = self.mode_active_time(message.mode)

            self.send_log_message(device_progres_bar(t / self._calib_time, "", 55, '|', '_'))

            if t >= self._calib_time:
                # self.send_message(message.mode, END_MODE_MESSAGE)
                return END_MODE_MESSAGE

            if not self._accelerometer.calibrate(False, self._accelerometer.basis.front):
                # self.send_message(message.mode, END_MODE_MESSAGE)
                return END_MODE_MESSAGE

            return RUNNING_MODE_MESSAGE

        if message.mode_arg == END_MODE_MESSAGE:
            self._accelerometer.calibrate(True, self._accelerometer.basis.front)
            with open(self._file_name, 'wt') as output_file:
                print(self._accelerometer, file=output_file)
            self.integrate()
            # self.begin_record() <- тестирование записи
            return DISCARD_MODE_MESSAGE

        return DISCARD_MODE_MESSAGE

    def _record(self, message: DeviceMessage) -> int:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            try:
                self._file_handle = open(self._file_name, 'wt')
            except IOError as ex:
                self._file_handle = None
                self.send_log_message(f"Unable to open accelerometer record file\n{ex.args}")
                return END_MODE_MESSAGE

            print(f"{{\n\"record_date\": \"{dt.datetime.now().strftime('%H; %M; %S')}\",\n", file=self._file_handle, end="")
            print("\"way_points\" :[\n", file=self._file_handle, end="")

            return RUNNING_MODE_MESSAGE

        if message.mode_arg == RUNNING_MODE_MESSAGE:

            print(f"\t{{\n"
                  f"\t\t\"{DTIME}\"           : {self.delta_t},\n"
                  f"\t\t\"{TIME}\"            : {self.curr_t},\n"
                  f"\t\t\"{ACCELERATION}\"    : {self.acceleration},\n"
                  f"\t\t\"{VELOCITY}\"        : {self.velocity},\n"
                  f"\t\t\"{POSITION}\"        : {self.position},\n"
                  f"\t\t\"{ANGLES_VELOCITY}\" : {self.omega},\n"
                  f"\t\t\"{ANGLES}\"          : {self.angles}\n"
                  f"\t}},\n", file=self._file_handle, end="")

            return RUNNING_MODE_MESSAGE

        if message.mode_arg == END_MODE_MESSAGE:
            if self._file_handle is None:
                return DISCARD_MODE_MESSAGE

            # self._file_handle.seek(-2, 1)
            print("\n\t]\n}", file=self._file_handle, end="")
            try:
                self._file_handle.close()
            except IOError as ex:
                self.send_log_message(f"Unable to close accelerometer record file\n{ex.args}")
                return DISCARD_MODE_MESSAGE

            return DISCARD_MODE_MESSAGE

        return DISCARD_MODE_MESSAGE

