from Utilities.Device import BEGIN_MODE_MESSAGE, RUNNING_MODE_MESSAGE, END_MODE_MESSAGE
from Utilities import Device, Timer


class DeviceMode:
    def __init__(self, device: Device):
        assert isinstance(Device, device)
        self._life_time_timer: Timer = Timer()
        self._parent: Device = device
        self._handle = self._parent.register_callback(lambda message: self.__update(message))

    def start(self) -> bool:
        return self._parent.begin_mode(self.handle)

    def stop(self) -> bool:
        return self._parent.stop_mode(self.handle)

    @property
    def is_active(self) -> bool:
        return self._parent.mode_active(self.handle)

    # @property
    # def active_time(self) -> float:
    #     return self._parent.mode_active_time(self.handle)

    @property
    def handle(self) -> int:
        return self._handle

    @property
    def device(self) -> Device:
        return self._parent

    @property
    def active_time(self) -> float:
        return self._life_time_timer.total_time

    def _on_start(self, message: int) -> bool:
        return True

    def _on_run(self, message: int) -> bool:
        return False

    def _on_end(self, message: int) -> bool:
        return False

    def __update(self, message: int) -> bool:
        with self._life_time_timer:
            flag = self.__update__(message)
        return flag

    def __update__(self, message: int) -> bool:
        if message == BEGIN_MODE_MESSAGE:
            return self._on_start(message)
        if message == RUNNING_MODE_MESSAGE:
            return self._on_run(message)
        if message == END_MODE_MESSAGE:
            return self._on_end(message)
        return False
