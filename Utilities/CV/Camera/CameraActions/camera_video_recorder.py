from .camera_action_utils import create_path_with_time_stamp, create_directory
from .camera_action import CameraAction
import os.path
import cv2


class CameraVideoRecorder(CameraAction):
    def __init__(self, camera_cv):
        super().__init__(camera_cv)
        self._video_directory: str = "recorded_videos\\"
        self._video_ext: str = 'avi'
        self._file_handle = None

    @property
    def video_record_directory(self) -> str:
        return self._video_directory

    @video_record_directory.setter
    def video_record_directory(self, value: str) -> None:
        if isinstance(value, str):
            self._video_directory = f"{os.path.dirname(value)}\\"

    @property
    def video_ext(self) -> str:
        return self._video_ext

    @video_ext.setter
    def video_ext(self, value: str) -> None:
        if not isinstance(value, str):
            return
        self._video_ext = value

    def _on_start(self) -> bool:
        if not super(CameraVideoRecorder, self)._on_start():
            return False
        try:
            video_path = create_path_with_time_stamp("video_at_time_", self.video_record_directory, self.video_ext)
            create_directory(video_path)
            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            self._file_handle = cv2.VideoWriter(video_path, fourcc, self.camera_device.fps,
                                                (self.camera_device.width, self.camera_device.height))
        except Exception as _ex:
            self.camera_device.make_log_message(f"Video recording start failed...\n{_ex.args}\n")
            return False
        return True

    def _on_run(self) -> bool:
        try:
            self._file_handle.write(self.camera_device.undistorted_frame)
            return True
        except Exception as _:
            return False

    def _on_end(self) -> bool:
        try:
            self._file_handle.release()
            return True
        except Exception as _ex:
            self.camera_device.make_log_message(f"Video recording file release failed...\n{_ex.args}\n")
            return False
