from Utilities.device import Device, START_MODE, BEGIN_MODE_MESSAGE, RUNNING_MODE_MESSAGE, END_MODE_MESSAGE, \
    DeviceMessage, device_progres_bar, DISCARD_MODE_MESSAGE
from .accelerometer_base import AccelerometerBase, smooth_step
from .accelerometer_bno055 import AccelerometerBNO055
from .accelerometer_settings import load_accelerometer_settings
from Utilities.Geometry.vector3 import Vector3
import datetime as dt
import os


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


# class LinearRegressor:
#     def __init__(self):
#         self._x0 = 0.0
#         self._y0 = 0.0
#         self._x_sum = 0.0
#         self._y_sum = 0.0
#         self._xy_sum = 0.0
#         self._xx_sum = 0.0
#         self._x = []
#         self._y = []
#         self._cap = 16
#
#     @property
#     def n_points(self) -> int:
#         return len(self._x)
#
#     def _append(self, x, y):
#         self._x.append(x)
#         self._y.append(y)
#         self._x_sum += x
#         self._y_sum += y
#         self._xy_sum += x * y
#         self._xx_sum += x * x
#
#     def _set_start_pt(self, index: int):
#         self._x_sum -= self._x0
#         self._y_sum -= self._y0
#         self._xy_sum -= self._x0 * self._y0
#         self._xx_sum -= self._x0 * self._x0
#         self._x0 = self._x[index]
#         self._y0 = self._x[index]
#
#     def update(self, x, y) -> float:
#         self._append(x, y)
#
#         if self.n_points < 2:
#             self._set_start_pt(0)
#             return y
#
#         if len(self._x) == self._cap:
#             self._set_start_pt(1)
#             del self._x[0]
#             del self._y[0]
#         k = (self._xy_sum - self._x_sum * self._y_sum / self._cap) / \
#             (self._xx_sum - self._x_sum * self._x_sum / self._cap)
#         return k * x + (self._y_sum - k * self._x_sum) / self._cap


class LinearRegressor:
    def __init__(self):
        self._x = []
        self._y = []
        self._cap = 16

    def update(self, x, y) -> float:
        self._x.append(x)
        self._y.append(y)
        if len(self._x) < 2:
            return y

        if len(self._x) == self._cap:
            del self._x[0]
            del self._y[0]

        sum_x = sum(xi for xi in self._x)
        sum_y = sum(yi for yi in self._y)
        sum_xy = sum(xi * yi for xi, yi in zip(self._x, self._y))
        sum_xx = sum(xi * xi for xi in self._x)
        k = (sum_xy - sum_x * sum_y / self._cap) / (sum_xx - sum_x * sum_x / self._cap)
        return k * x + (sum_y - k * sum_x) / self._cap


# TODO запись актуальных калибровочных данных и поиск логов калибровки при запуске (DONE)
# TODO Подумать как можно организовать ввод с клавиатуры без cv2.waitKey(timeout)
#  вроде Keyboard либа может решить эту проблему
# TODO что сделать с синхронизацией, если например камера работает в одном потоке,
#  а мы запрашиваем изображение или ещё что из другого потока (Возможно просто воткнуть Lock...)
class IMU(Device):
    """
    1. Интегрирует угол поворота на основе данных акселерометра
    2. Интегрирует скорость на основе данных акселерометра
    3. Интегрирует путь на основе данных акселерометра
    4. Режим старта полностью захватывает устройство, запрещая другие режимы до завершения режима старта
    5. Режим калибровки полностью захватывает устройство, запрещая другие режимы до завершения режима калибровки
    6. Может работать единовременно в режиме интегрирования или интегрирования и записи
    """
    def __init__(self):  # , forward: Vector3 = None):
        self._accelerometer: AccelerometerBNO055
        try:
            self._accelerometer = AccelerometerBNO055()
        except RuntimeError as err:
            print(err.args)
            exit(0)
        super().__init__()
        self._file_name = ""
        self._file_handle = None
        # время простоя перед запуском
        self._start_time:   float = 1.0
        # время калибровки
        self._calib_time:     float = 5.0
        # время ...
        self._trust_acc_time: float = 0.1
        self._acc_check_time: float = 0.0
        self._vel: Vector3       = Vector3(0.0, 0.0, 0.0)
        self._vel_raw: Vector3   = Vector3(0.0, 0.0, 0.0)
        self._vel_reg: Vector3   = Vector3(0.0, 0.0, 0.0)
        self._pos: Vector3   = Vector3(0.0, 0.0, 0.0)
        self.update_time = 1.0 / 60.0
        self.register_callback(RECORDING_MODE, self._record)
        self.register_callback(CALIBRATION_MODE, self._calibrate)
        self.register_callback(INTEGRATE_MODE, self._integrate)
        self._vx = LinearRegressor()
        self._vy = LinearRegressor()
        self._vz = LinearRegressor()

    @property
    def accelerometer(self) -> AccelerometerBase:
        """
        Время простоя перед запуском.
        :return:
        """
        return self._accelerometer

    @property
    def start_time(self) -> float:
        """
        Время простоя перед запуском.
        :return:
        """
        return self._start_time

    @start_time.setter
    def start_time(self, value: float) -> None:
        """
        Время простоя перед запуском.
        :return:
        """
        self._start_time = min(max(0.125, value), 60)

    @property
    def calib_time(self) -> float:
        """
        Время калибровки.
        :return:
        """
        return self._calib_time

    @calib_time.setter
    def calib_time(self, value: float) -> None:
        """
        Время калибровки.
        :return:
        """
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
        self._accelerometer.k_accel = value

    @property
    def accel_threshold(self) -> float:
        """
        Пороговый уровень отклонения значения модуля вектора G относительно которого определяется, движемся или нет.
        """
        return self._accelerometer.acceleration_noize_level

    @accel_threshold.setter
    def accel_threshold(self, value: float) -> None:
        """
        Пороговый уровень отклонения значения модуля вектора G относительно которого определяется, движемся или нет.
        """
        self._accelerometer.acceleration_noize_level = value

    @property
    def accel_lin(self) -> Vector3:
        """
        Угловые скорости
        """
        return self._accelerometer.acceleration_linear

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
        return self._accelerometer.angles

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
    def velocity_clean(self) -> Vector3:
        """
        Усреднённая линейным регрессором скорость
        """
        return self._vel_reg

    @property
    def velocity_raw(self) -> Vector3:
        """
        Сырой результат интегрирования ускорения. Текущая скорость в мировой системе координат
        """
        return self._vel_raw

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

    def calibrate(self, timeout: float = None, calib_results_save_path: str = None) -> None:
        """
        Запуск калибровки акселерометра.
        :param timeout: время калибровки
        :param calib_results_save_path: путь сохранения результатов калибровки
        """
        if self.mode_active(CALIBRATION_MODE):
            return
        self.stop_all()
        self.send_message(CALIBRATION_MODE, BEGIN_MODE_MESSAGE)
        self._calib_time = self._calib_time if timeout is None else timeout
        self._file_name = f"accelerometer_calib_info_({dt.datetime.now().strftime('%H; %M; %S')}).json" \
            if calib_results_save_path is None else calib_results_save_path

    def begin_record(self, results_save_path: str = None) -> None:
        """
        Запуск режима записи.
        :param results_save_path: путь сохранения результатов интегрирования
        """
        if self.mode_active(CALIBRATION_MODE):
            return
        if self.mode_active(START_MODE):
            return
        self.send_message(RECORDING_MODE, BEGIN_MODE_MESSAGE)
        self._file_name = f"imu_log_({dt.datetime.now().strftime('%H; %M; %S')}).json" \
            if results_save_path is None else results_save_path

    def end_record(self) -> None:
        """
        Завершение режима записи.
        :return:
        """
        if self.mode_active(CALIBRATION_MODE):
            return
        if not self.mode_active(RECORDING_MODE):
            return
        self.send_message(RECORDING_MODE, END_MODE_MESSAGE)

    def integrate(self) -> None:
        """
        Чтение данных акселерометра интегрирование значений пути и скорости
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
            self.accelerometer.read_request()
            self.send_log_message(device_progres_bar(t / self._start_time if self.start_time > 0.001 else 1.0, "", 55, '|', '_'))
            if t >= self._start_time:
                self.calibrate()
                return END_MODE_MESSAGE
            return RUNNING_MODE_MESSAGE

        return DISCARD_MODE_MESSAGE

    def on_messages_wait(self, key_code: int) -> None:
        # Включение режима калибровки
        if key_code == ord('i'):
            self.integrate()
            return
        # Включение режима калибровки
        if key_code == ord('c'):
            self.calibrate()
            return
        # Включение режима калибровки
        if key_code == ord('r'):
            if self.mode_active(RECORDING_MODE):
                self.end_record()
                return
            self.begin_record()
            return

    def on_reset(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self._accelerometer.reset()
            self._pos = Vector3(0.0, 0.0, 0.0)
            self._vel = Vector3(0.0, 0.0, 0.0)
            self._vel_raw = Vector3(0.0, 0.0, 0.0)
            self._vel_reg = Vector3(0.0, 0.0, 0.0)
            self.send_message(START_MODE, BEGIN_MODE_MESSAGE)
        return END_MODE_MESSAGE

    def on_reboot(self, message: int) -> None:
        if message == BEGIN_MODE_MESSAGE:
            self.stop_all()
            self._pos = Vector3(0.0, 0.0, 0.0)
            self._vel = Vector3(0.0, 0.0, 0.0)
            self._vel_raw = Vector3(0.0, 0.0, 0.0)
            self._vel_reg = Vector3(0.0, 0.0, 0.0)
            self.send_message(INTEGRATE_MODE, BEGIN_MODE_MESSAGE)
        return END_MODE_MESSAGE

    def _integrate(self, message: DeviceMessage) -> int:
        if message.is_begin:
            self.send_log_message(f"\n|----------Accelerometer read and integrate...----------|\n"
                                  f"|-------------------Please stand by...------------------|\n")
            self._acc_check_time = 0.0
            self.accelerometer.build_basis()
            self._pos = Vector3(0.0, 0.0, 0.0)
            self._vel = Vector3(0.0, 0.0, 0.0)
            self._vel_raw = Vector3(0.0, 0.0, 0.0)
            self._vel_reg = Vector3(0.0, 0.0, 0.0)
            return message.run

        if message.is_running:
            if not self._accelerometer.read_request():
                return message.run

            delta_t = self.delta_t
            # Оценка времени, когда изменение модуля вектора ускорения меньше acceleration_noize_level
            accel_delta = (self._accelerometer.acceleration - self._accelerometer.acceleration_prev).magnitude()
            if accel_delta > self.accel_threshold:
                self._acc_check_time = 0.0
            else:
                self._acc_check_time += delta_t
            # локальный базис акселерометра
            basis = self._accelerometer.basis
            # ускорение в локальном базисе акселерометра
            a = self._accelerometer.acceleration_local_space
            # интегрирование скорости
            self._vel_raw += (a * Vector3(1, 1, 0)) * delta_t

            t = self.mode_active_time(INTEGRATE_MODE)

            self._vel_reg = Vector3(self._vx.update(t, self._vel_raw.x),
                                    self._vy.update(t, self._vel_raw.y),
                                    self._vz.update(t, self._vel_raw.z))

            self._vel = (self._vel_raw - self._vel_reg) * \
                        smooth_step(accel_delta, self.accel_threshold * 0.5, self.accel_threshold * 1.0)

            self._pos += self.velocity * delta_t

            return message.run

        return message.discard

    def _calibrate(self, message: DeviceMessage) -> int:
        if message.is_begin:
            self.send_log_message(f"\n|--------------Accelerometer calibrating...-------------|\n"
                                  f"|-------------Please stand by and hold still...---------|\n")
            self._accelerometer.reset()
            # TODO подумать что будет, если нужно перекалиброваться, а калибровочный файл уже есть
            file_dir = os.path.dirname(self._file_name)
            if file_dir == "":
                file_dir = '.'
            for file in os.listdir(file_dir):
                if file.startswith("accelerometer_calib_info_"):
                    try:
                        load_accelerometer_settings(self._accelerometer, file)
                        self._file_name = ""
                        self.send_log_message(f"|------------------Loaded from file...------------------|\n|{file:^55}|\n")

                        return message.end
                    except Exception as _ex:
                        self.send_log_message(f"Loading error accelerometer calib info from file\n:{self._file_name}...\n")
                        self.send_log_message(f"{_ex.args}")
                        return message.run

            return message.run

        if message.is_running:
            t = self.mode_active_time(message.mode)

            self.send_log_message(device_progres_bar(t / self._calib_time, "", 55, '|', '_'))

            if t >= self._calib_time:
                return message.end

            if not self._accelerometer.calibrate(False, self._accelerometer.basis.front):
                return message.end

            return message.run

        if message.is_end:
            if self._file_name != "":
                self._accelerometer.calibrate(True, self._accelerometer.basis.front)
                with open(self._file_name, 'wt') as output_file:
                    print(self._accelerometer, file=output_file)
                    self._file_name = ""
            self.integrate()
            return message.discard

        return message.discard

    def _record(self, message: DeviceMessage) -> int:
        if message.is_begin:
            try:
                self._file_handle = open(self._file_name, 'wt')
            except IOError as ex:
                self._file_handle = None
                self.send_log_message(f"Unable to open accelerometer record file\n{ex.args}")
                return message.end

            print(f"{{\n\"record_date\": \"{dt.datetime.now().strftime('%H; %M; %S')}\",\n", file=self._file_handle, end="")
            print("\"way_points\" :[\n", file=self._file_handle, end="")

            return message.run

        if message.is_running:

            print(f"\t{{\n"
                  f"\t\t\"{DTIME}\"           : {self.delta_t},\n"
                  f"\t\t\"{TIME}\"            : {self.curr_t},\n"
                  f"\t\t\"{ACCELERATION}\"    : {self.acceleration},\n"
                  f"\t\t\"{VELOCITY}\"        : {self.velocity},\n"
                  f"\t\t\"{POSITION}\"        : {self.position},\n"
                  f"\t\t\"{ANGLES_VELOCITY}\" : {self.omega},\n"
                  f"\t\t\"{ANGLES}\"          : {self.angles}\n"
                  f"\t}},\n", file=self._file_handle, end="")

            return message.run

        if message.is_end:
            if self._file_handle is None:
                return message.discard
            self._file_handle.seek(self._file_handle.tell() - 3, 0)
            print("\n\t]\n}", file=self._file_handle, end="")
            try:
                self._file_handle.close()
            except IOError as ex:
                self.send_log_message(f"Unable to close accelerometer record file\n{ex.args}")
                return message.discard
            return message.discard
        return message.discard



