import threading
import time


class IDevice(threading.Thread):
    def __init__(self):
        super().__init__()
        # super().setDaemon(True)
        self.__life_time = -1.0
        self.__time_alive = 0.0
        self.__update_rate = 0.010
        self.__active = False
        self.__alive = False
        self.__initialized = False
        self.__lock = threading.Lock()
        self.__enable_logging: bool = False
        self._log_file_origin: str = f"device at address {id(self)}.txt"
        self.__log_file_descriptor = None
        self.__initialized = self._init()
        if not self.__initialized:
            raise RuntimeError(f"device: {self.name} init function call error")

    @property
    def life_time(self) -> float:
        return self.__life_time

    @life_time.setter
    def life_time(self, time_: float):
        if self.active:
            return
        self.__life_time = time_

    @property
    def _log_file_descriptor(self):
        return self.__log_file_descriptor

    def _try_open_log_file(self, orig: str = None) -> bool:

        path = orig
        if path is None:
            path = self._log_file_origin
        try:
            self.__log_file_descriptor = open(path, "a")
            return True
        except IOError as ex_:
            self.__log_file_descriptor = None
            print(f"IOError {ex_.args} \n Unable to open file {path}")
            return False

    def _try_close_log_file(self) -> bool:
        if self.__log_file_descriptor is None:
            return True
        try:
            self.__log_file_descriptor.close()
            self.__log_file_descriptor = None
            return True
        except IOError as ex_:
            print(f"IOError {ex_.args} \n Unable to close file {self._log_file_origin}")
            return False

    @property
    def enable_logging(self) -> bool:
        return self.__enable_logging

    @enable_logging.setter
    def enable_logging(self, value: bool) -> None:
        self.lock()
        self.__enable_logging = value

        if self.__enable_logging:
            self.__enable_logging = self._try_open_log_file()
            self.release()
            return

        self._try_close_log_file()
        self.release()
        return

    @property
    def log_file_origin(self) -> str:
        return self._log_file_origin

    @log_file_origin.setter
    def log_file_origin(self, value: str) -> None:
        self.lock()
        if value == self._log_file_origin:
            self.release()
            return

        if not self._try_close_log_file():
            self.release()
            return

        if not self._try_open_log_file(value):
            self.release()
            return

        self._log_file_origin = value
        self.release()

    def lock(self):
        self.__lock.acquire()

    def release(self):
        self.__lock.release()

    @property
    def initialized(self) -> bool:
        return self.__initialized

    @property
    def update_rate(self) -> float:
        return self.__update_rate

    @update_rate.setter
    def update_rate(self, value: float) -> None:
        self.lock()
        self.__update_rate = min(max(value, 0.001), 3600)
        self.release()

    @property
    def active(self) -> bool:
        return self.__active

    @active.setter
    def active(self, val: bool) -> None:
        self.lock()
        self.__active = val
        self.release()

    @property
    def alive(self) -> bool:
        return self.__alive

    @alive.setter
    def alive(self, val: bool) -> None:
        self.lock()
        self.__alive = val
        self.release()

    def _logging(self) -> str:
        return ""

    def _start(self) -> bool:
        return True

    def _init(self) -> bool:
        return True

    def _dispose(self) -> bool:
        return True

    def _update(self) -> None: ...
        # pass

    def run(self):
        self.__alive = self._start()
        if not self.__alive:
            raise RuntimeError(f"device: {self.name} start function call error")
        update_time: float
        self.__active = True
        while self.__alive:
            update_time = time.time()
            if not self.__active:
                continue
            self._update()
            if self.__enable_logging:
                try:
                    self._log_file_descriptor.write(self._logging())
                except IOError as ex_:
                    print(f"IOError: {ex_.args}\n"
                          f"log write error to file {self.log_file_origin}")

            update_time = time.time() - update_time
            if update_time < self.__update_rate:
                time.sleep(self.__update_rate - update_time)
                self.__time_alive += self.__update_rate
            self.__time_alive += update_time
            if self.__life_time > 0:
                if self.__time_alive > self.__life_time:
                    break

        self._try_close_log_file()
        if not self._dispose():
            raise RuntimeError(f"device: {self.name} dispose function call error")