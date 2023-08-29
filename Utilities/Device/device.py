from typing import List, Callable, Dict, Set
from collections import namedtuple
import cv2 as cv
import threading
import time

START_MODE = 1
PAUSE_MODE = 2
EXIT_MODE = 3
RESET_MODE = 4
REBOOT_MODE = 5
SHUTDOWN_MODE = 6
ANY_MODE = -1

BEGIN_MODE_MESSAGE = 0
RUNNING_MODE_MESSAGE = 1
END_MODE_MESSAGE = 2
DISCARD_MODE_MESSAGE = -1


def device_progres_bar(val: float, label: str = "", max_chars: int = 55,
                       char_progress: str = '#', char_stand_by: str = '.') -> str:
    filler_l = int(min(max(0.0, val), 1.0) * max_chars)  # max_chars - title chars count
    filler_r = max_chars - filler_l
    if len(label) == 0:
        return f'\r|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|' if filler_r != 0 else \
            f'\r|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|\n'

    return f'\r|{label:15}|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|' if filler_r != 0 else \
        f'\r|{label:15}|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|\n'


class DeviceMessage(namedtuple('DeviceMessage', 'mode, mode_arg')):
    __slots__ = ()

    def __new__(cls, mode: int = -1, mode_arg: int = -1):
        return super().__new__(cls, int(mode), int(mode_arg))

    def __str__(self):
        return f"{{\"mode_info\": {self.mode:3}, \"mode_arg\": {self.mode_arg:3}}}"

    @property
    def next(self) -> int:
        if self.is_running:
            return RUNNING_MODE_MESSAGE
        if self.is_begin:
            return self.mode_arg + 1
        if self.is_end:
            return -1

    @property
    def end(self) -> int:
        return END_MODE_MESSAGE

    @property
    def run(self) -> int:
        return RUNNING_MODE_MESSAGE

    @property
    def discard(self) -> int:
        return DISCARD_MODE_MESSAGE

    @property
    def is_begin(self) -> bool:
        return self.mode_arg == BEGIN_MODE_MESSAGE

    @property
    def is_running(self) -> bool:
        return self.mode_arg == RUNNING_MODE_MESSAGE

    @property
    def is_end(self) -> bool:
        return self.mode_arg == END_MODE_MESSAGE


SystemCallback = Callable[[DeviceMessage], None]
Callback = Callable[[int], bool]


class Device:
    """
    Базовое поведение для устройства, которое может работать в одном нескольких режимах единовременно
    """
    def __init__(self):
        self._curr_modes:             Dict[int, int]            = {}  # текущие режимы и их состояния
        self._mode_times:             Dict[int, float]          = {}  # время существования в режимах
        self._messages:               Dict[int, DeviceMessage]  = {}  # список сообщений для переключения режимов
        self._callbacks:              Dict[int, SystemCallback] = {}  # список служебных функций
        self._user_callbacks_ids:     Set[int]                  = set()  # список пользовательских функций
        self._delta_update_call_time: float                     = 0.0  # время между текущим и предыдущим вызовом метода self.update()
        self._update_rate_time:       float                     = 0.1
        self._last_update_call_time:  float                     = 0.0
        self.enable_logging:          bool                      = True
        self._log_messages:           List[str]                 = []
        # Служебных функции
        self._callbacks.update({START_MODE:  self._start })
        self._callbacks.update({PAUSE_MODE:  self._pause })
        self._callbacks.update({EXIT_MODE:   self._exit  })
        self._callbacks.update({RESET_MODE:  self._reset })
        self._callbacks.update({REBOOT_MODE: self._reboot})
        # Сообщение о запуске
        self.begin_mode(START_MODE)

    def _on_mode_register(self, message: DeviceMessage):
        """
        Регистрация нового режима к выполнению
        :param message:
        :return:
        """
        # один и тот же режим дважды не запустить
        if self.mode_active(message.mode):
            return
        # регистрация времени режима и состояния режима (запуск)
        self._curr_modes[message.mode] = RUNNING_MODE_MESSAGE
        self._mode_times[message.mode] = 0.0

    def _on_mode_unregister(self, message: DeviceMessage):
        # что мертво, умереть не может
        if not self.mode_active(message.mode):
            return
        # отписка времени режима и отписка режима
        del self._curr_modes[message.mode]
        del self._mode_times[message.mode]

    def _on_mode_run(self, message: DeviceMessage):
        # сколько времени работает режим
        self._mode_times[message.mode] += self._delta_update_call_time
        # Если мы уже включили этот режим, то ничего не делаем. Нельзя переключить режим в предыдущее состояние.
        if message.mode_arg <= self._curr_modes[message.mode]:
            return
        self._curr_modes[message.mode] = message.mode_arg

    def _on_mode_common_behavior(self, message: DeviceMessage) -> None:
        """
        Базовое поведение любого режима.
        В момент включения время работы режима обнуляется.
        После происходит инкремент с каждым вызовом функции update().
        :param message: состояние режима (старт режима, рабочий режим, завершение режима).
        :return:
        """
        if message.is_begin:
            self._on_mode_register(message)
            return
        if message.is_end:
            self._on_mode_unregister(message)
            return
        self._on_mode_run(message)

    def begin_mode(self, mode) -> bool:
        if not self.got_mode(mode):
            return False
        if self.mode_active(mode):
            return False
        self.send_message(mode, BEGIN_MODE_MESSAGE)
        return True

    def stop_mode(self, mode) -> bool:
        if not self.got_mode(mode):
            return False
        if not self.mode_active(mode):
            return False
        self.send_message(mode, END_MODE_MESSAGE)
        return True

    def stop_all_except(self, except_mode: int) -> bool:
        """
        Генерирует сообщения завершающие все процессы, кроме указанного. Если указанного нет, то запускает его.
        :param except_mode:
        :return: True если процесс был создан при вызове функции. False, если процесс был создан до вызова функции.
        """
        flag = False
        if not self.mode_active(except_mode):
            flag |= self.begin_mode(except_mode)
        for mode in self._curr_modes:
            if mode == except_mode:
                continue
            self.send_message(mode, END_MODE_MESSAGE)
        return flag

    def _callback_exec(self, message: DeviceMessage, callback: Callable[[int], bool]):
        self.send_message(message.mode, RUNNING_MODE_MESSAGE if callback(message.mode_arg) else END_MODE_MESSAGE)

    def _reset(self, message: DeviceMessage) -> None:
        if message.is_begin:
            self.stop_all_except(message.mode)
        if message.is_end:
            self.begin_mode(START_MODE)
        self._callback_exec(message, self.on_reset)

    def _reboot(self, message: DeviceMessage) -> None:
        if message.is_begin:
            self.stop_all_except(message.mode)
        if message.is_end:
            self.begin_mode(START_MODE)
        self._callback_exec(message, self.on_reboot)

    def _start(self, message: DeviceMessage) -> None:
        if message.is_begin:
            self.stop_all_except(message.mode)
        self._callback_exec(message, self.on_start)

    def _exit(self, message: DeviceMessage) -> None:
        if message.is_begin:
            self.stop_all_except(message.mode)
        self._callback_exec(message, self.on_exit)

    def _pause(self, message: DeviceMessage) -> None:
        self.on_pause(message.mode_arg)
        if message.is_end:
            for mode, mode_arg in self._curr_modes.items():
                message = DeviceMessage(mode, mode_arg)
                if message.mode in self._callbacks:
                    self._callbacks[message.mode](message)
            self.send_message(message.mode, END_MODE_MESSAGE)
        self.send_message(message.mode, RUNNING_MODE_MESSAGE)

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

    def on_start(self, message: int) -> bool:
        """
        Настраивает поведение в процессе запуска
        :param message:
        :return:
        """
        return False

    def suspend(self):
        if PAUSE_MODE in self._curr_modes:
            self.resume()
            return
        self.pause()

    def on_reset(self, message: int) -> bool:
        """
        Настраивает поведение в процессе сброса
        :param message:
        :return:
        """
        return False

    def on_reboot(self, message: int) -> bool:
        """
        Настраивает поведение в процессе перезапуска
        :param message:
        :return:
        """
        return False

    def on_exit(self, message: int) -> bool:
        """
        Настраивает поведение в процессе выхода
        :param message:
        :return:
        """
        return False

    def on_pause(self, message: int) -> bool:
        """
        Настраивает поведение в процессе паузы
        :param message:
        :return:
        """
        return False

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
        if not self.enable_logging:
            return
        self._log_messages.insert(0, message)
        if len(self._log_messages) == 1000:
            self.print_log_messages()

    @property
    def is_complete(self) -> bool:
        """
        Время между соседними запусками функции Update.
        :return:
        """
        if len(self._curr_modes) != 0:
            return False
        if len(self._messages) != 0:
            return False
        return True

    @property
    def update_time(self) -> float:
        """
        Время между соседними запусками функции Update.
        :return:
        """
        return self._update_rate_time  # _timer.timeout

    @update_time.setter
    def update_time(self, value: float) -> None:
        """
        Время между соседними запусками функции Update.
        :return:
        """
        self._update_rate_time = value if value > 0.0 else self._update_rate_time

    def send_message(self, mode, mode_state) -> None:

        if self.mode_active(mode):
            message = DeviceMessage(mode, mode_state)
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
        self.begin_mode(PAUSE_MODE)

    def resume(self) -> None:
        """
        Возобновляет выполнение
        :return:
        """
        if PAUSE_MODE in self._curr_modes:
            self.stop_mode(PAUSE_MODE)

    def exit(self) -> None:
        """
        Завершает выполнение
        :return:
        """
        self.begin_mode(EXIT_MODE)

    def reset(self) -> None:
        """
        Сброс устройства
        :return:
        """
        self.begin_mode(RESET_MODE)

    def reboot(self) -> None:
        """
        Перезапускает устройство
        :return:
        """
        self.begin_mode(REBOOT_MODE)

    def register_callback(self, callback: Callback) -> int:
        """
        Регистрация пользовательских функций
        :param callback:
        :return:
        """
        # assert isinstance(Callback, callback)
        callback_id = id(callback)
        if callback_id in self._user_callbacks_ids:
            return -1
        self._user_callbacks_ids.update({callback_id})
        self._callbacks.update({callback_id: lambda message: self._callback_exec(message, callback)})
        return callback_id

    def stop_all(self):
        """
        Завершение всех процессов.
        :return:
        """
        for mode in self._curr_modes:
            self.stop_mode(mode)

    def mode_active(self, mode: int) -> bool:
        """
        Проверка работает ли указанный режим
        :param mode:
        :return:
        """
        return mode in self._curr_modes

    def got_mode(self, mode: int) -> bool:
        """
        Проверка есть ли функция обработчик для указанного режима
        :param mode:
        :return:
        """
        return mode in self._callbacks

    def mode_active_time(self, mode: int) -> float:
        """
        Проверка работает ли указанный режим
        :param mode:
        :return:
        """
        return self._mode_times[mode] if self.mode_active(mode) else 0.0

    def update(self) -> bool:
        curr_t = time.perf_counter()
        delta_t = curr_t - self._last_update_call_time
        if delta_t < self.update_time:
            return False
        self._delta_update_call_time = delta_t

        self._last_update_call_time = curr_t

        self.print_log_messages()

        self._wait_for_messages()

        messages, self._messages = self._messages, {}

        if PAUSE_MODE in messages:
            self._callbacks[PAUSE_MODE](messages[PAUSE_MODE])

        else:
            for mode, message in messages.items():
                if message.mode not in self._callbacks:
                    continue
                self._on_mode_common_behavior(message)
                self._callbacks[message.mode](message)
        return True

    def run_gen(self) -> bool:
        while not self.is_complete:
            yield self.update()

    def run_in_separated_thread(self):
        t = threading.Thread(target=self.run_gen)
        t.start()
        t.join()
        return t


TIME = 5


class DeviceTest(Device):
    def __init__(self):
        super().__init__()

    def on_start(self, message: int) -> bool:
        if message == BEGIN_MODE_MESSAGE:
            return True
        if message == RUNNING_MODE_MESSAGE:
            mode_time = self.mode_active_time(START_MODE)
            self.send_log_message(device_progres_bar(mode_time / TIME, "start..."))
            if mode_time < TIME:
                return True
            return False
        print("on_start is done")
        self.exit()
        return False

    def on_exit(self, message: int) -> bool:
        if message == BEGIN_MODE_MESSAGE:
            return True
        if message == RUNNING_MODE_MESSAGE:
            mode_time = self.mode_active_time(EXIT_MODE)
            self.send_log_message(device_progres_bar(mode_time / TIME, "exit..."))
            if mode_time < TIME:
                return True
            return False
        print("on_exit is done")
        return False


if __name__ == "__main__":
    # messages1 = [DeviceMessage(i, i) for i in range(3)]
    # messages2 = [] # messages1.copy()
    # while len(messages1) != 0:
    #     message = messages1.pop()
    #     print(f"{message} present in messages" if message in messages2 else f"{message} not present in messages")
    d = DeviceTest()
    while not d.is_complete:
        d.update()
