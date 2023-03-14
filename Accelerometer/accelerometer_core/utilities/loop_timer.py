import time


class LoopTimer:
    """
    Интервальный таймер, который можно использоваться в контексте with
    """
    __slots__ = "__timeout", "__time", "__total_time", "__loop_done", "__delta_time"

    def __init__(self, timeout: float = 1.0):
        if timeout <= 0.001:
            self.__timeout = 0.001
        else:
            self.__timeout = timeout
        self.__time: float = 0.0
        self.__delta_time: float = 0.0
        self.__total_time: float = 0.0
        self.__loop_done: bool = False

    def __str__(self):
        return f"{{\n" \
               f"\t\"timeout\":        {self.timeout:-1.3f},\n" \
               f"\t\"time\":           {self.time:-1.3f},\n" \
               f"\t\"last_loop_time\": {self.last_loop_time:-1.3f}\n" \
               f"}}"

    def __enter__(self):
        if self.__loop_done:
            self.__total_time %= self.__timeout
        self.__time = time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__delta_time = time.perf_counter() - self.__time
        self.__total_time += self.__delta_time
        self.__loop_done = self.__total_time > self.__timeout

    @property
    def is_loop(self) -> bool:
        """
        Полное время измеренное таймером
        """
        return self.__loop_done

    @property
    def time(self) -> float:
        """
        Полное время измеренное таймером
        """
        return self.__time

    @property
    def last_loop_time(self) -> float:
        """
        Последнее измеренное время
        """
        return self.__delta_time

    @property
    def timeout(self) -> float:
        """
        Время интервала
        """
        return self.__timeout

    @timeout.setter
    def timeout(self, val: float) -> None:
        if val < 0.0:
            return
        self.__timeout = val
