from ..camera_calibration import IMAGE_TYPES
from .camera_action import CameraAction
# from ..camera import Camera
import os


class CameraFrameSaver(CameraAction):
    def __init__(self, camera_cv):
        super().__init__(camera_cv)
        self._frames_directory: str = "saved_frames\\"
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

    def _on_run(self) -> bool:
        self._save_frame(self.frames_directory, self.frames_ext)
        return False
