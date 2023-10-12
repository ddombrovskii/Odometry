from .camera_action_utils import get_screen_resolution
from .camera_action import CameraAction
# from ..camera import Camera
import cv2


class CameraCVController(CameraAction):
    def __init__(self, camera_cv):
        super().__init__(camera_cv)
        self._window_handle = "CameraCV"

    def _center_aligned_window_cv(self):
        cv2.namedWindow(self._window_handle, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self._window_handle, self.camera_device.width, self.camera_device.height)
        sw, sh = get_screen_resolution()
        cv2.moveWindow(self._window_handle, (sw - self.camera_device.width) >> 1, (sh - self.camera_device.height) >> 1)

    def _on_active_modes_update(self, key_code: int) -> None:
        if key_code == 27:  # esc
            self.camera.stop_all()
            return
        if key_code == ord('r'):
            self.camera.record_video()
            return
        if key_code == ord('s'):
            self.camera.record_frames()
            return
        if key_code == ord('f'):
            self.camera.save_frame()
            return

    def _on_start(self) -> bool:
        try:
            self._center_aligned_window_cv()
            return True
        except Exception as _:
            return False

    def _on_run(self) -> bool:
        self._on_active_modes_update(cv2.waitKey(3))
        cv2.imshow(self._window_handle, self.camera_device.undistorted_frame)
        return True

    def _on_end(self) -> bool:
        if self._window_handle != "":
            try:
                cv2.destroyWindow(self._window_handle)
            except cv2.error as _:
                return False
        return True
