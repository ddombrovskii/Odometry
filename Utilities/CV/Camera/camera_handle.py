from .camera_calibration import load_camera_calib_info, undistort_image
from .camera_calibration import CameraCalibrationInfo
from typing import Union, TextIO
from . import camera_constants
import numpy as np
import cv2
import sys
import os


class CameraHandle:
    def __init__(self, port: int = 0):
        self._camera_cv: Union[cv2.VideoCapture, None] = None
        self._curr_frame: Union[np.ndarray, None] = None
        self._prev_frame: Union[np.ndarray, None] = None
        self._undistorted_frame: Union[np.ndarray, None] = None
        self._undistorted_rebuild: bool = True
        self._log_stream = sys.stdout  # console print default stream
        self._enable_logging: bool = True
        self._calib_params: Union[CameraCalibrationInfo, None] = None
        if not any(isinstance(port, t_type) for t_type in (int, str)):
            self.make_log_message(f"CV camera arg type {type(port)} is unsupported\n default port = 0 assigned\n")
            port = 0
        self._camera_port: Union[int, str] = port
        if not self._open_camera():
            raise RuntimeError("CV Camera instantiate error")

    def _open_camera(self) -> bool:
        try:
            self._camera_cv = cv2.VideoCapture(self._camera_port, camera_constants.CAP_DSHOW)
            self.fps = 30
        except Exception as ex:
            self.make_log_message(f"CV Camera instantiate error {ex}\n")
            return False
        if not self.is_open:
            return False
        return True

    def close_camera(self) -> bool:
        try:
            self.camera_cv.release()
            self.make_log_message("Camera released...\n")
        except RuntimeError() as ex:
            self.make_log_message(f"Camera dispose error:\n {ex.args}\n")
            return False
        return True

    def __del__(self):
        self.close_camera()

    def __str__(self):
        res: str = "{\n" \
                   f"\"CV_CAP_PROP_FRAME_WIDTH\"  : {self.width:>5},\n" \
                   f"\"CV_CAP_PROP_FRAME_HEIGHT\" : {self.height:>5},\n" \
                   f"\"CAP_PROP_FPS\"             : {self.fps:>5},\n" \
                   f"\"CAP_PROP_EXPOSUREPROGRAM\" : {self.camera_cv.get(camera_constants.CAP_PROP_EXPOSUREPROGRAM)},\n" \
                   f"\"CAP_PROP_POS_MSEC\"        : {self.camera_cv.get(camera_constants.CAP_PROP_POS_MSEC):>5},\n" \
                   f"\"CAP_PROP_FRAME_COUNT\"     : {self.camera_cv.get(camera_constants.CAP_PROP_FRAME_COUNT):>5},\n" \
                   f"\"CAP_PROP_BRIGHTNESS\"      : {self.camera_cv.get(camera_constants.CAP_PROP_BRIGHTNESS):>5},\n" \
                   f"\"CAP_PROP_CONTRAST\"        : {self.camera_cv.get(camera_constants.CAP_PROP_CONTRAST):>5},\n" \
                   f"\"CAP_PROP_SATURATION\"      : {self.camera_cv.get(camera_constants.CAP_PROP_SATURATION):>5},\n" \
                   f"\"CAP_PROP_HUE\"             : {self.camera_cv.get(camera_constants.CAP_PROP_HUE):>5},\n" \
                   f"\"CAP_PROP_GAIN\"            : {self.camera_cv.get(camera_constants.CAP_PROP_GAIN):>5},\n" \
                   f"\"CAP_PROP_CONVERT_RGB\"     : {self.camera_cv.get(camera_constants.CAP_PROP_CONVERT_RGB):>5}\n" \
                   "}"
        return res

    __repr__ = __str__

    def make_log_message(self, message: str) -> None:
        if self.enable_logging:
            print(message, file=self._log_stream, end='')

    @property
    def enable_logging(self) -> bool:
        return self._enable_logging

    @enable_logging.setter
    def enable_logging(self, value: bool) -> None:
        if isinstance(value, bool):
            self._enable_logging = value

    @property
    def logging_stream(self) -> TextIO:
        return self._log_stream

    @logging_stream.setter
    def logging_stream(self, value: TextIO) -> None:
        if not isinstance(value, TextIO):
            self.make_log_message(f"logging stream change error. stream type {type(value)} is unsupported")
            return
        self._log_stream = value

    def get_total_camera_info(self, stream=None):
        def print_key(_key):
            return f"\"{_key}\":"

        def print_info(_key):
            return f"\"Info\": {camera_constants.CAMERA_CONSTANTS_INFO[_key]:>40}" if \
                _key in camera_constants.CAMERA_CONSTANTS_INFO else ""

        for key, arg in camera_constants.CAMERA_CONSTANTS.items():
            try:
                val = self.camera_cv.get(arg)
            except cv2.error as _:
                continue
            if val == -1:
                continue
            print(f"{print_key(key):<40}{val:>20}\n{print_info(key)}\n", file=stream)

    def set_resolution(self, resolution: str) -> bool:
        if resolution not in camera_constants.CAMERA_RESOLUTIONS:
            return False
        w, h = camera_constants.CAMERA_RESOLUTIONS[resolution]
        self.height, self.width = h, w
        if w != self.width or h != self.height:
            return False
        return True

    @property
    def calib_params(self) -> CameraCalibrationInfo:
        return self._calib_params

    @calib_params.setter
    def calib_params(self, params: CameraCalibrationInfo) -> None:
        if isinstance(params, bool):
            self._calib_params = params

    def load_calib_params(self, file_path: str) -> bool:
        if not isinstance(file_path, str):
            self.make_log_message(f"Unable to load camera calibration params. File path {file_path} is not string...")
            return False
        if not os.path.exists(file_path):
            self.make_log_message(f"Unable to load camera calibration params. File path {file_path} does not exist...")
            return False
        self._calib_params = load_camera_calib_info(file_path)
        return True

    @property
    def camera_cv(self) -> cv2.VideoCapture:
        """
        Cv камера
        :return: CV.VideoCapture
        """
        return self._camera_cv

    @property
    def is_open(self) -> bool:
        """
        Открыта ли камера?
        :return:
        """
        return self.camera_cv.isOpened()

    @property
    def width(self) -> int:
        return int(self.camera_cv.get(camera_constants.CAP_PROP_FRAME_WIDTH))

    @width.setter
    def width(self, w: int) -> None:
        if self.camera_cv.set(camera_constants.CAP_PROP_FRAME_WIDTH, w):
            return
        self.make_log_message(f"incorrect devices width {w}\n")

    @property
    def height(self) -> int:
        return int(self.camera_cv.get(camera_constants.CAP_PROP_FRAME_HEIGHT))

    @height.setter
    def height(self, h: int) -> None:
        if self.camera_cv.set(camera_constants.CAP_PROP_FRAME_HEIGHT, h):
            return
        self.make_log_message(f"incorrect devices height {h}\n")

    @property
    def offset_x(self) -> int:
        return int(self.camera_cv.get(camera_constants.CAP_PROP_XI_OFFSET_X))

    @offset_x.setter
    def offset_x(self, value) -> None:
        if self.camera_cv.set(camera_constants.CAP_PROP_XI_OFFSET_X, min(max(-self.width, value), self.width)):
            return
        self.make_log_message(f"incorrect devices x - offset {value}\n")

    @property
    def offset_y(self) -> int:
        return int(self.camera_cv.get(camera_constants.CAP_PROP_XI_OFFSET_Y))

    @offset_y.setter
    def offset_y(self, value) -> None:
        if self.camera_cv.set(camera_constants.CAP_PROP_XI_OFFSET_Y, min(max(-self.height, value), self.height)):
            return
        self.make_log_message(f"incorrect devices y - offset {value}\n")

    @property
    def aspect(self) -> float:
        return float(self.width) / float(self.height)

    @property
    def exposure_mode(self) -> str:
        return str(self.camera_cv.get(camera_constants.CAP_PROP_EXPOSUREPROGRAM))

    @exposure_mode.setter
    def exposure_mode(self, value: str):
        self.make_log_message(f"Exposure mode setter is unsupported for this camera\n")

    @property
    def exposure(self) -> float:
        return float(self.camera_cv.get(camera_constants.CAP_PROP_EXPOSURE))

    @exposure.setter
    def exposure(self, value) -> None:
        if self.camera_cv.set(camera_constants.CAP_PROP_EXPOSURE, min(max(-12, value), 12)):
            return
        self.make_log_message(f"incorrect devices y - offset {value}\n")

    @property
    def frame_time(self) -> float:
        try:
            return 1.0 / self.fps
        except ZeroDivisionError as _:
            return 1.0

    @property
    def fps(self) -> int:
        return self.camera_cv.get(camera_constants.CAP_PROP_FPS)

    @fps.setter
    def fps(self, fps: int) -> None:
        if self.camera_cv.set(camera_constants.CAP_PROP_FPS, min(max(1, fps), 60)):
            return
        self.make_log_message(f"incorrect devices fps {fps}\n")

    @property
    def curr_frame(self) -> np.ndarray:
        return self._curr_frame

    @property
    def prev_frame(self) -> np.ndarray:
        return self._prev_frame

    def read_frame(self) -> bool:
        if not self.is_open:
            return False
        try:
            has_frame, cam_frame = self.camera_cv.read()
        except cv2.error as cv_error:
            self.make_log_message(f"CV error: {cv_error}\n")
            return False
        if not has_frame:
            self.make_log_message(f"camera read error: unable to read frame\n")
            return False
        self._undistorted_rebuild = True
        self._prev_frame = self._curr_frame
        self._curr_frame = cam_frame
        return True

    @property
    def undistorted_frame(self) -> np.ndarray:
        if self._calib_params is None:
            return self.curr_frame
        if self._undistorted_rebuild:
            self._undistorted_frame = undistort_image(self.curr_frame, self._calib_params)
            self._undistorted_rebuild = False
        return self._undistorted_frame
