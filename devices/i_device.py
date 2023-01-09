from cgeo.loop_timer import LoopTimer
from threading import Thread, Lock
from cgeo.bitset import BitSet32
import datetime as dt
import dataclasses


_DEVICE_ALIVE = 0
_DEVICE_ACTIVE = 1
_DEVICE_LOCKED = 2
_DEVICE_INITIALIZED = 3
_DEVICE_LOGGING_ENABLED = 4


@dataclasses.dataclass
class IDeviceSettings:
    update_rate: float
    life_time: float
    state: int
    device_name: str
    log_file_origin: str


class IDevice(Thread):
    """
    """
    def __init__(self):
        super().__init__()
        self.device_name: str = f"device_{id(self)}"
        self.__rt_timer: LoopTimer = LoopTimer()
        """
        Время жизни устройства
        """
        self.__life_time = -1.0
        self.__lock = Lock()
        self.__log_file_descriptor = None
        self._log_file_origin: str = f"device at address {id(self)}.json"

        if not self._init():
            raise RuntimeError(f"device: {self.name} init function call error")

        self.__state: BitSet32 = BitSet32()
        self.__state.set_bit(_DEVICE_INITIALIZED)

    def __str__(self):
        return f"\t{{\n" \
               f"\t\t\"update_rate\"     : {self.update_rate},\n" \
               f"\t\t\"life_time\"       : {self.life_time},\n" \
               f"\t\t\"state\"           : {self.__state.state},\n" \
               f"\t\t\"device_name\"     : \"{self.device_name}\",\n" \
               f"\t\t\"log_file_origin\" : \"{self.log_file_origin}\"\n" \
               f"\t}}"

    def __enter__(self):
        if not self.require_lock():
            raise RuntimeError("unable to require lock")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release_lock()

    @property
    def timer(self) -> LoopTimer:
        return self.__rt_timer

    @property
    def settings(self) -> IDeviceSettings:
        return IDeviceSettings(self.update_rate, self.life_time,
                               self.__state.state, self.device_name, self.log_file_origin)

    @settings.setter
    def settings(self, settings_set: IDeviceSettings) -> None:
        active = self.active
        if active:
            self.active = False
        self.update_rate = settings_set.update_rate
        self.__life_time = settings_set.life_time
        self.__state = BitSet32(settings_set.state)
        self.device_name = settings_set.device_name
        self.log_file_origin = settings_set.log_file_origin
        self.active = active

    @property
    def update_delta_time(self) -> float:
        """
        Истиное значение времени на метод Update
        """
        return self.timer.last_loop_time

    @property
    def time_alive(self) -> float:
        """
        Время жизни
        """
        return self.timer.time

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
        return self.timer.timeout

    @update_rate.setter
    def update_rate(self, value: float) -> None:
        with self:
            self.timer.timeout = min(max(value, 0.001), 3600)

    @property
    def active(self) -> bool:
        """
        Активен ли в данный момент
        """
        return self.__state.is_bit_set(_DEVICE_ACTIVE)

    @active.setter
    def active(self, val: bool) -> None:
        with self:
            if val:
                self.__state.set_bit(_DEVICE_ACTIVE)
            else:
                self.__state.clear_bit(_DEVICE_ACTIVE)

    @property
    def alive(self) -> bool:
        """
        Жив или нет...
        """
        return self.__state.is_bit_set(_DEVICE_ALIVE)

    @alive.setter
    def alive(self, val: bool) -> None:
        with self:
            if val:
                self.__state.set_bit(_DEVICE_ALIVE)
            else:
                self.__state.clear_bit(_DEVICE_ALIVE)

    @property
    def enable_logging(self) -> bool:
        return self.__state.is_bit_set(_DEVICE_LOGGING_ENABLED)

    @enable_logging.setter
    def enable_logging(self, value: bool) -> None:
        if self.enable_logging == value:
            return
        with self:
            if value and self._try_open_log_file():
                self.__state.set_bit(_DEVICE_LOGGING_ENABLED)
            else:
                self.__state.clear_bit(_DEVICE_LOGGING_ENABLED)
                self._try_close_log_file()

    @property
    def log_file_origin(self) -> str:
        return self._log_file_origin

    @log_file_origin.setter
    def log_file_origin(self, value: str) -> None:
        if value == self._log_file_origin:
            return

        with self:
            if self._try_close_log_file():
                self._try_open_log_file(value)

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

        if not self.__lock.acquire():
            return False

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
            with self.timer:
                if not self.active:
                    continue

                self._update()

                if self.enable_logging:
                    try:
                        self._log_file_descriptor.write(self._logging())
                    except IOError as ex_:
                        print(f"IOError: {ex_.args}\nlog write error to file {self.log_file_origin}")

                if self.life_time > 0:
                    if self.time_alive > self.life_time:
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
