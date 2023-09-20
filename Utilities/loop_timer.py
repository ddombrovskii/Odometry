from .timer import Timer


class LoopTimer(Timer):
    """
    Интервальный таймер, который можно использоваться в контексте with
    """
    def __init__(self, timeout: float = 1.0, init_state: bool = False):
        super().__init__()
        self._timeout = 0.001 if timeout <= 0.001 else timeout
        self._loop_done:  bool  =  init_state
        self._loop_time: float  = 0.0

    def __str__(self):
        return f"{{\n" \
               f"\t\"timeout\":          {self.timeout:>.5f},\n" \
               f"\t\"total_time\":       {self.total_time:>.5f},\n" \
               f"\t\"inner_time\":       {self.inner_time:>.5f},\n" \
               f"\t\"outer_time\":       {self.outer_time:>.5f},\n" \
               f"\t\"delta_inner_time\": {self.delta_inner_time:>.10f},\n" \
               f"\t\"delta_outer_time\": {self.delta_outer_time:>.10f}\n" \
               f"}}"

    def _on_enter(self) -> None:
        super()._on_enter()
        self._loop_time += self.delta_outer_time
        if self._loop_done:
            self._loop_done = False

    def _on_exit(self) -> None:
        super()._on_exit()
        self._loop_time += self.delta_inner_time
        (self._loop_done, self._loop_time) = \
            (True, 0.0) if self._loop_time >= self.timeout else (False, self._loop_time)

    @property
    def is_loop(self) -> bool:
        """
        Полное время измеренное таймером
        """
        return self._loop_done

    @property
    def timeout(self) -> float:
        """
        Время интервала
        """
        return self._timeout

    @timeout.setter
    def timeout(self, val: float) -> None:
        if val < 0.0:
            return
        self._timeout = val
