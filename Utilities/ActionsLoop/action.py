from ..timer import Timer


STANDBY_MODE_MESSAGE = -1
BEGIN_MODE_MESSAGE  = 0
RUN_MODE_MESSAGE = 1
END_MODE_MESSAGE = 3
PAUSE_MODE_MESSAGE = 2
COMPLETE_MODE_MESSAGE = 4


class Action:
    def __init__(self):
        self._curr_state: int = STANDBY_MODE_MESSAGE
        self._prev_state: int = STANDBY_MODE_MESSAGE
        self._modes = {BEGIN_MODE_MESSAGE: self.__on_start,
                       RUN_MODE_MESSAGE: self.__on_run,
                       END_MODE_MESSAGE: self.__on_end,
                       PAUSE_MODE_MESSAGE: self._on_pause,
                       STANDBY_MODE_MESSAGE: self._on_pause}
        self._life_time_timer: Timer = Timer()

    def _on_start(self) -> bool:
        # True if mode step complete
        return True

    def _on_run(self) -> bool:
        # True if mode step complete
        return True

    def _on_end(self) -> bool:
        # True if mode step complete
        return True

    def _on_pause(self) -> bool:
        # True if mode step complete
        return True

    def __on_start(self) -> None:
        self.__set_action_state(RUN_MODE_MESSAGE if self._on_start() else self.action_state)

    def __on_run(self) -> None:
        self.__set_action_state(END_MODE_MESSAGE if not self._on_run() else self.action_state)

    def __on_end(self) -> None:
        self.__set_action_state(COMPLETE_MODE_MESSAGE if self._on_end() else self.action_state)

    def __update(self):
        # TODO refactor update logic
        if self.action_state not in self._modes:
            return
        self._modes[self.action_state]()

    def __set_action_state(self, state: int) -> bool:
        if state <= self._curr_state:
            return False
        self._prev_state = self._curr_state
        self._curr_state = state
        return True

    @property
    def is_action_done(self) -> bool:
        return self._curr_state == COMPLETE_MODE_MESSAGE

    @property
    def is_action_paused(self) -> bool:
        return self._curr_state == PAUSE_MODE_MESSAGE

    @property
    def action_id(self) -> int:
        return id(self)

    @property
    def action_time(self) -> float:
        return self._life_time_timer.total_time

    @property
    def action_delta_time(self) -> float:
        return self._life_time_timer.inner_time

    @property
    def action_state(self) -> int:
        return self._curr_state

    def start(self, **start_params) -> bool:
        self._curr_state = STANDBY_MODE_MESSAGE
        self._curr_state = STANDBY_MODE_MESSAGE
        return self.__set_action_state(BEGIN_MODE_MESSAGE)

    def stop(self) -> bool:
        return self.__set_action_state(END_MODE_MESSAGE)

    def pause(self):
        self._prev_state = self._curr_state
        self._curr_state = PAUSE_MODE_MESSAGE

    def resume(self):
        self._curr_state = self._prev_state
        self._prev_state = PAUSE_MODE_MESSAGE

    def update(self) -> bool:
        with self._life_time_timer:
            self.__update()
        return self.is_action_done

