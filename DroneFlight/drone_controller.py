from Utilities.flight_odometer import FlightOdometer
from Utilities.Geometry import Quaternion
from Utilities.CV import CameraHandle
from Mavlink import DroneConnection
from threading import Thread
from Utilities import Timer
from typing import Union
import asyncio


class DroneController:
    def __init__(self, camera_port: Union[int, str] = 0, camera_settings: str = None):
        self._camera: CameraHandle = CameraHandle(camera_port)
        if camera_settings is not None:
            self._camera.load_calib_params(camera_settings)
        self._odometer: FlightOdometer = FlightOdometer()
        # следующие два параметра устанавливаются исходя из параметров камеры!!!
        # У КАЖОЙ КАМЕРЫ РАЗНЫЕ
        # ЕСЛИ ПОМЕНЯТЬ НАСТРОКУ ОБЪЕКТИВА, ТО ОНИ ИЗМЕНЯТСЯ ТАК ЖЕ, КАК И КАЛИБРОВОЧНЫЕ!!!
        self._odometer.pinhole_camera.fov = 45  # зависит от параметров камеры!!!
        self._odometer.pinhole_camera._aspect = 1.0  # зависит от размера матрицы камеры!!!
        self._drone_connection: DroneConnection = DroneConnection()
        self._update_time = 1.0
        self._timer: Timer = Timer()  # как часто будем запускать алгоритм

    @property
    def odometer(self) -> FlightOdometer:
        return self._odometer

    @property
    def drone(self) -> DroneConnection:
        return self._drone_connection

    @property
    def camera(self) -> CameraHandle:
        return self._camera

    def _update(self):
        if self._camera.read_frame():
            print("camera frame reading error...")
            return
        self._odometer.compute(self._camera.camera_cv.undistorted_frame,
                               Quaternion(*self._drone_connection.get_quaternion()),
                               self._drone_connection.get_altitude_mono())
        # вектор положения дрона, рассчитанный на основе одометрии
        # position = self._odometer.position  # {x-coordinate; y-coordinate; z-altitude}
        # position_gps = GPSLocation(position)  # какой-нибудь способ по переводу из координат на плоскости в GPS
        # actual_gps = position_gps + self._drone_connection.start_gps
        # ВНИМАНИЕ ОПЕРАТОР "+" ДЛЯ GPSLocation НЕ ОПРЕДЕЛЁН!!!
        # НАЧИНАЯ С ЭТОГО МОМЕНТА ОТПРАВЛЯЮТСЯ GPS КООРДИНАТЫ НА PIXHAWK
        # self._drone_connection.send_gps(actual_gps)

    @property
    def update_time(self) -> float:
        """
        Время между соседними запусками функции Update.
        :return:
        """
        return self._update_time  # _timer.timeout

    @update_time.setter
    def update_time(self, value: float) -> None:
        """
        Время между соседними запусками функции Update.
        :return:
        """
        assert isinstance(value, float)
        self._update_time = max(value, 0.0)

    async def _main_loop(self):
        # _main_loop ВЫПОЛНЯЕТСЯ БЕСКОНЕЧНО !!!
        # ДЛЯ ОГРАНИЧЕНИЯ ВРЕМЕНИ ВЫПОЛНЕНИЯ НЕОБХОДИМО ОТСЛЕЖИВАТЬ СТАТУС ПОДКЛЮЧЕНИЯ К PIXHAWK
        while True:
            with self._timer:
                self._update()
            await asyncio.sleep(max(0.0, self.update_time - self._timer.inner_time))

    def run(self):
        asyncio.run(self._main_loop())

    def run_in_separated_thread(self) -> Thread:
        _thread = Thread(target=self.run, daemon=True)
        _thread.start()
        return _thread
