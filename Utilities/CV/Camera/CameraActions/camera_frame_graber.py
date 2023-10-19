from .camera_action import CameraAction
# from ..camera import Camera


class CameraFrameGrabber(CameraAction):
    def __init__(self, camera_cv):
        super().__init__(camera_cv)

    def _on_run(self) -> bool:
        return self.camera_device.read_frame()
