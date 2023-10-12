from .camera_action_utils import create_directory, _DEFAULT_FRAMES_DIR_NAME, create_path_with_time_stamp
from ..camera_calibration import IMAGE_TYPES
from ..camera_handle import CameraHandle
from Utilities.ActionsLoop import Action
# from ..camera import Camera
import cv2


class CameraAction(Action):
    def _save_frame_to_file(self, path_to_frame: str):
        if not cv2.imwrite(path_to_frame, self.camera.camera_cv.undistorted_frame):
            self.camera_device.make_log_message(f"failed to save frame at path: {path_to_frame}\n")
        self.camera_device.make_log_message(f"frame saved at path: {path_to_frame}\n")

    def _save_frame(self, directory_path: str = _DEFAULT_FRAMES_DIR_NAME, ext: str = 'png'):
        flag, directory_path = create_directory(directory_path)
        if ext not in IMAGE_TYPES:
            ext = 'png'
        if not flag:
            self.camera_device.make_log_message(f"unable to make dir: {directory_path}\n")
        self._save_frame_to_file(create_path_with_time_stamp("frame_at_time_", directory_path, ext, True))

    def __init__(self, camera_cv):
        super().__init__()
        self._camera = camera_cv

    @property
    def camera(self):  # -> Camera:
        return self._camera

    @property
    def camera_device(self) -> CameraHandle:
        return self._camera.camera_cv

    def _on_start(self) -> bool:
        return self.camera.is_open

