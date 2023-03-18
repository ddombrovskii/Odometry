from typing import List, Callable, Dict
from collections import namedtuple
from Utilities import LoopTimer
import cv2 as cv


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
DISCARD_MODE_MESSAGE = -1


def device_progres_bar(val: float, label: str = "", max_chars: int = 55,
                       char_progress: str = '#', char_stand_by: str = '.' ) -> str:
    filler_l = int(min(max(0.0, val), 1.0) * max_chars)  # max_chars - title chars count
    filler_r = max_chars - filler_l
    if len(label) == 0:
        return f'\r|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|' if filler_r != 0 else\
            f'\r|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|\n'

    return f'\r|{label:15}|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|' if filler_r != 0 else \
        f'\r|{label:15}|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|\n'


class DeviceMessage(namedtuple('DeviceMessage', 'mode, mode_arg')):
    __slots__ = ()

    def __new__(cls, mode: int = -1, mode_arg: int = -1):
        return super().__new__(cls, int(mode),  int(mode_arg))

    def __str__(self):
        return f"{{\"mode_info\": {self.mode}, \"mode_arg\": {self.mode_arg}}}"


class Device:
    class DeviceCallback(namedtuple('DeviceCallback', 'service_callback, user_callback')):
        def __new__(cls, service_callback, user_callback):
            return super().__new__(cls, service_callback, user_callback)

        def __call__(self, message: DeviceMessage) -> int:
            self.service_callback.__call__(message)
            return self.user_callback.__call__(message)
    """
    Базовое поведение для устройства, которое может работать в одном нескольких режимах единовременно
    """
    def __init__(self):
        self._curr_modes: Dict[int, int]   = {}  # текущие режимы и их состояния
        self._mode_times: Dict[int, float] = {}  # время существования в режимах
        self._d_time: float = 0.0  # время между текущим и предыдущим вызовом метода self.update()
        self._timer: LoopTimer = LoopTimer(0.01, init_state=True)  # синхронизирующий таймер
        self._log_messages: List[str] = []
        self._messages: Dict[int, DeviceMessage] = {}  # список сообщений для переключения режимов
        self._callbacks: Dict[int, Callable[[DeviceMessage], None]] = {}  # список служебных функций
        self._user_callbacks: Dict[int, Device.DeviceCallback] = {}  # список пользовательских функций
        # Служебных функции
        self._callbacks.update({START_MODE:  self._start })
        self._callbacks.update({PAUSE_MODE:  self._pause })
        self._callbacks.update({EXIT_MODE:   self._exit  })
        self._callbacks.update({RESET_MODE:  self._reset })
        self._callbacks.update({REBOOT_MODE: self._reboot})
        # Сообщение о запуске
        self.send_message(START_MODE, BEGIN_MODE_MESSAGE)

    def __on_mode_register(self, message: DeviceMessage):
        """
        Регистрация нового режима к выполнению
        :param message:
        :return:
        """
        # один и тот же режим дважды не запустить
        if message.mode in self._curr_modes:
            return
        # регистрация времени режима и
        # состояния режима (запуск)
        self._curr_modes[message.mode] = BEGIN_MODE_MESSAGE
        self._mode_times[message.mode] = 0.0

    def __on_mode_unregister(self, message: DeviceMessage):
        # что мертво, умереть не может
        if message.mode not in self._curr_modes:
            return
        # отписка времени режима и
        # отписка режима
        del self._curr_modes[message.mode]
        del self._mode_times[message.mode]

    def __on_mode_run(self, message: DeviceMessage):
        # сколько времени работает режим
        self._mode_times[message.mode] += self._d_time
        # Если мы уже включили этот режим, то ничего не делаем.
        # Нельзя переключить режим в предыдущее состояние (посрать обратно не получится...)
        if message.mode_arg <= self._curr_modes[message.mode]:
            return
        self._curr_modes[message.mode] = message.mode_arg

    def __on_mode_common_behavior(self, message: DeviceMessage) -> None:
        """
        Базовое поведение любого режима.
        В момент включения время работы режима обнуляется.
        После происходит инкремент с каждым вызовом функции update().
        :param message: состояние режима (старт режима, рабочий режим, завершение режима).
        :return:
        """
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self.__on_mode_register(message)
            return

        if message.mode_arg == END_MODE_MESSAGE:
            self.__on_mode_unregister(message)
            return

        self.__on_mode_run(message)

    def stop_all_except(self, except_mode: int):
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
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self.stop_all_except(message.mode)
        self.__on_mode_common_behavior(message)
        self.send_message(message.mode, self.on_reset(message.mode_arg))

    def _reboot(self, message: DeviceMessage) -> None:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self.stop_all_except(message.mode)
        self.__on_mode_common_behavior(message)
        self.send_message(message.mode, self.on_reboot(message.mode_arg))

    def _start(self, message: DeviceMessage) -> None:
        self.__on_mode_common_behavior(message)
        self.send_message(message.mode, self.on_start(message.mode_arg))

    def _exit(self, message: DeviceMessage) -> None:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self.stop_all_except(message.mode_arg)
        self.__on_mode_common_behavior(message)
        self.send_message(message.mode, self.on_exit(message.mode_arg))

    def _pause(self, message: DeviceMessage) -> None:

        self.__on_mode_common_behavior(message)
        self.send_message(message.mode, self.on_pause(message.mode_arg))

        if message.mode_arg == END_MODE_MESSAGE:
            for mode, mode_arg in self._curr_modes.items():
                message = DeviceMessage(mode, mode_arg)
                if message.mode in self._callbacks:
                    self._callbacks[message.mode].__call__(message)
                if message.mode in self._user_callbacks:
                    self.send_message(message.mode, self._user_callbacks[message.mode].__call__(message))

    def _wait_for_messages(self, wait_time_in_milliseconds: int = 5) -> None:
        key_code = cv.waitKey(wait_time_in_milliseconds)
        if key_code == -1:
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

    def on_start(self, message: int) -> int:
        """
        Настраивает поведение в процессе запуска
        :param message:
        :return:
        """
        return message

    def on_reset(self, message: int) -> int:
        """
        Настраивает поведение в процессе сброса
        :param message:
        :return:
        """
        return message

    def on_reboot(self, message: int) -> int:
        """
        Настраивает поведение в процессе перезапуска
        :param message:
        :return:
        """
        return message

    def on_exit(self, message: int) -> int:
        """
        Настраивает поведение в процессе выхода
        :param message:
        :return:
        """
        return END_MODE_MESSAGE

    def on_pause(self, message: int) -> int:
        """
        Настраивает поведение в процессе паузы
        :param message:
        :return:
        """
        return message

    def on_messages_wait(self, key_code: int) -> None:
        """
        Настраивает поведение в процессе ожидания и обработки нажатия клавиш.
        :param key_code:
        :return:
        """
        ...

    def print_log_messages(self, print_stream=None):
        if print_stream is None:
            while len(self._log_messages) != 0:
                print(self._log_messages.pop(), end="")
            return

        while len(self._log_messages) != 0:
            print(self._log_messages.pop(), file=print_stream, end="")

    def send_log_message(self, message: str):
        self._log_messages.insert(0, message)
        if len(self._log_messages) == 1000:
            self.print_log_messages()

    @property
    def update_time(self) -> float:
        """
        Время между соседними запусками функции Update.
        :return:
        """
        return self._timer.timeout

    @update_time.setter
    def update_time(self, value: float) -> None:
        """
        Время между соседними запусками функции Update.
        :return:
        """
        self._timer.timeout = value

    def send_message(self, mode, mode_state) -> None:
        if mode in self._curr_modes:
            message = DeviceMessage(mode, max(self._curr_modes[mode], mode_state))
            self._messages[mode] = message
            return

        if mode_state == BEGIN_MODE_MESSAGE:
            self._messages.update({mode: DeviceMessage(mode, mode_state)})

    def pause(self) -> None:
        """
        Приостанавливает выполнение
        :return:
        """
        if PAUSE_MODE in self._curr_modes:
            return
        self.send_message(PAUSE_MODE, BEGIN_MODE_MESSAGE)

    def resume(self) -> None:
        """
        Возобновляет выполнение
        :return:
        """
        if PAUSE_MODE in self._curr_modes:
            self.send_message(PAUSE_MODE, END_MODE_MESSAGE)

    def exit(self) -> None:
        """
        Завершает выполнение
        :return:
        """
        self.send_message(EXIT_MODE, BEGIN_MODE_MESSAGE)

    def reset(self) -> None:
        """
        Сброс устройства
        :return:
        """
        self.send_message(RESET_MODE, BEGIN_MODE_MESSAGE)

    def reboot(self) -> None:
        """
        Перезапускает устройство
        :return:
        """
        self.send_message(REBOOT_MODE, BEGIN_MODE_MESSAGE)

    def register_callback(self, callback_id: int, callback: Callable[[DeviceMessage], int]) -> bool:
        """
        Регистрация пользовательских функций
        :param callback_id:
        :param callback:
        :return:
        """
        if callback_id in self._user_callbacks:
            return False
        self._user_callbacks.update({callback_id: Device.DeviceCallback(self.__on_mode_common_behavior, callback)})
        return True

    def stop_all(self):
        """
        Завершение всех процессов.
        :return:
        """
        for mode in self._curr_modes:
            self.send_message(mode, END_MODE_MESSAGE)

    def mode_active(self, mode: int) -> bool:
        """
        Проверка работает ли указанный режим
        :param mode:
        :return:
        """
        return mode in self._curr_modes

    def mode_active_time(self, mode: int) -> float:
        """
        Проверка работает ли указанный режим
        :param mode:
        :return:
        """
        return self._mode_times[mode] if self.mode_active(mode) else 0.0

    def update(self) -> None:
        with self._timer:
            if not self._timer.is_loop:
                return

            self.print_log_messages()

            self._d_time = max(self._timer.last_loop_time, self._timer.timeout)

            self._wait_for_messages()

            messages, self._messages = self._messages, {}

            if PAUSE_MODE in messages:
                self._callbacks[PAUSE_MODE].__call__(messages[PAUSE_MODE])
                return

            for mode, message in messages.items():

                if message.mode in self._callbacks:
                    self._callbacks[message.mode].__call__(message)
                if message.mode in self._user_callbacks:
                    self.send_message(message.mode, self._user_callbacks[message.mode].__call__(message))

    def run(self):
        while True:
            self.update()
            if len(self._curr_modes) == 0 and len(self._messages) == 0:
                break


class DeviceTest(Device):
    def __init__(self):
        super().__init__()

    def on_start(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            return RUNNING_MODE_MESSAGE
        if message == RUNNING_MODE_MESSAGE:
            t = self.mode_active_time(START_MODE)
            self.send_log_message(device_progres_bar(t / 1.0, "start..."))
            if t > 1.0:
                self.exit()
                return END_MODE_MESSAGE
            return RUNNING_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def on_exit(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            return RUNNING_MODE_MESSAGE
        if message == RUNNING_MODE_MESSAGE:
            t = self.mode_active_time(EXIT_MODE)
            self.send_log_message(device_progres_bar(t / 1.0, "exit..."))
            if t > 1.0:
                return END_MODE_MESSAGE
            return RUNNING_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE


if __name__ == "__main__":
    # messages1 = [DeviceMessage(i, i) for i in range(3)]
    # messages2 = [] # messages1.copy()
    # while len(messages1) != 0:
    #     message = messages1.pop()
    #     print(f"{message} present in messages" if message in messages2 else f"{message} not present in messages")
    d = DeviceTest()
    d.run()