import time


class LoopTimer:
    """
    Интервальный таймер, который можно использоваться в контексте with
    """
    # __slots__ = "__timeout", "__time_start", "__total_time", "__loop_done", "__delta_time"

    def __init__(self, timeout: float = 1.0, init_state: bool = False):
        if timeout <= 0.001:
            self.__timeout = 0.001
        else:
            self.__timeout = timeout
        self._time_enter: float = 0.0
        self._time_exit:  float = -1.0
        self._delta_time: float = 0.0
        self._total_time: float = 0.0
        self._loop_done: bool = init_state

    def __str__(self):
        return f"{{\n" \
               f"\t\"timeout\":        {self.timeout:-1.3f},\n" \
               f"\t\"last_loop_time\": {self.last_loop_time:-1.3f},\n" \
               f"}}"

    def __enter__(self):
        self._delta_time = self._on_enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._delta_time += self._on_exit()

    def _on_enter(self) -> float:
        self._time_enter = time.perf_counter()
        dt = self._time_enter - self._time_exit if self._time_exit > 0 else 0.0
        self._total_time += dt
        return dt

    def _on_exit(self) -> float:
        dt = time.perf_counter() - self._time_enter
        self._total_time += dt
        self._loop_done = self._total_time >= self.__timeout
        if self._loop_done:
            self._total_time = 0.0  # self.__timeout
        self._time_exit = time.perf_counter()
        return dt

    @property
    def is_loop(self) -> bool:
        """
        Полное время измеренное таймером
        """
        return self._loop_done

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
    lt = LoopTimer(0.0333)

    t = 0.0
    while not lt.is_loop:
        t0 = time.perf_counter()
        with lt:
            for i in range(10000):
                pass
        t += time.perf_counter() - t0

    print(f"elapsed {t}")
