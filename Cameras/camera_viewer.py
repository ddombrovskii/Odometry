from Cameras import CameraCV, get_screen_resolution
from Utilities.Geometry import Vector2
from typing import Tuple
import cv2


class CameraViewer:
    def __init__(self, cam: CameraCV):
        if cam is None:
            raise RuntimeError("")
        self._camera_cv: CameraCV = cam
        self._window_handle: str = "camera_viewer"
        cv2.namedWindow(self._window_handle, cv2.WINDOW_NORMAL)
        self._cntr: Vector2 = Vector2()
        self._size: Vector2 = Vector2(cam.width, cam.height)
        self.to_scr_center()

    def __del__(self):
        if self._window_handle != "":
            try:
                cv2.destroyWindow(self._window_handle)
            except:
                pass

    @property
    def is_size_changed(self):
        window_rect   = cv2.getWindowImageRect(self._window_handle)
        for a, b in zip(window_rect, self._window_rect):
            if a != b:
                return True
        return False

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

    def reshape(self, shape: Tuple[float, float, float, float] ):
        if not self.is_valid:
            return

        new_size = Vector2(shape[2], shape[3])
        new_cntr = Vector2(shape[0] + shape[2] * 0.5, shape[1] + shape[3] * 0.5)

        if self._size == new_size and self._cntr == new_cntr:
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

    # def _on_width_change(self, width: int):
    #     self.resize(Vector2(self._size.x, width))
    # def _on_height_change(self, height: int):
    #     self.resize(Vector2(height, self._size.y))
    # def _on_pos_x_change(self, width: int):
    #     self.resize(Vector2(self._size.x, width))
    # def _on_pos_y_change(self, height: int):
    #     self.resize(Vector2(height, self._size.y))


if  __name__ == "__main__":
    _window_handle: str = "camera_viewer"
    cv2.namedWindow(_window_handle, cv2.WINDOW_NORMAL)
    _window_rect = cv2.getWindowImageRect(_window_handle)
    print(_window_rect)
    _size = Vector2(_window_rect[2], _window_rect[3])
    _cntr = Vector2(_window_rect[0], _window_rect[1]) + _size * 0.5
    sw, sh = get_screen_resolution()
    _cntr = Vector2(int(sw - _size.x) >> 1, int(sh - _size.y) >> 1)
    cv2.moveWindow(_window_handle, int(_cntr.x), int(_cntr.y))

    a = input()
