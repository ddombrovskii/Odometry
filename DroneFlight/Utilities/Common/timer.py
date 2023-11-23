import time


class Timer:
    """
    Таймер, который можно использоваться в контексте with
    """
    def __init__(self):
        self._time_enter: float =  0.0
        self._time_exit:  float = -1.0
        self._delta_inner_time: float =  0.0
        self._delta_outer_time: float =  0.0
        self._outer_time: float =  0.0
        self._inner_time: float =  0.0

    def __str__(self):
        return f"{{\n" \
               f"\t\"total_time\":       {self.total_time:>.12f},\n" \
               f"\t\"inner_time\":       {self.inner_time:>.12f},\n" \
               f"\t\"outer_time\":       {self.outer_time:>.12f},\n" \
               f"\t\"delta_inner_time\": {self.delta_inner_time:>.12f},\n" \
               f"\t\"delta_outer_time\": {self.delta_outer_time:>.12f}\n" \
               f"}}"

    def __enter__(self):
        self._on_enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._on_exit()

    def _on_enter(self) -> None:
        self._time_enter = time.perf_counter()
        self._delta_outer_time = self._time_enter - self._time_exit if self._time_exit > 0 else 0.0
        self._outer_time += self._delta_outer_time

    def _on_exit(self) -> None:
        self._time_exit = time.perf_counter()
        self._delta_inner_time = self._time_exit - self._time_enter
        self._inner_time += self._delta_inner_time

    def reset(self, hard_reset: bool = False):
        self._outer_time = 0.0
        self._inner_time = 0.0
        if hard_reset:
            self._time_enter = 0.0
            self._time_exit = -1.0
            self._delta_inner_time = 0.0
            self._delta_outer_time = 0.0

    @property
    def delta_inner_time(self) -> float:
        """
        Последнее измеренное время в рамках enter -> exit
        """
        return self._delta_inner_time

    @property
    def delta_outer_time(self) -> float:
        """
        Последнее измеренное время в рамках exit -> enter
        """
        return self._delta_outer_time

    @property
    def inner_time(self) -> float:
        """
        Полное время измеренное в рамках enter -> exit
        """
        return self._inner_time

    @property
    def outer_time(self) -> float:
        """
        Полное время измеренное в рамках enter -> exit
        """
        return self._outer_time

    @property
    def total_time(self) -> float:
        """
        Полное время от первого запуска до текущего
        """
        return self.outer_time + self.inner_time
