from Cameras.CameraModes.camera_mode import CameraMode


class FrameGrabber(CameraMode):
    def __init__(self, camera_cv):
        super().__init__(camera_cv)

    def _on_run(self, message: int) -> bool:
        if self.camera.read_frame():
            return True
        self.camera.exit()
        return False
