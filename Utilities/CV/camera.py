from .camera_calibration import undistort_image, load_camera_calib_info
from typing import Union, TextIO, Tuple, Generator, Dict
from .camera_calibration import CameraCalibrationInfo
from .camera_calibration import IMAGE_TYPES
from . import camera_constants
from ..timer import Timer
import numpy as np
import datetime
import platform
import asyncio
import os.path
import time
import sys
import cv2


def _create_path_with_time_stamp(file_name: str, directory: str, ext: str, microseconds: bool = False):
    now = datetime.datetime.now()
    if microseconds:
        return f'{directory}{file_name}{now.hour:2}_{now.minute:2}_{now.second:2}_{now.microsecond:<4}.{ext}'
    return f'{directory}{file_name}{now.hour:2}_{now.minute:2}_{now.second:2}.{ext}'


def _get_scr_res_wind_old() -> Tuple[int, int]:
    try:
        cmd = 'wmic desktopmonitor get screenheight, screenwidth'
        h, w = tuple(map(int, os.popen(cmd).read().split()[-2::]))
        return w, h
    except ValueError as _:
        return 0, 0


def _get_scr_res_wind_new() -> Tuple[int, int]:
    try:
        cmd = 'wmic path Win32_VideoController get VideoModeDescription,' \
              'CurrentVerticalResolution,CurrentHorizontalResolution /format:value'
        line = os.popen(cmd).read()
        lines = [v for v in line.split('\n') if v != ''][0:2]
        lines = [int(v.split('=')[-1]) for v in lines]
        return lines[0], lines[1]
    except ValueError as _:
        return 0, 0


def _get_screen_resolution() -> Tuple[int, int]:
    try:
        if platform.system() == 'Linux':
            screen = os.popen("xrandr -q -d :0").readlines()[0]
            return int(screen.split()[7]), int(screen.split()[9][:-1])
        if platform.system() == 'Windows':
            w, h = _get_scr_res_wind_old()
            if (w, h) == (0, 0):
                w, h = _get_scr_res_wind_new()
            return w, h
    except ValueError as _:
        return 0, 0


_DEFAULT_DIR_NAME = "camera_records\\"
_DEFAULT_VIDEO_RECORDS_DIR_NAME = "camera_records\\recorded_videos\\"
_DEFAULT_FRAMES_RECORDS_DIR_NAME = "camera_records\\recorded_frames\\"
_DEFAULT_FRAMES_DIR_NAME = "camera_records\\saved_frames\\"


# TODO specify calib params path / frames saving directory path / frames recording directory path / video recording path
class Camera:
    """
    q - quite
    s - save frames with time interval (default 1 second)
    r - record video (default 30 fps)
    f - save single frame
    esq - stop saving frames or recording video
    """
    def __init__(self, port: int = 0):
        self._camera_cv: Union[cv2.VideoCapture, None] = None
        self._curr_frame: Union[np.ndarray, None] = None
        self._prev_frame: Union[np.ndarray, None] = None
        self._undistorted_frame: Union[np.ndarray, None] = None
        self._undistorted_rebuild: bool = True
        self._log_stream = sys.stdout  # console print default stream
        self._enable_logging: bool = True
        self._calib_params: Union[CameraCalibrationInfo, None] = None
        self._recording_frames: bool = False
        self._recording_video: bool = False
        if not any(isinstance(port, t_type) for t_type in (int, str)):
            self._make_log_message(f"CV camera arg type {type(port)} is unsupported\n default port = 0 assigned\n")
            port = 0
        self._camera_port: Union[int, str] = port
        if not self._open_camera():
            raise RuntimeError("CV Camera instantiate error")

    def _open_camera(self) -> bool:
        try:
            self._camera_cv = cv2.VideoCapture(self._camera_port, camera_constants.CAP_DSHOW)
            self.fps = 30
        except Exception as ex:
            self._make_log_message(f"CV Camera instantiate error {ex}\n")
            return False
        if not self.is_open:
            return False
        return True

    def _close_camera(self) -> bool:
        try:
            self.camera_cv.release()
            self._make_log_message("Camera released...\n")
        except RuntimeError() as ex:
            self._make_log_message(f"Camera dispose error:\n {ex.args}\n")
            return False
        return True

    def __del__(self):
        self._close_camera()

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

    def _make_log_message(self, message: str) -> None:
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
            self._make_log_message(f"logging stream change error. stream type {type(value)} is unsupported")
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
            self._make_log_message(f"Unable to load camera calibration params. File path {file_path} is not string...")
            return False
        if not os.path.exists(file_path):
            self._make_log_message(f"Unable to load camera calibration params. File path {file_path} does not exist...")
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
        self._make_log_message(f"incorrect devices width {w}\n")

    @property
    def height(self) -> int:
        return int(self.camera_cv.get(camera_constants.CAP_PROP_FRAME_HEIGHT))

    @height.setter
    def height(self, h: int) -> None:
        if self.camera_cv.set(camera_constants.CAP_PROP_FRAME_HEIGHT, h):
            return
        self._make_log_message(f"incorrect devices height {h}\n")

    @property
    def offset_x(self) -> int:
        return int(self.camera_cv.get(camera_constants.CAP_PROP_XI_OFFSET_X))

    @offset_x.setter
    def offset_x(self, value) -> None:
        if self.camera_cv.set(camera_constants.CAP_PROP_XI_OFFSET_X, min(max(-self.width, value), self.width)):
            return
        self._make_log_message(f"incorrect devices x - offset {value}\n")

    @property
    def offset_y(self) -> int:
        return int(self.camera_cv.get(camera_constants.CAP_PROP_XI_OFFSET_Y))

    @offset_y.setter
    def offset_y(self, value) -> None:
        if self.camera_cv.set(camera_constants.CAP_PROP_XI_OFFSET_Y, min(max(-self.height, value), self.height)):
            return
        self._make_log_message(f"incorrect devices y - offset {value}\n")

    @property
    def aspect(self) -> float:
        return float(self.width) / float(self.height)

    @property
    def exposure_mode(self) -> str:
        return str(self.camera_cv.get(camera_constants.CAP_PROP_EXPOSUREPROGRAM))

    @exposure_mode.setter
    def exposure_mode(self, value: str):
        pass
        # raise RuntimeError("exposure mode setter is unsupported for this camera")

    @property
    def exposure(self) -> float:
        return float(self.camera_cv.get(camera_constants.CAP_PROP_EXPOSURE))

    @exposure.setter
    def exposure(self, value) -> None:
        if self.camera_cv.set(camera_constants.CAP_PROP_EXPOSURE, min(max(-12, value), 12)):
            return
        self._make_log_message(f"incorrect devices y - offset {value}\n")

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
        self._make_log_message(f"incorrect devices fps {fps}\n")

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
            self._make_log_message(f"CV error: {cv_error}\n")
            return False
        if not has_frame:
            self._make_log_message(f"camera read error: unable to read frame\n")
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
        # return self.curr_frame if self._calib_params is None else undistort_image(self.curr_frame, self._calib_params)

    def _create_directory(self, dir_path: str) -> str:
        if not isinstance(dir_path, str):
            self._make_log_message(f"Camera CV: create directory error. "
                                   f"Directory path type {type(dir_path)} is unsupported\n")
            return ''
        dir_path = os.path.dirname(dir_path)
        if not os.path.isdir(dir_path):
            try:
                os.mkdir(dir_path)
                return dir_path if dir_path.endswith('\\') else f"{dir_path}\\"
            except IOError as error:
                self._make_log_message(
                    f"Camera CV: create directory error. Directory \"{error}\" creation error {error}\n")
                return ''
        return dir_path if dir_path.endswith('\\') else f"{dir_path}\\"

    def _save_frame(self, path_to_frame: str):
        if not cv2.imwrite(path_to_frame, self.undistorted_frame):
            self._make_log_message(f"failed to save frame at path: {path_to_frame}\n")
        self._make_log_message(f"frame saved at path: {path_to_frame}\n")

    def save_frame(self, directory_path: str = _DEFAULT_FRAMES_DIR_NAME, ext: str = 'png'):
        directory_path = self._create_directory(directory_path)
        if ext not in IMAGE_TYPES:
            ext = 'png'
        yield self._save_frame(_create_path_with_time_stamp("frame_at_time_", directory_path, ext, microseconds=True))

    def record_frames(self, directory_path: str = _DEFAULT_FRAMES_RECORDS_DIR_NAME, ext: str = 'png',
                      interval: float = 1.0):
        if self._recording_frames:
            return
        directory_path = self._create_directory(directory_path)
        if ext not in IMAGE_TYPES:
            ext = 'png'
        self._recording_frames = True
        interval = interval if interval > 0 else self.frame_time
        time_0 = 0.0
        while self._recording_frames:
            if time.perf_counter() -  time_0 > interval:
                time_0 = time.perf_counter()
                yield self._save_frame(_create_path_with_time_stamp("frame_at_time_", directory_path, ext, True))
            yield None

    def record_video(self, video_path: str = _DEFAULT_VIDEO_RECORDS_DIR_NAME, ext: str = 'mp4'):
        if self._recording_video:
            return
        if not isinstance(video_path, str):
            self._make_log_message(f"record video error. directory path type {type(video_path)} is unsupported\n")
            return
        try:
            video_path = _create_path_with_time_stamp("video_at_time_", video_path, ext)
            self._create_directory(video_path)
            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            file_handle = cv2.VideoWriter(video_path, fourcc, self.fps, (self.width, self.height))
        except Exception as _ex:
            self._make_log_message(f"Video recording start failed...\n{_ex.args}\n")
            return
        self._recording_video = True
        while self._recording_video:
            file_handle.write(self.undistorted_frame)
            yield None
        try:
            file_handle.release()
        except Exception as _ex:
            self._make_log_message(f"Video recording file release failed...\n{_ex.args}\n")

    def _stop_all_modes(self):
        self._recording_video = False
        self._recording_frames = False

    def _on_active_modes_update(self, key_code: int, generators: Dict[int, Generator]) -> None:
        """
        Only for Python version >= 3.10
            match key_code:
            case 27:
                self._recording_video = False
                self._recording_frames = False
            case ord('r'):
                self._recording_frames = False
                if not self._recording_video:
                    mode = self.record_video()
                    generators.update({id(mode): mode})
            case ord('s'):
                self._recording_video = False
                if not self._recording_frames:
                    mode = self.record_frames()
                    generators.update({id(mode): mode})
            case ord('f'): self.save_frame()
        """
        # Включение режима записи
        if key_code == 27:  # esc
            self._stop_all_modes()
            return

        if key_code == ord('r'):
            self._recording_frames = False
            if not self._recording_video:
                mode = self.record_video()
                generators.update({id(mode): mode})
            return

        if key_code == ord('s'):
            self._recording_video = False
            if not self._recording_frames:
                mode = self.record_frames()
                generators.update({id(mode): mode})
            return

        if key_code == ord('f'):
            mode = self.save_frame()
            generators.update({id(mode): mode})

    def _center_aligned_window_cv(self, window_handle: str = "camera window"):
        cv2.namedWindow(window_handle, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_handle, self.width, self.height)
        sw, sh = _get_screen_resolution()
        cv2.moveWindow(window_handle, (sw - self.width) >> 1, (sh - self.height) >> 1)

    @staticmethod
    def _generators_next(generators: Dict[int, Generator]):
        disposed_modes = []
        for key, value in generators.items():
            try:
                next(value)
            except StopIteration as _:
                disposed_modes.append(key)
        for mode_id in disposed_modes:
            del generators[mode_id]
        return generators

    async def _main_camera_loop(self, window_handle: str = "camera window"):
        self._center_aligned_window_cv(window_handle)
        modes = {}
        l_timer = Timer()
        frame_time = self.frame_time
        while True:
            with l_timer:
                # ожидаем сигнала с клавиатуры
                key_code = cv2.waitKey(3)
                # завершаем всё
                if key_code == ord('q') or not self.read_frame():
                    self._stop_all_modes()
                    break
                modes = Camera._generators_next(modes)
                cv2.imshow(window_handle, self.undistorted_frame)
                self._on_active_modes_update(key_code, modes)
            await asyncio.sleep(max(0.0, frame_time - l_timer.inner_time))
        Camera._generators_next(modes)

    def run(self, window_handle: str = "camera window"):
        asyncio.run(self._main_camera_loop(window_handle))
