from Cameras import CameraCV, get_screen_resolution
from Utilities import Vector2
import cv2


class CameraViewer:
    def __init__(self, cam: CameraCV):
        if cam is None:
            raise RuntimeError("")
        self._camera_cv: CameraCV = cam
        self._cntr: Vector2 = Vector2()
        self._size: Vector2 = Vector2(cam.width, cam.height)
        self._window_handle: str = "camera_viewer"
        cv2.namedWindow(self._window_handle, cv2.WINDOW_NORMAL)
        self.to_scr_center()

    def __del__(self):
        if self._window_handle != "":
            try:
                cv2.destroyWindow(self._window_handle)
            except:
                pass

    @property
    def is_valid(self):
        if self._window_handle is None:
            return False
        if self._window_handle == "":
            return False
        return True

    def to_scr_center(self):
        if not self.is_valid:
            return
        sw, sh = get_screen_resolution()
        self._cntr = Vector2(int(sw - self._size.x) >> 1,
                             int(sh - self._size.y) >> 1)
        cv2.moveWindow(self._window_handle, int(self._cntr.x), int(self._cntr.y))

    def _resize(self, new_size: Vector2):
        if not self.is_valid:
            return

        aspect = self._camera_cv.aspect

        if new_size.x > new_size.y:
            new_size = Vector2(new_size.x, new_size.x / aspect)
        else:
            new_size = Vector2(new_size.y * aspect, new_size.y)

        self._cntr = Vector2(int(self._cntr.x) << 1 + self._size.x,
                             int(self._cntr.y) << 1 + self._size.y)

        self._cntr = Vector2(int(self._cntr.x - new_size.x) >> 1,
                             int(self._cntr.y - new_size.y) >> 1)

        self._size = new_size

        cv2.resizeWindow(self._window_handle, self._size.x, self._size.y)
        cv2.moveWindow(self._window_handle, int(self._cntr.x), int(self._cntr.y))

    def _on_width_change(self, width: int):
        self._resize(Vector2(self._size.x, width))

    def _on_height_change(self, height: int):
        self._resize(Vector2(height, self._size.y))

    def _on_pos_x_change(self, width: int):
        self._resize(Vector2(self._size.x, width))

    def _on_pos_y_change(self, height: int):
        self._resize(Vector2(height, self._size.y))