from Utilities.Device import Device, BEGIN_MODE_MESSAGE, START_MODE, RUNNING_MODE_MESSAGE, device_progres_bar
from Cameras.utilities import get_screen_resolution, CameraCalibrationInfo, CameraCalibrationArgs, create_fourcc
from Cameras.CameraModes.camera_calibrator import CameraCalibrator
from Cameras.CameraModes.video_recorder import VideoRecorder
from Cameras.CameraModes.frame_grabber import FrameGrabber
from Cameras.CameraModes.video_player import VideoPlayer
from Cameras.CameraModes.camera_slam import CameraSlam
from Cameras.CameraModes.frame_saver import FrameSaver
import Cameras.camera_constants as constants
import numpy as np
import cv2 as cv


# TODO Подумать как можно организовать ввод с клавиатуры без cv2.waitKey(timeout)
#  вроде Keyboard либа может решить эту проблему(если она кроссплатформенная)


class CameraCV(Device):
    _MAX_CAMERA_PORTS_SUPPORT = 32
    _LAST_CAMERA_PORT = 0
    _FREE_CAMERA_PORTS = []

    def __init__(self):
        self._camera_port: int = -1
        self._camera_stream: cv.VideoCapture = None
        try:
            if len(CameraCV._FREE_CAMERA_PORTS) != 0:
                self._camera_port = CameraCV._FREE_CAMERA_PORTS.pop()
                # if win 10 :: self._camera_stream = CV.VideoCapture(self._camera_port)
                self._camera_stream = cv.VideoCapture(self._camera_port, constants.CAP_DSHOW)
            else:
                if CameraCV._MAX_CAMERA_PORTS_SUPPORT < CameraCV._LAST_CAMERA_PORT:
                    raise RuntimeError("CV Camera exceed max amount of instances...")
                self._camera_port = CameraCV._LAST_CAMERA_PORT
                # if win 10 :: self._camera_stream = CV.VideoCapture(self._camera_port)
                self._camera_stream = cv.VideoCapture(self._camera_port, constants.CAP_DSHOW)

                CameraCV._LAST_CAMERA_PORT += 1
        except RuntimeError("CV Camera instantiate error") as ex:
            print(ex.args)
        print(f"self._camera_port: {self._camera_port}")
        if not self.is_open:
            raise RuntimeError("device init function call error")
        super().__init__()
        self._camera_calibration_info: CameraCalibrationInfo = None
        # common camera info
        self._window_handle: str = ""  # имя текущего окна
        self._curr_frame: np.ndarray = np.zeros((self.width, self.height, 3), dtype=np.uint8)  # текущий кадр
        self._prev_frame: np.ndarray = np.zeros((self.width, self.height, 3), dtype=np.uint8)  # предыдущий кадр
        # modes callbacks e.t.c...
        self._start_up_time: float = 1.0  # время до начала оперирования
        # инициализация новых режимов работы
        self._frame_grabber     = FrameGrabber    (self)
        self._frame_saver       = FrameSaver      (self)
        self._video_player      = VideoPlayer     (self)
        self._video_recoder     = VideoRecorder   (self)
        self._camera_calibrator = CameraCalibrator(self)
        self._camera_slam       = CameraSlam      (self)

        self.camera_cv.set(constants.CAP_PROP_EXPOSUREPROGRAM, 1   )
        self.camera_cv.set(constants.CAP_PROP_EXPOSURE,       -12.0)
        self.camera_cv.set(constants.CAP_PROP_GAIN,            0.0 )
        self.camera_cv.set(constants.CAP_PROP_AUTOFOCUS,       0.0 )
        self.camera_cv.set(constants.CAP_PROP_FOCUS,           60.0)
        # self.camera_cv.set(constants.CAP_PROP_SATURATION, 1.0)
        # self.camera_cv.set(constants.CAP_PROP_GAMMA, 4.0)
        # self.camera_cv.set(constants.CAP_PROP_BRIGHTNESS, 100.0)
        # self.camera_cv.set(constants.CAP_PROP_CONVERT_RGB, 0.0)
        self.set_resolution("HD2")
        self.set_mjpg()
        self.width = 640
        self.height = 480
        self.fps = 33
        self._camera_calibrator.search_for_calib_info()

    def __del__(self):
        try:
            self.camera_cv.release()
            CameraCV._FREE_CAMERA_PORTS.append(self._camera_port)
            self.send_log_message("\nCamera released...")
        except RuntimeError() as ex:
            self.send_log_message(f"\nCamera dispose error:\n {ex.args}")
            return False
        return True

    def __str__(self):
        res: str = "/*CV Camera*/\n{{\n" \
                   f"\"CV_CAP_PROP_FRAME_WIDTH\"  : {self.width},\n" \
                   f"\"CV_CAP_PROP_FRAME_HEIGHT\" : {self.height},\n" \
                   f"\"CAP_PROP_FPS\"             : {self.fps},\n" \
                   f"\"CAP_PROP_EXPOSUREPROGRAM\" : {self.camera_cv.get(constants.CAP_PROP_EXPOSUREPROGRAM)},\n" \
                   f"\"CAP_PROP_POS_MSEC\"        : {self.camera_cv.get(constants.CAP_PROP_POS_MSEC)},\n" \
                   f"\"CAP_PROP_FRAME_COUNT\"     : {self.camera_cv.get(constants.CAP_PROP_FRAME_COUNT)},\n" \
                   f"\"CAP_PROP_BRIGHTNESS\"      : {self.camera_cv.get(constants.CAP_PROP_BRIGHTNESS)},\n" \
                   f"\"CAP_PROP_CONTRAST\"        : {self.camera_cv.get(constants.CAP_PROP_CONTRAST)},\n" \
                   f"\"CAP_PROP_SATURATION\"      : {self.camera_cv.get(constants.CAP_PROP_SATURATION)},\n" \
                   f"\"CAP_PROP_HUE\"             : {self.camera_cv.get(constants.CAP_PROP_HUE)},\n" \
                   f"\"CAP_PROP_GAIN\"            : {self.camera_cv.get(constants.CAP_PROP_GAIN)},\n" \
                   f"\"CAP_PROP_CONVERT_RGB\"     : {self.camera_cv.get(constants.CAP_PROP_CONVERT_RGB)}\n}}"
        return res

    __repr__ = __str__

    def _resize_window(self):
        if self._window_handle is None:
            return
        if self._window_handle == "":
            return
        cv.resizeWindow(self._window_handle, self.width, self.height)
        sw, sh = get_screen_resolution()
        cv.moveWindow(self._window_handle, (sw - self.width) >> 1, (sh - self.height) >> 1)

    @property
    def window_handle(self) -> str:
        return self._window_handle

    @window_handle.setter
    def window_handle(self, handle_name: str) -> None:
        if self._window_handle == handle_name:
            return
        try:
            cv.destroyWindow(self._window_handle)
        except cv.error as _:
            pass
        self._window_handle = handle_name
        cv.namedWindow(self._window_handle, cv.WINDOW_NORMAL)
        self._resize_window()

    @property
    def camera_calibration_info(self) -> CameraCalibrationInfo:
        return self._camera_calibration_info

    @camera_calibration_info.setter
    def camera_calibration_info(self, value: CameraCalibrationInfo) -> None:
        self._camera_calibration_info = value

    def get_total_camera_info(self, stream=None):
        def print_key(_key):
            return f"\"{_key}\":"

        def print_info(_key):
            return f"\"Info\": {constants.CAMERA_CONSTANTS_INFO[_key]:>40}" if\
                _key in constants.CAMERA_CONSTANTS_INFO else ""

        for key, arg in constants.CAMERA_CONSTANTS.items():
            try:
                val = self.camera_cv.get(arg)
            except cv.error as _:
                continue
            if val == -1:
                continue
            print(f"{print_key(key):<40}{val:>20}\n{print_info(key)}\n", file=stream)

    def set_resolution(self, resolution: str) -> bool:
        if resolution not in constants.CAMERA_RESOLUTIONS:
            return False
        w, h = constants.CAMERA_RESOLUTIONS[resolution]
        self.height, self.width = h, w
        if w != self.width or h != self.height:
            return False
        self.send_log_message(f"new resolution {resolution}: {constants.CAMERA_RESOLUTIONS[resolution]}")
        return True

    @property
    def camera_cv(self) -> cv.VideoCapture:
        """
        Cv камера
        :return: CV.VideoCapture
        """
        return self._camera_stream

    @property
    def is_open(self) -> bool:
        """
        Открыта ли камера?
        :return:
        """
        return self.camera_cv.isOpened()

    @property
    def pixel_format(self) -> str:
        return self.camera_cv.get(constants.CAP_PROP_FORMAT)

    @pixel_format.setter
    def pixel_format(self, pixel_format) -> None:
        if not self.camera_cv.set(constants.CAP_PROP_FORMAT, pixel_format):
            self.send_log_message(f"incorrect pixel format {pixel_format}\n")
            return

    def set_mjpg(self):
        fourcc = create_fourcc('MJPG')
        if not self.camera_cv.set(constants.CAP_PROP_FOURCC, fourcc):
            self.send_log_message(f"Camera::set_mjpg({fourcc}) error")

    def set_rgb(self):
        fourcc = create_fourcc('MJPG')
        if not self.camera_cv.set(constants.CAP_PROP_FOURCC, create_fourcc('MJPG')):
            self.set_mjpg()
            self.send_log_message(f"Camera::set_rgb({fourcc}) error")

    def set_grey(self):
        fourcc = create_fourcc('GREY')
        if not self.camera_cv.set(constants.CAP_PROP_FOURCC, fourcc):
            self.set_mjpg()
            self.send_log_message(f"Camera::set_grey({fourcc}) error")

    def set_bgr(self):
        fourcc = create_fourcc('BGRX')
        if not self.camera_cv.set(constants.CAP_PROP_FOURCC, fourcc):
            self.set_mjpg()
            self.send_log_message(f"Camera::set_bgr({fourcc}) error")

    def set_yuyv(self):
        fourcc = create_fourcc('YUYV')
        if not self.camera_cv.set(constants.CAP_PROP_FOURCC, fourcc):
            self.set_mjpg()
            self.send_log_message(f"Camera::set_yuyv({fourcc}) error")

    @property
    def width(self) -> int:
        return int(self.camera_cv.get(constants.CAP_PROP_FRAME_WIDTH))

    @width.setter
    def width(self, w: int) -> None:
        if not self.camera_cv.set(constants.CAP_PROP_FRAME_WIDTH, w):
            self.send_log_message(f"incorrect devices width {w}\n")
            return
        self._resize_window()

    @property
    def height(self) -> int:
        return int(self.camera_cv.get(constants.CAP_PROP_FRAME_HEIGHT))

    @height.setter
    def height(self, h: int) -> None:
        if not self.camera_cv.set(constants.CAP_PROP_FRAME_HEIGHT, h):
            self.send_log_message(f"incorrect devices height {h}\n")
            return
        self._resize_window()

    @property
    def offset_x(self) -> int:
        return int(self.camera_cv.get(constants.CAP_PROP_XI_OFFSET_X))

    @offset_x.setter
    def offset_x(self, value) -> None:
        if not self.camera_cv.set(constants.CAP_PROP_XI_OFFSET_X, min(max(-self.width, value), self.width)):
            self.send_log_message(f"incorrect devices x - offset {value}\n")

    @property
    def offset_y(self) -> int:
        return int(self.camera_cv.get(constants.CAP_PROP_XI_OFFSET_Y))

    @offset_y.setter
    def offset_y(self, value) -> None:
        if not self.camera_cv.set(constants.CAP_PROP_XI_OFFSET_Y, min(max(-self.height, value), self.height)):
            self.send_log_message(f"incorrect devices y - offset {value}\n")

    @property
    def aspect(self) -> float:
        return float(self.width) / float(self.height)

    @property
    def exposure_mode(self) -> str:
        return str(self.camera_cv.get(constants.CAP_PROP_EXPOSUREPROGRAM))

    @exposure_mode.setter
    def exposure_mode(self, value: str):
        raise RuntimeError("exposure mode setter is unsupported for this camera")

    @property
    def exposure(self) -> float:
        return float(self.camera_cv.get(constants.CAP_PROP_EXPOSURE))

    @exposure.setter
    def exposure(self, value) -> None:
        if not self.camera_cv.set(constants.CAP_PROP_EXPOSURE, min(max(-12, value), 12)):
            self.send_log_message(f"incorrect devices y - offset {value}\n")

    @property
    def frame_time(self) -> float:
        return 1.0 / float(self.camera_cv.get(constants.CAP_PROP_FPS))

    @property
    def fps(self) -> int:
        return self.camera_cv.get(constants.CAP_PROP_FPS)

    @fps.setter
    def fps(self, fps: int) -> None:
        if not self.camera_cv.set(constants.CAP_PROP_FPS, min(max(1, fps), 60)):
            self.send_log_message(f"incorrect devices fps {fps}\n")
        self.update_time = 1.0 / self.camera_cv.get(constants.CAP_PROP_FPS)

    @property
    def curr_frame(self) -> np.ndarray:
        return self._curr_frame

    @property
    def prev_frame(self) -> np.ndarray:
        return self._prev_frame

    @property
    def undistorted_frame(self) -> np.ndarray:
        # return self.curr_frame
        if self.camera_calibration_info is None:
            return self.curr_frame
        h, w = self.height, self.width
        new_camera_matrix, roi = cv.getOptimalNewCameraMatrix(self.camera_calibration_info.camera_matrix,
                                                              self.camera_calibration_info.distortion_coefficients,
                                                              (w, h), 1, (w, h))
        # undistorted image
        undistorted_image = cv.undistort(self.curr_frame, self.camera_calibration_info.camera_matrix,
                                         self.camera_calibration_info.distortion_coefficients,
                                         None, new_camera_matrix)
        # crop the image
        x, y, w, h = roi
        undistorted_image = undistorted_image[y: y + h, x: x + w]
        # resize the image
        undistorted_image = cv.resize(undistorted_image, (self.width, self.height), interpolation=cv.INTER_AREA)
        return undistorted_image

    def read_frame(self) -> bool:
        if not self.is_open:
            return False
        try:
            has_frame, cam_frame = self.camera_cv.read()
        except cv.error as _:
            return False
        if not has_frame:
            return False
        self._prev_frame = self._curr_frame
        self._curr_frame = cam_frame
        return True

    def save_frame(self):
        self._frame_saver.start()

    def calibrate(self, calib_results_save_path: str = None, calib_params: CameraCalibrationArgs = None):
        if not self._camera_calibrator.start():
            return
        self._video_recoder.stop()
        self._camera_slam.stop()
        self._camera_calibrator.calibration_params = calib_params
        self._camera_calibrator.save_calib_results_file_path = calib_results_save_path

    def record_video(self, recorded_video_save_path: str = None):
        if not self._video_recoder.start():
            return
        self._camera_calibrator.stop()
        self._camera_slam.stop()
        self._video_recoder.video_record_file_path = recorded_video_save_path

    def show_video(self):
        self._video_player.start()

    def hide_video(self):
        self._video_player.stop()

    def begin_slam(self, slam_results_save_path: str = None):
        if not self._camera_slam.start():
            return
        self._video_recoder.stop()
        self._camera_calibrator.stop()
        self._video_player.stop()
        self._camera_slam.slam_record_file_path = slam_results_save_path

    def end_slam(self) -> bool:
        self._camera_slam.stop()
        self.show_video()
        return False

    def on_start(self, message: int) -> bool:
        if message == BEGIN_MODE_MESSAGE:
            self.send_log_message(f'\n|-------------------Camera start up...------------------|\n'
                                  f'|-------------Please stand by and hold still...---------|\n')
            return True
        if message == RUNNING_MODE_MESSAGE:
            t = self.mode_active_time(START_MODE)
            self.send_log_message(device_progres_bar(t / self._start_up_time, "", 55, '|', '_'))
            if t >= self._start_up_time:
                self._frame_grabber.start()
                self._video_player.start()
                return False
            return True
        return False

    def on_reset(self, message: int) -> bool:
        if message == BEGIN_MODE_MESSAGE:
            self.stop_all()
            self.begin_mode(START_MODE)
        return False

    def on_reboot(self, message: int) -> bool:
        if message == BEGIN_MODE_MESSAGE:
            self.stop_all()
            self._frame_grabber.start()
            self._video_player.start()
        return False

    def on_exit(self, message: int) -> bool:
        if message == BEGIN_MODE_MESSAGE:
            if self._window_handle != "":
                try:
                    cv.destroyWindow(self._window_handle)
                except cv.error as _:
                    pass
        return False

    def on_pause(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self.send_log_message(f"\n|--------------------CameraCV stop...-------------------|")
            return True
        return False

    def on_messages_wait(self, key_code: int) -> None:
        # Завершение работы режима
        if key_code == ord('q') or key_code == ord('v'):
            self._camera_calibrator.stop()
            self._video_recoder.stop()
            self._camera_slam.stop()
            return
        # Включение режима калибровки
        if key_code == ord('c'):
            self.calibrate()
            return
        # Включение режима записи
        if key_code == ord('r'):
            self.record_video()
            return
        # Включение режима SLAM
        if key_code == ord('s'):
            self.begin_slam()
            return

        if key_code == ord('f'):
            self.save_frame()
            return


def camera_cv_test():
    camera = CameraCV()
    camera.hide_video()
    camera.enable_logging = False
    camera.show_video()
    while not camera.is_complete:
        camera.update()


if __name__ == "__main__":
    camera_cv_test()

