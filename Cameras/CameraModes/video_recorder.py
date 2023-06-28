from Cameras.CameraModes.camera_mode import CameraMode
from Utilities.Device import device_progres_bar
import datetime
import cv2


class VideoRecorder(CameraMode):

    @staticmethod
    def video_record_path() -> str:
        return f"camera record {datetime.datetime.now().strftime('%H; %M; %S')}.avi"

    def __init__(self, camera_cv):
        super().__init__(camera_cv)
        self._file_name = ""
        self._file_handle = None

    @property
    def video_record_file_path(self) -> str:
        return self._file_name

    @video_record_file_path.setter
    def video_record_file_path(self, value: str) -> None:
        if value is None:
            self._file_name = VideoRecorder.video_record_path()
            return

        if len(value)  == 0:
            self._file_name = VideoRecorder.video_record_path()
            return
        self._file_name = value

    def _on_start(self, message: int) -> bool:
        if not super()._on_start(message):
            return False
        self.camera.send_log_message(f'\n|----------------CameraCV record video...---------------|')
        self.camera.window_handle = "CameraCV record video..."
        try:
            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            self._file_handle = cv2.VideoWriter(self.video_record_file_path, fourcc, self.camera.fps,
                                                (self.camera.width, self.camera.height))
        except Exception as _ex:
            self.camera.send_log_message(f"\nVideo recording start failed...\n{_ex.args}")
            self.camera.show_video()
            return False
        return True

    def _on_run(self, message: int) -> bool:
        self.camera.send_log_message(
            device_progres_bar((self.camera.mode_active_time(self.handle) / 10.0) % 1.0, "", 55, '|', '_'))
        self._file_handle.write(self.camera.curr_frame)
        return True

    def _on_end(self, message: int) -> bool:
        try:
            self._file_handle.release()
            self._file_handle = None
        except Exception as _ex:
            self.camera.send_log_message(f"\nVideo recording file release failed...\n{_ex.args}")
        return False
