from threading import Thread
from typing import Dict, Set, List, Union
from .action import Action
from ..timer import Timer
import asyncio


class ActionsLoop:
    def __init__(self, update_time: float = 0.033):
        self._actions:                Dict[int, Action] = {}
        self._active_actions:         Set [int]         = set()
        # вызов мб асинхронным, поэтому все команды сперва тут
        self._active_actions_request: Set [int]         = set()
        self._non_active_actions:     List[int]         = []
        self._update_time: float                        = max(update_time, 0)
        self._timer:                  Timer             = Timer()

    def _start_action_by_value(self, action: Action) -> bool:
        if self.action_active(action):
            return False
        if not self.got_action(action):
            self.register_action(action)
        if self._actions[action.action_id].start():
            self._active_actions_request.update({action.action_id})
            # self._active_actions.update({action.action_id})
            return True
        return False

    def _start_action_by_id(self, action_id: int) -> bool:
        if not self.got_action(action_id):
            return False
        if self.action_active(action_id):
            return False
        if self._actions[action_id].start():
            # self._active_actions.update({action_id})
            self._active_actions_request.update({action_id})
            return True
        return False

    def _stop_action_by_value(self, action: Action) -> bool:
        if not self.got_action(action):
            return False
        if not self.action_active(action):
            return False
        return self._actions[action.action_id].stop()

    def _stop_action_by_id(self, action_id: int) -> bool:
        if not self.got_action(action_id):
            return False
        if not self.action_active(action_id):
            return False
        return self._actions[action_id].stop()

    def _update(self):
        self._non_active_actions = [action for action in self._active_actions if self._actions[action].update()]
        while len(self._active_actions_request) != 0:
            self._active_actions.update({self._active_actions_request.pop()})
        while len(self._non_active_actions) != 0:
            self._active_actions.remove(self._non_active_actions.pop())

    @property
    def is_complete(self) -> bool:
        """
        Время между соседними запусками функции Update.
        :return:
        """
        return len(self._active_actions) == 0 and len(self._active_actions_request) == 0

    @property
    def is_paused(self) -> bool:
        """
        Время между соседними запусками функции Update.
        :return:
        """
        return len(self._active_actions) == 0

    @property
    def update_time(self) -> float:
        """
        Время между соседними запусками функции Update.
        :return:
        """
        return self._update_time  # _timer.timeout

    @update_time.setter
    def update_time(self, value: float) -> None:
        """
        Время между соседними запусками функции Update.
        :return:
        """
        assert isinstance(value, float)
        self._update_time = max(value, 0.0)

    def got_action(self, action: Union[int, Action]) -> bool:
        """
        Проверка есть ли функция обработчик для указанного режима
        :param action:
        :return:
        """
        if isinstance(action, int):
            return action in self._actions
        if isinstance(action, Action):
            return action.action_id in self._actions
        raise ValueError(f"actions_loop::got_action::invalid type::{type(action)}")

    def action_active(self, action: Union[int, Action]) -> bool:
        """
        Проверка работает ли указанный режим
        :param action:
        :return:
        """
        if isinstance(action, int):
            return action in self._active_actions
        if isinstance(action, Action):
            return action.action_id in self._active_actions
        raise ValueError(f"actions_loop::action_active::invalid type::{type(action)}")

    def start_action(self, action: Union[int, Action]) -> bool:
        """
        Проверка работает ли указанный режим
        :param action:
        :return:
        """
        if isinstance(action, int):
            return self._start_action_by_id(action)
        if isinstance(action, Action):
            return self._start_action_by_value(action)
        raise ValueError(f"actions_loop::start_action::invalid type::{type(action)}")

    def stop_action(self, action: Union[int, Action]) -> bool:
        """
        Проверка работает ли указанный режим
        :param action:
        :return:
        """
        if isinstance(action, int):
            return self._stop_action_by_id(action)
        if isinstance(action, Action):
            return self._stop_action_by_value(action)
        raise ValueError(f"actions_loop::stop_action::invalid type::{type(action)}")

    def register_action(self, action: Action, instantaneous_start: bool = False) -> int:
        if self.got_action(action):
            return -1
        self._actions.update({action.action_id: action})
        if instantaneous_start:
            self.start_action(action)
        return action.action_id

    def pause_action(self,  action: Union[int, Action]) -> bool:
        """
        Проверка работает ли указанный режим
        :param action:
        :return:
        """
        if not self.got_action(action):
            return False
        if not self.action_active(action):
            return False
        if isinstance(action, int):
            self._actions[action].pause()
            return self._actions[action].is_action_paused
        if isinstance(action, Action):
            action.pause()
            return action.is_action_paused
        return False

    def resume_action(self,  action: Union[int, Action]) -> bool:
        """
        Проверка работает ли указанный режим
        :param action:
        :return:
        """
        if not self.got_action(action):
            return False
        if not self.action_active(action):
            return False
        if isinstance(action, int):
            if self._actions[action].is_action_paused:
                self._actions[action].resume()
                return True
        if isinstance(action, Action):
            if action.is_action_paused:
                action.resume()
                return True
        return False

    def pause(self):
        for action_id in self._active_actions:
            self._actions[action_id].pause()

    def resume(self):
        for action_id in self._active_actions:
            self._actions[action_id].resume()

    def stop_all(self) -> bool:
        flag = False
        for action_id in self._active_actions:
            flag |= self._actions[action_id].stop()
        return flag

    def stop_all_except(self,  action: Union[int, Action]) -> bool:
        if not self.got_action(action):
            return False
        if not self.action_active(action):
            self.start_action(action)
        flag = False
        if isinstance(action, int):
            for action_id in self._active_actions:
                if action_id == action:
                    continue
                flag |= self._actions[action_id].stop()
            return flag

        if isinstance(action, Action):
            for action_id in self._active_actions:
                if action_id == action.action_id:
                    continue
                flag |= self._actions[action_id].stop()
            return flag

    async def _main_loop(self):
        while not self.is_complete:
            with self._timer:
                self._update()
            await asyncio.sleep(max(0.0, self.update_time - self._timer.inner_time))

    def run(self):
        asyncio.run(self._main_loop())

    def run_in_separated_thread(self) -> Thread:
        _thread = Thread(target=self.run, daemon=True)
        _thread.start()
        return _thread
