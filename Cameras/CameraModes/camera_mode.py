from Utilities.Device import DeviceMode, Device


class CameraMode(DeviceMode):
    def __init__(self, camera_cv: Device):
        super().__init__(camera_cv)

    @property
    def camera(self):
        return self.device

    def _on_start(self, message: int) -> bool:
        return self.camera.is_open
