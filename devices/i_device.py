from Odometry.bit_set import BitSet32
from threading import Thread, Lock
import datetime as dt
import time


_DEVICE_ALIVE = 0
_DEVICE_ACTIVE = 1
_DEVICE_LOCKED = 2
_DEVICE_INITIALIZED = 3
_DEVICE_LOGGING_ENABLED = 4


class IDevice(Thread):
    """
    """
    def __init__(self):
        super().__init__()

        self.device_name: str = f"device_{id(self)}"
        """
        Время жизни устройства
        """
        self.__life_time = -1.0
        """
        Текущее время жизни
        """
        self.__time_alive = 0.0
        """
        Истиное значение времени на метод Update
        """
        self.__update_delta_time = 0.0

        """
        Частота обновления
        """
        self.__update_rate = 0.010
        self.__lock = Lock()
        self.__log_file_descriptor = None
        self._log_file_origin: str = f"device at address {id(self)}.json"

        if not self._init():
            raise RuntimeError(f"device: {self.name} init function call error")

        self.__state: BitSet32 = BitSet32()
        self.__state.set_bit(_DEVICE_INITIALIZED)

    @property
    def update_delta_time(self) -> float:
        """
        Истиное значение времени на метод Update
        """
        return self.__update_delta_time

    @property
    def life_time(self) -> float:
        """
        Время жизни
        """
        return self.__life_time

    @life_time.setter
    def life_time(self, time_: float):
        if self.active:
            return
        if time_ < 0.0:
            self.__life_time = -1.0
            return
        self.__life_time = time_

    @property
    def initialized(self) -> bool:
        """ Флаг отвечающий за корректность инициализации """
        return self.__state.is_bit_set(_DEVICE_LOGGING_ENABLED)

    @property
    def update_rate(self) -> float:
        """
        Время обновления
        """
        return self.__update_rate

    @update_rate.setter
    def update_rate(self, value: float) -> None:
        if not self.require_lock():
            return
        self.__update_rate = min(max(value, 0.001), 3600)
        self.release_lock()

    @property
    def active(self) -> bool:
        """
        Активен ли в данный момент
        """
        return self.__state.is_bit_set(_DEVICE_ACTIVE)

    @active.setter
    def active(self, val: bool) -> None:
        if not self.require_lock():
            return
        if val:
            self.__state.set_bit(_DEVICE_ACTIVE)
            self.release_lock()
            return
        self.__state.clear_bit(_DEVICE_ACTIVE)
        self.release_lock()

    @property
    def alive(self) -> bool:
        """
        Жив или нет...
        """
        return self.__state.is_bit_set(_DEVICE_ALIVE)

    @alive.setter
    def alive(self, val: bool) -> None:
        if not self.require_lock():
            return
        if val:
            self.__state.set_bit(_DEVICE_ALIVE)
            self.release_lock()
            return
        self.__state.clear_bit(_DEVICE_ALIVE)
        self.release_lock()

    @property
    def enable_logging(self) -> bool:
        return self.__state.is_bit_set(_DEVICE_LOGGING_ENABLED)

    @enable_logging.setter
    def enable_logging(self, value: bool) -> None:
        if self.enable_logging == value:
            return

        if not self.require_lock():
            return

        if value and self._try_open_log_file():
            self.__state.set_bit(_DEVICE_LOGGING_ENABLED)
            self.release_lock()
            return

        self._try_close_log_file()
        self.release_lock()
        return

    @property
    def log_file_origin(self) -> str:
        return self._log_file_origin

    @log_file_origin.setter
    def log_file_origin(self, value: str) -> None:
        if value == self._log_file_origin:
            return

        if not self.require_lock():
            return

        if not self._try_close_log_file():
            self.release_lock()
            return

        if not self._try_open_log_file(value):
            self.release_lock()
            return

        self._log_file_origin = value
        self.release_lock()

    @property
    def _log_file_descriptor(self):
        return self.__log_file_descriptor

    def _try_open_log_file(self, orig: str = None) -> bool:
        # TODO refactor
        if self.__log_file_descriptor is not None:
            if self.__log_file_descriptor.name == orig:
                return True
            if not self._try_close_log_file():
                return False
            self._log_file_origin = orig
        try:
            self.__log_file_descriptor = open(self._log_file_origin, "wt")
            self.__log_file_descriptor.write(f"{{\n\"device_name\"   : \"{self.device_name}\",\n")
            self.__log_file_descriptor.write(f"\"log_time_start\": \"{dt.datetime.now().strftime('%H; %M; %S')}\"")
            return True

        except IOError as ex_:
            self.__log_file_descriptor = None
            print(f"IOError {ex_.args} \n Unable to open file {self._log_file_origin}")
            self._log_file_origin = ""
            return False

    def _try_close_log_file(self) -> bool:
        if self.__log_file_descriptor is None:
            return True
        try:
            self.__log_file_descriptor.write("\n}")
            self.__log_file_descriptor.close()
            self.__log_file_descriptor = None
            return True
        except IOError as ex_:
            print(f"IOError {ex_.args} \n Unable to close file {self._log_file_origin}")
            return False

    def require_lock(self) -> bool:
        if self.__state.is_bit_set(_DEVICE_LOCKED):
            return False

        if self.__lock.acquire():
            self.__state.set_bit(_DEVICE_LOCKED)
            return True

    def release_lock(self):
        self.__state.clear_bit(_DEVICE_LOCKED)
        self.__lock.release()

    def _logging(self) -> str:
        return f"\n\"{dt.datetime.now().strftime('%H; %M; %S')}\","

    def _start(self) -> bool:
        return True

    def _init(self) -> bool:
        return True

    def _dispose(self) -> bool:
        return True

    def _update(self) -> None:
        ...

    def run(self):
        if not self._start():
            raise RuntimeError(f"device: {self.name} start function call error")

        self.__state.set_bit(_DEVICE_ALIVE)

        self.__state.set_bit(_DEVICE_ACTIVE)

        update_time: float

        while self.alive:
            # начало
            update_time = time.perf_counter()
            # проверка на факт активно устройство или нет
            if not self.active:
                continue
            # выполнение полезной нагрузки
            self._update()
            # логгирование результатов, если включено и реализовано...
            if self.enable_logging:
                try:
                    self._log_file_descriptor.write(self._logging())

                except IOError as ex_:
                    print(f"IOError: {ex_.args}\nlog write error to file {self.log_file_origin}")

            self.__update_delta_time = time.perf_counter() - update_time

            if self.update_delta_time < self.update_rate:
                time.sleep(self.update_rate - self.update_delta_time)
                self.__time_alive += self.update_rate

            self.__time_alive += self.update_delta_time

            if self.life_time > 0:
                if self.__time_alive > self.life_time:
                    break

        self._try_close_log_file()

        if not self._dispose():
            raise RuntimeError(f"device: {self.name} dispose function call error")


class DeviceTest(IDevice):
    def __init__(self):
        super().__init__()

    def _try_open_log_file(self, orig: str = None) -> bool:
        if super()._try_open_log_file(orig):
            self._log_file_descriptor.write(f",\n\"time_stamps\":[")
            return True
        return False

    def _try_close_log_file(self) -> bool:
        if self._log_file_descriptor is None:
            return True
        try:
            self._log_file_descriptor.seek(self._log_file_descriptor.tell() - 1)
            self._log_file_descriptor.write(f"\n]")
        except Exception as _ex:
            print(f"log file closing failed:\n{_ex.args}")
            return False or super()._try_close_log_file()
        return super()._try_close_log_file()


if __name__ == "__main__":
    dev_test = DeviceTest()
    dev_test.update_rate = 1.0
    dev_test.enable_logging = True
    dev_test.life_time = 10
    dev_test.start()
    dev_test.join()
