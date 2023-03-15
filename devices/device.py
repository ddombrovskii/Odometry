from Accelerometer.accelerometer_core.utilities import LoopTimer
from typing import List, Callable, Dict
from collections import namedtuple
import cv2 as cv
import sys


def progres_bar(val: float, label: str = "", max_chars: int = 55, char_progress: str = '#', char_stand_by: str = '.' ):
    filler_l = int(min(max(0.0, val), 1.0) * max_chars)  # max_chars - title chars count
    filler_r = max_chars - filler_l
    if len(label) == 0:
        sys.stdout.write(f'\r|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|')
    else:
        sys.stdout.write(f'\r|{label:15}|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|')
    if filler_r == 0:
         sys.stdout.write('\n')


class DeviceMessage(namedtuple('DeviceMessage', 'mode, mode_arg')):
    __slots__ = ()

    def __new__(cls, mode: int = -1, mode_arg: int = -1):
        return super().__new__(cls, int(mode),  int(mode_arg))

    def __str__(self):
        return f"{{\"mode_info\": {self.mode}, \"mode_arg\": {self.mode_arg}}}"


START_MODE = 1
PAUSE_MODE = 2
EXIT_MODE  = 3
RESET_MODE  = 4
REBOOT_MODE  = 5
SHUTDOWN_MODE  = 6
ANY_MODE   = -1

BEGIN_MODE_MESSAGE = 0
RUNNING_MODE_MESSAGE = 1
END_MODE_MESSAGE = 2


class Device:
    class DeviceCallback(namedtuple('DeviceCallback', 'service_callback, user_callback')):
        def __new__(cls, service_callback, user_callback):
            return super().__new__(cls, service_callback, user_callback)

        def __call__(self, message: DeviceMessage):
            self.service_callback.__call__(message)
            self.user_callback.__call__(message)
    """
    Базовое поведение для устройства, которое может работать в одном нескольких режимах единовременно
    """
    def __init__(self):
        self._curr_modes: Dict[int, int]   = {}  # текущие режимы
        self._prev_modes: Dict[int, int]   = {}  # предыдущие режимы
        self._mode_times: Dict[int, float] = {}  # время существования в режимах
        self._d_time: float = 0.0  # время между текущим и предыдущим вызовом метода self.update()
        self._messages: List[DeviceMessage] = []  # список сообщений для переключения режимов
        self._callbacks: Dict[int, Callable[[DeviceMessage, ], None]] = {}  # список служебных функций
        self._user_callbacks: Dict[int, Device.DeviceCallback] = {}  # список пользовательских функций
        self._timer: LoopTimer = LoopTimer(0.01)
        self._callbacks.update({START_MODE:  self._start })
        self._callbacks.update({PAUSE_MODE:  self._pause })
        self._callbacks.update({EXIT_MODE:   self._exit  })
        self._callbacks.update({RESET_MODE:  self._reset })
        self._callbacks.update({REBOOT_MODE: self._reboot})
        self.send_message(START_MODE, BEGIN_MODE_MESSAGE)

    def __default(self, message: DeviceMessage) -> None:
        """
        Базовое поведение любого режима.
        В момент включения время работы режима обнуляется.
        После происходит инкремент с каждым вызовом функции update().
        :param message: состояние режима (старт режима, рабочий режим, завершение режима).
        :return:
        """
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            if message.mode in self._curr_modes:
                return
            self._mode_times[message.mode] = 0.0
            self._curr_modes[message.mode] = message.mode
            return
        if message.mode_arg == RUNNING_MODE_MESSAGE:
            self._mode_times[message.mode] += self._d_time
            return
        if message.mode_arg == END_MODE_MESSAGE:
            if not(message.mode in self._curr_modes):
                return
            del self._curr_modes[message.mode]
            del self._mode_times[message.mode]
            return

    def __stop_all_except(self, except_mode: int):
        """
        Генерирует сообщения завершающие все процессы, кроме указанного
        :param except_mode:
        :return:
        """
        for mode in self._curr_modes:
            if mode == except_mode:
                continue
            self.send_message(mode, END_MODE_MESSAGE)

    def _reset(self, message: DeviceMessage) -> None:
        self.__default(message)
        self.on_reset(message.mode_arg)
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self.__stop_all_except(RESET_MODE)

    def _reboot(self, message: DeviceMessage) -> None:
        self.__default(message)
        self.on_reboot(message.mode_arg)
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self.__stop_all_except(REBOOT_MODE)

    def _start(self, message: DeviceMessage) -> None:
        self.__default(message)
        self.on_start(message.mode_arg)

    def _exit(self, message: DeviceMessage) -> None:
        # print(message)
        self.__default(message)
        self.on_exit(message.mode_arg)
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self.__stop_all_except(EXIT_MODE)

    def _pause(self, message: DeviceMessage) -> None:
        self.on_pause(message.mode_arg)
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            for mode in self._curr_modes:
                self._prev_modes.update({mode: mode})
            self._curr_modes.clear()
            self._curr_modes.update({PAUSE_MODE: PAUSE_MODE})
            return

        if message.mode_arg == END_MODE_MESSAGE:
            self._curr_modes.clear()
            for mode in self._prev_modes:
                self.send_message(mode, RUNNING_MODE_MESSAGE)
                self._curr_modes.update({mode: mode})
            self._prev_modes.clear()
            return

    def _wait_for_messages(self, wait_time_in_milliseconds: int = 5) -> None:
        key_code = cv.waitKey(wait_time_in_milliseconds)
        if key_code == -1:
            for mode in self._curr_modes:
                self.send_message(mode, RUNNING_MODE_MESSAGE)
            return
        self.on_messages_wait(key_code)
        # приостановка любого выполняющегося режима
        if key_code == ord('p'):
            if PAUSE_MODE in self._curr_modes:
                self.resume()
                return
            self.pause()
            return
        # Завершение работы режима
        if key_code == ord('q'):
            self.reboot()
            return
        if key_code == ord('z'):
            self.reset()
            return
        # Выход из камеры
        if key_code == 27:
            self.exit()
            return

    def on_start(self, message: int) -> None:
        ...

    def on_reset(self, message: int) -> None:
        ...

    def on_reboot(self, message: int) -> None:
        ...

    def on_exit(self, message: int) -> None:
        if message == BEGIN_MODE_MESSAGE:
            self.send_message(EXIT_MODE, RUNNING_MODE_MESSAGE)
        if message == RUNNING_MODE_MESSAGE:
            self.send_message(EXIT_MODE, END_MODE_MESSAGE)

    def on_pause(self, message: int) -> None:
        ...

    def on_messages_wait(self, key_code: int) -> None:
        ...

    @property
    def update_time(self) -> float:
        return self._timer.timeout

    @update_time.setter
    def update_time(self, value: float) -> None:
        self._timer.timeout = value

    def send_message(self, mode_info, mode_state) -> None:
        # Если сообщение для ткущего режима
        self._messages.insert(0, DeviceMessage(mode_info, mode_state))

    def pause(self) -> None:
        if PAUSE_MODE in self._curr_modes:
            return
        self.send_message(PAUSE_MODE, BEGIN_MODE_MESSAGE)

    def resume(self) -> None:
        if PAUSE_MODE in self._curr_modes:
            self.send_message(PAUSE_MODE, END_MODE_MESSAGE)

    def exit(self) -> None:
        self.send_message(EXIT_MODE, BEGIN_MODE_MESSAGE)

    def reset(self) -> None:
        self.send_message(RESET_MODE, BEGIN_MODE_MESSAGE)

    def reboot(self) -> None:
        self.send_message(REBOOT_MODE, BEGIN_MODE_MESSAGE)

    def register_callback(self, callback_id: int, callback: Callable[[DeviceMessage], None]) -> bool:
        if callback_id in self._user_callbacks:
            return False
        self._user_callbacks.update({callback_id: Device.DeviceCallback(self.__default, callback)})
        return True

    def stop_all(self):
        for mode in self._curr_modes:
            self.send_message(mode, END_MODE_MESSAGE)

    def mode_active(self, mode: int) -> bool:
        return mode in self._curr_modes

    def update(self) -> None:
        with self._timer:
            if not self._timer.is_loop:
                return
            self._d_time = max(self._timer.last_loop_time, self._timer.timeout)
            self._wait_for_messages()
            while len(self._messages) != 0:
                message = self._messages.pop()
                if message.mode == ANY_MODE:
                    for mode in self._curr_modes:
                        if mode in self._callbacks:
                            self._callbacks[mode].__call__(message)
                        if mode in self._user_callbacks:
                            self._user_callbacks[mode].__call__(message)
                    continue

                if message.mode in self._callbacks:
                    self._callbacks[message.mode].__call__(message)
                if message.mode in self._user_callbacks:
                    self._user_callbacks[message.mode].__call__(message)

    def run(self):
        while True:
            self.update()
            if len(self._curr_modes) == 0:
                break


class DeviceTest(Device):
    def __init__(self):
        super().__init__()

    def on_start(self, message: int):
        super().on_start(message)
        if message == RUNNING_MODE_MESSAGE:
            progres_bar(self._mode_times[START_MODE] / 5.0, "start...")
            if self._mode_times[START_MODE] > 5.0:
                self.send_message(START_MODE, END_MODE_MESSAGE)
                self.send_message(EXIT_MODE, BEGIN_MODE_MESSAGE)

    def on_exit(self, message: int) -> None:
        super().on_exit(message)
        if message == RUNNING_MODE_MESSAGE:
            progres_bar(self._mode_times[EXIT_MODE] / 5.0, "exit...")
            if self._mode_times[EXIT_MODE] > 5.0:
                self.send_message(EXIT_MODE, END_MODE_MESSAGE)




# d = DeviceTest()
# d.run()




