from Cameras.CameraModes.camera_mode import CameraMode
import cv2


class VideoPlayer(CameraMode):
    def __init__(self, camera_cv):
        super().__init__(camera_cv)

    def _on_start(self, message: int) -> bool:
        if not super()._on_start(message):
            return False
        self.camera.send_log_message(f"\n|-----------------CameraCV show video...----------------|")
        self.camera.window_handle = "CameraCV video mode..."
        return True

    def _on_run(self, message: int) -> bool:
        cv2.imshow(self.camera.window_handle, self.camera.undistorted_frame)
        return True
