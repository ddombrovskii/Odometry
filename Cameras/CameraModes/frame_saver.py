from Cameras.CameraModes.camera_mode import CameraMode
import datetime
import cv2
import os


class FrameSaver(CameraMode):
    def __init__(self, camera_cv):
        super().__init__(camera_cv)

    def _on_run(self, message: int) -> bool:
        now = datetime.datetime.now()
        _dir = 'saved_frames'
        if not os.path.exists(_dir):
            os.mkdir(_dir)

        _curr_dir = f"{_dir}/{now.day}_{now.month}_{now.year}"
        if not os.path.exists(_curr_dir):
            os.mkdir(_curr_dir)

        f_path = f'{_curr_dir}/frame_at_time_{now.hour:2}_{now.minute:2}_{now.second:2}_{now.microsecond:3}.png'
        if not cv2.imwrite(f_path, self.camera.undistorted_frame):
            self.camera.send_log_message(f"failed to save frame at path: {f_path}")
        return False
