import time


class LoopTimer:
    """
    Интервальный таймер, который можно использоваться в контексте with
    """
    # __slots__ = "__timeout", "__time_start", "__total_time", "__loop_done", "__delta_time"

    def __init__(self, timeout: float = 1.0):
        if timeout <= 0.001:
            self.__timeout = 0.001
        else:
            self.__timeout = timeout
        self._time_enter: float = 0.0
        self._delta_time: float = 0.0
        self._total_time: float = 0.0
        self._loop_done: bool = False

    def __str__(self):
        return f"{{\n" \
               f"\t\"timeout\":        {self.timeout:-1.3f},\n" \
               f"\t\"last_loop_time\": {self.last_loop_time:-1.3f}\n" \
               f"}}"

    def __enter__(self):
        self._time_enter = time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._delta_time = time.perf_counter() - self._time_enter
        self._total_time += self._delta_time
        self._loop_done = self._total_time >= self.__timeout
        if self._loop_done:
            # нахрена это делать? если так нужно, то print(f"done... нужно делать раньше, чем эту операцию
            print(f"done...{self._total_time}")
            self._total_time %= self.__timeout

    @property
    def is_loop(self) -> bool:
        """
        Полное время измеренное таймером
        """
        return self._loop_done

    # @property
    # def time(self) -> float:
    #    """
    #    Полное время измеренное таймером
    #    """
    #    return self.__time_start

    @property
    def last_loop_time(self) -> float:
        """
        Последнее измеренное время
        """
        return self._delta_time

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


if __name__ == "__main__":
    lt = LoopTimer(1.0)

    t = time.time()
    while not lt.is_loop:
        with lt:
            # print("in loop")
            continue
    t = time.time() - t
    print(f"elapsed {t}")
