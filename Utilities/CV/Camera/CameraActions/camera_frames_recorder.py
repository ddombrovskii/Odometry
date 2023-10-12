from ..camera_calibration import IMAGE_TYPES
from .camera_action import CameraAction
# from ..camera import Camera
import time
import os


class CameraFramesRecorder(CameraAction):
    def __init__(self, camera_cv, time_interval: float = 1.0):
        super().__init__(camera_cv)
        self._time_interval = time_interval
        self._last_save_time = 0.0
        self._frames_directory: str = "recorded_frames\\"
        self._frames_ext: str = 'png'

    @property
    def frames_directory(self) -> str:
        return self._frames_directory

    @frames_directory.setter
    def frames_directory(self, value: str) -> None:
        if isinstance(value, str):
            self._frames_directory = f"{os.path.dirname(value)}\\"

    @property
    def frames_ext(self) -> str:
        return self._frames_ext

    @frames_ext.setter
    def frames_ext(self, value: str) -> None:
        if not isinstance(value, str):
            return
        if value not in IMAGE_TYPES:
            return
        self._frames_ext = value

    @property
    def time_interval(self) -> float:
        return self._time_interval

    @time_interval.setter
    def time_interval(self, value: float) -> None:
        if not isinstance(value, float):
            return
        self._time_interval = max(0.0, value)

    def _on_run(self) -> bool:
        curr_t = time.perf_counter()
        if curr_t - self._last_save_time > self._time_interval:
            self._save_frame(self.frames_directory, self.frames_ext)
            self._last_save_time = curr_t
        return True
