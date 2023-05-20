from Cameras.slam import SLAM
from Cameras.utilities import get_screen_resolution, CameraCalibrationInfo, CameraCalibrationArgs, \
    load_camera_calib_info
from Utilities import Device, START_MODE, BEGIN_MODE_MESSAGE, RUNNING_MODE_MESSAGE, \
    END_MODE_MESSAGE, DeviceMessage, device_progres_bar
from Utilities.device import DISCARD_MODE_MESSAGE
import Cameras.camera_constants as constants
import datetime as datetime
import numpy as np
import cv2 as cv
import os


CALIBRATION_MODE = 7
SHOW_VIDEO_MODE = 8
RECORD_VIDEO_MODE = 9
READ_FRAME_MODE = 10
SLAM_MODE = 11
FRAME_SAVE_MODE = 12


# TODO Подумать как можно организовать ввод с клавиатуры без cv2.waitKey(timeout)
#  вроде Keyboard либа может решить эту проблему(если она кроссплатформенная)
# TODO исправить запись камеры в рапиде (self._record_video) DONE
# TODO доделать и калибровку (все ли параметры нужны, которые тут используются) DONE
# TODO проверить адекватность работы LoopTimer DONE
# TODO что не так с цветом? почему постоянно серый? DONE
# TODO что сделать с синхронизацией, если например камера работает в одном потоке,
#  а мы запрашиваем изображение или ещё что из другого потока DONE
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
                self._camera_stream = cv.VideoCapture(self._camera_port)  # , constants.CAP_DSHOW)
            else:
                if CameraCV._MAX_CAMERA_PORTS_SUPPORT < CameraCV._LAST_CAMERA_PORT:
                    raise RuntimeError("CV Camera exceed max amount of instances...")
                self._camera_port = CameraCV._LAST_CAMERA_PORT
                self._camera_stream = cv.VideoCapture(self._camera_port)  # , constants.CAP_DSHOW)

                CameraCV._LAST_CAMERA_PORT += 1
        except RuntimeError("CV Camera instantiate error") as ex:
            print(ex.args)
        print(f"self._camera_port: {self._camera_port}")
        if not self.is_open:
            raise RuntimeError("device init function call error")
        super().__init__()
        # TODO Calibration info...
        # calibration info:
        self._camera_calibration_info: CameraCalibrationInfo = None
        # common camera info
        self._window_handle: str = ""  # имя текущего окна
        self._file_name:     str = ""  # имя текущего файла
        self._file_handle        = None  # дескриптор текущего файла
        self._curr_frame: np.ndarray = np.zeros((self.width, self.height, 3), dtype=np.uint8)  # текущий кадр
        self._prev_frame: np.ndarray = np.zeros((self.width, self.height, 3), dtype=np.uint8)  # предыдущий кадр
        # modes callbacks e.t.c...
        self._start_up_time: float = 1.0  # время до начала оперирования
        # инициализация новых режимов работы
        self.register_callback(CALIBRATION_MODE,  self._calibrate)
        self.register_callback(SHOW_VIDEO_MODE,   self._show_video)
        self.register_callback(RECORD_VIDEO_MODE, self._record_video)
        self.register_callback(READ_FRAME_MODE,   self._grab_frame)
        self.register_callback(FRAME_SAVE_MODE,   self._save_frame)
        self.register_callback(SLAM_MODE,         self._slam)
        self.camera_cv.set(constants.CAP_PROP_EXPOSUREPROGRAM, 3)
        self.camera_cv.set(constants.CAP_PROP_EXPOSURE,       -9.0)
        self.camera_cv.set(constants.CAP_PROP_GAIN,            0.0)
        self.camera_cv.set(constants.CAP_PROP_AUTOFOCUS,       0.0)
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
        self._try_to_load_calib_info()

    def __del__(self):
        try:
            self.camera_cv.release()
            CameraCV._FREE_CAMERA_PORTS.append(self._camera_port)
            print("\nCamera released...")
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

    def get_total_camera_info(self, stream=None):
        def print_key(key):
            return f"\"{key}\":"

        def print_info(key):
            return f"\"Info\": {constants.CAMERA_CONSTANTS_INFO[key]:>40}" if key in constants.CAMERA_CONSTANTS_INFO else ""

        for key, arg in constants.CAMERA_CONSTANTS.items():
            try:
                val = self.camera_cv.get(arg)
            except:
                continue
            if val == -1:
                continue
            print(f"{print_key(key):<40}{val:>20}\n{print_info(key)}\n", file=stream)

    def set_resolution(self, resolution: str) -> bool:
        if resolution not in constants.CAMERA_RESOLUTIONS:
            return False
        w, h = constants.CAMERA_RESOLUTIONS[resolution]
        self.width = w
        self.height = h
        if w != self.width:
            return False
        if h != self.height:
            return False
        print(f"{resolution}: {constants.CAMERA_RESOLUTIONS[resolution]}")
        return True

    @property
    def camera_cv(self) -> cv.VideoCapture:
        """
        Cv камера
        :return: cv.VideoCapture
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

    def create_fourcc(self, fourcc: str) -> int:
        if len(fourcc) < 4:
            return 0

    @staticmethod
    def mmio_fourcc(ch0: str, ch1: str, ch2: str, ch3: str):
        assert len(ch0) == 1
        assert len(ch1) == 1
        assert len(ch2) == 1
        assert len(ch3) == 1
        return ord(ch0) | (ord(ch1) << 8 ) | (ord(ch2) << 16)  | (ord(ch3) << 24)

    #  # define mmioFOURCC( ch0, ch1, ch2, ch3 )                \
    #  ((uint32_t)(unsigned char)(ch0) | ((uint32_t)(unsigned char)(ch1) << 8 ) | \
    #          ((uint32_t)(unsigned char)(ch2) << 16 ) | ((uint32_t)(unsigned char)(ch3) << 24 ) )
    #  # endif

    def set_mjpg(self):
        fourcc = CameraCV.mmio_fourcc('M', 'J', 'P', 'G')
        if not self.camera_cv.set(constants.CAP_PROP_FOURCC, fourcc):
            print(f"self.set_mjpg({fourcc}) error")

    def set_rgb(self):
        fourcc = CameraCV.mmio_fourcc('M', 'J', 'P', 'G')
        if not self.camera_cv.set(constants.CAP_PROP_FOURCC, fourcc):
            self.set_mjpg()

    def set_grey(self):
        fourcc = CameraCV.mmio_fourcc('G', 'R', 'E', 'Y')
        if not self.camera_cv.set(constants.CAP_PROP_FOURCC, fourcc):
            self.set_mjpg()

    def set_bgr(self):
        fourcc = CameraCV.mmio_fourcc('B', 'G', 'R', 'X')
        if not self.camera_cv.set(constants.CAP_PROP_FOURCC, fourcc):
            self.set_mjpg()

    def set_yuyv(self):
        fourcc = CameraCV.mmio_fourcc('Y', 'U', 'Y', 'V')
        if not self.camera_cv.set(constants.CAP_PROP_FOURCC, fourcc):
            self.set_mjpg()

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
        if self._camera_calibration_info is None:
            return self.curr_frame
        h, w = self.height, self.width
        new_camera_matrix, roi = cv.getOptimalNewCameraMatrix(self._camera_calibration_info.camera_matrix,
                                                              self._camera_calibration_info.distortion_coefficients,
                                                              (w, h), 1, (w, h))
        # undistorted image
        undistorted_image = cv.undistort(self.curr_frame, self._camera_calibration_info.camera_matrix,
                                         self._camera_calibration_info.distortion_coefficients,
                                         None, new_camera_matrix)
        # crop the image
        x, y, w, h = roi
        undistorted_image = undistorted_image[y: y + h, x: x + w]
        # resize the image
        undistorted_image = cv.resize(undistorted_image, (self.width, self.height), interpolation=cv.INTER_AREA)
        return undistorted_image

    @property
    def world_transform(self) -> np.ndarray:
        if not self.mode_active(SLAM_MODE):
            return np.eye(4, dtype=np.float64)
        return self._slam_detector.transform

    def read_frame(self) -> bool:
        if not self.is_open:
            return False
        try:
            has_frame, cam_frame = self.camera_cv.read()
        except cv.error as err:
            return False
        if not has_frame:
            return False
        self._prev_frame = self._curr_frame
        self._curr_frame = cam_frame
        return True

    def save_frame(self):
        self.begin_mode(FRAME_SAVE_MODE)

    def calibrate(self, calib_results_save_path: str = "calibration_results.json",
                  calib_params: CameraCalibrationArgs = None):
        if not self.begin_mode(CALIBRATION_MODE):
            return
        self.stop_mode(RECORD_VIDEO_MODE)
        self.stop_mode(SLAM_MODE)
        self._calib_params = CameraCalibrationArgs() if calib_params is None else calib_params
        self._file_name = calib_results_save_path if calib_results_save_path is not None else \
            f"calibration_results {datetime.datetime.now().strftime('%H; %M; %S')}.json"

    def record_video(self, recorded_video_save_path: str = None):
        if not self.begin_mode(RECORD_VIDEO_MODE):
            return
        self.stop_mode(SLAM_MODE)
        self.stop_mode(CALIBRATION_MODE)
        self._file_name = recorded_video_save_path if recorded_video_save_path is not None else\
        f"video {datetime.datetime.now().strftime('%H; %M; %S')}.avi"

    def show_video(self):
        self.begin_mode(SHOW_VIDEO_MODE)

    def hide_video(self):
        self.stop_mode(SHOW_VIDEO_MODE)

    def begin_slam(self, slam_results_save_path: str = None):
        if not self.begin_mode(SLAM_MODE):
            return
        self.stop_mode(RECORD_VIDEO_MODE)
        self.stop_mode(CALIBRATION_MODE)
        self.stop_mode(SHOW_VIDEO_MODE)
        self._file_name = slam_results_save_path if slam_results_save_path is not None else\
            f"optical_odometry {datetime.datetime.now().strftime('%H; %M; %S')}.json"

    def end_slam(self) -> bool:
        self.stop_mode(SLAM_MODE)
        self.show_video()
        return False

    def on_start(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self.send_log_message(f'\n|-------------------Camera start up...------------------|\n'
                                  f'|-------------Please stand by and hold still...---------|\n')
            return RUNNING_MODE_MESSAGE
        if message == RUNNING_MODE_MESSAGE:
            t = self.mode_active_time(START_MODE)
            self.send_log_message(device_progres_bar(t / self._start_up_time, "", 55, '|', '_'))
            if t >= self._start_up_time:
                self.begin_mode(READ_FRAME_MODE)
                # self.begin_mode(SHOW_VIDEO_MODE)
                return END_MODE_MESSAGE
            return RUNNING_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def on_reset(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self.stop_all()
            self.begin_mode(START_MODE)
            return RUNNING_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def on_reboot(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self.stop_all()
            self.begin_mode(READ_FRAME_MODE)
            # self.begin_mode(SHOW_VIDEO_MODE)
            return RUNNING_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def on_exit(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            if self._window_handle != "":
                try:
                    cv.destroyWindow(self._window_handle)
                except:
                    pass
            return END_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def on_pause(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self.send_log_message(f"\n|--------------------CameraCV stop...-------------------|")
            return RUNNING_MODE_MESSAGE

        if message == RUNNING_MODE_MESSAGE:
            #  cv.imshow(self._window_handle, self.undistorted_frame)
            return RUNNING_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def on_messages_wait(self, key_code: int) -> None:
        # Завершение работы режима
        if key_code == ord('q') or key_code == ord('v'):
            self.stop_mode(CALIBRATION_MODE)
            self.stop_mode(RECORD_VIDEO_MODE)
            self.stop_mode(SLAM_MODE)
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

    def _resize_window(self):
        if self._window_handle is None:
            return
        if self._window_handle == "":
            return
        # cv.namedWindow(self._window_handle, cv.WINDOW_NORMAL)
        cv.resizeWindow(self._window_handle, self.width, self.height)
        sw, sh = get_screen_resolution()
        cv.moveWindow(self._window_handle, (sw - self.width) >> 1, (sh - self.height) >> 1)

    def _try_to_load_calib_info(self) -> bool:
        file_dir = os.path.dirname(self._file_name)
        if file_dir == "":
            file_dir = '.'
        for file in os.listdir(file_dir):
            if file.startswith("calibration_results"):
                self._camera_calibration_info = load_camera_calib_info(file)
                self._file_name = ""
                if self._camera_calibration_info is None:
                    return False
                self.send_log_message(f"\n|------------------Loaded from file...------------------|\n")
                return True
        return False

    def _calibrate(self, message: DeviceMessage) -> int:

        if message.is_begin:
            self.send_log_message(f"\n|-----------------CameraCV calibrating...---------------|\n"
                                  f"|-------------Please stand by and hold still...---------|")
            if self._calib_params.recalibrate:
                return message.next
            if self._try_to_load_calib_info():
                if "_calib_params" in self.__dict__:
                    del self._calib_params
                return message.end
            return message.next

        if message.is_running:
            # чтение текущего кадра
            self.send_log_message(device_progres_bar((self._mode_times[CALIBRATION_MODE] / 2.0) % 1.0))
            ###############################################
            # Добавляет новый калибровочный кадр по клику #
            ###############################################
            if self.mode_active_time(CALIBRATION_MODE) % 1.0 <= 0.9:
                return message.mode_arg
            # перевод текущего кадра в серый цвет
            frame_gray = cv.cvtColor(self.curr_frame, cv.COLOR_BGR2GRAY)
            # поиск углов шахматной доски
            ret, corners = cv.findChessboardCorners(frame_gray, self._calib_params.ches_board_size, None)
            if ret:
                self._calib_params.obj_points.append(self._calib_params.obj_points_array)
                self._calib_params.image_points.append(corners)
                self.send_log_message("\radded new calibration image")
                corners_2 = cv.cornerSubPix(frame_gray, corners, (11, 11), (-1, -1), self._calib_params.criteria)
                curr_frame = cv.drawChessboardCorners(self.curr_frame, self._calib_params.ches_board_size, corners_2, ret)
                cv.imshow(self._window_handle, curr_frame)
            return message.mode_arg

        if message.is_end:
            if "_calib_params" not in self.__dict__:
                return message.discard

            if len(self._calib_params.obj_points) > 0 and len(self._calib_params.image_points) > 0:
                status, camera_matrix, distortion, r_vectors, t_vectors = \
                    cv.calibrateCamera(self._calib_params.obj_points, self._calib_params.image_points,
                                       (self.width, self.height), None, None)
                if status:
                    self._camera_calibration_info = CameraCalibrationInfo(camera_matrix, distortion,
                                                                          t_vectors, r_vectors)
                    with open(self._file_name, 'wt') as calib_info:
                        print(self._camera_calibration_info, file=calib_info)
                    self._file_name, self._file_handle = "", None

            del self._calib_params

            return message.discard

        return message.discard

    def _record_video(self, message: DeviceMessage) -> int:
        if message.is_begin:
            self.send_log_message(f'\n|----------------CameraCV record video...---------------|')

            if self._file_name is None:
                self._file_name = f"camera record {datetime.datetime.now().strftime('%H; %M; %S')}.avi"

            if len(self._file_name) == 0:
                self._file_name = f"camera record {datetime.datetime.now().strftime('%H; %M; %S')}.avi"
            try:
                fourcc = cv.VideoWriter_fourcc('m', 'p', '4', 'v')
                self._file_handle = cv.VideoWriter(self._file_name, fourcc, self.fps, (self.width, self.height))
            except Exception as _ex:
                self.send_log_message(f"\nVideo recording start failed...\n{_ex.args}")
                self.show_video()
                return message.end
            return message.next

        if message.is_running:
            self.send_log_message(device_progres_bar((self._mode_times[RECORD_VIDEO_MODE] / 10.0) % 1.0, "", 55, '|', '_'))
            self._file_handle.write(self.curr_frame)
            return message.run

        if message.is_end:
            try:
                self._file_handle.release()
                self._file_handle = None
            except Exception as _ex:
                self.send_log_message(f"\nVideo recording file release failed...\n{_ex.args}")
            return message.discard

        return message.discard

    def _show_video(self, message: DeviceMessage) -> int:
        if message.is_begin:
            self.send_log_message(f"\n|-----------------CameraCV show video...----------------|")
            if self._window_handle != "":
                cv.destroyWindow(self._window_handle)
            self._window_handle = "show-video-window"
            cv.namedWindow(self._window_handle, cv.WINDOW_NORMAL)
            self._resize_window()
            return message.next

        if message.is_running:
            frame = self.undistorted_frame
            while True:
                if self.mode_active(CALIBRATION_MODE):
                    frame = cv.putText(frame, "Calibration mode...", (10, 20), cv.FONT_HERSHEY_SIMPLEX, 1,
                                       (50, 45, 240), 2, cv.LINE_AA)
                    break
                if self.mode_active(RECORD_VIDEO_MODE):
                    frame = cv.putText(frame, "Recording mode...", (10, 20), cv.FONT_HERSHEY_SIMPLEX, 1,
                                       (250, 45, 40), 2, cv.LINE_AA)
                    break
                if self.mode_active(SHOW_VIDEO_MODE):
                    frame = cv.putText(frame, "Video mode...", (10, 20), cv.FONT_HERSHEY_SIMPLEX, 1,
                                       (50, 245, 40), 2, cv.LINE_AA)
                    break
                break
            cv.imshow(self._window_handle, frame)
            return message.run

        if message.is_end:
            return message.discard

        return message.discard

    def _save_frame(self, message: DeviceMessage) -> int:
        if message.is_begin:
            if not self.is_open:
                return message.end
            return message.next

        if message.is_running:
            now = datetime.datetime.now()
            _dir = 'saved_frames'
            if not os.path.exists(_dir):
                os.mkdir(_dir)

            _curr_dir = f"{_dir}/{now.day}_{now.month}_{now.year}"
            if not os.path.exists(_curr_dir):
                os.mkdir(_curr_dir)

            f_path = f'{_curr_dir}/frame_at_time_{now.hour:2}_{now.minute:2}_{now.second:2}_{now.microsecond:3}.png'
            if not cv.imwrite(f_path, self.undistorted_frame):
                self.send_log_message(f"failed to save frame at path: {f_path}")
            return message.end

        return message.discard

    def _grab_frame(self, message: DeviceMessage) -> int:
        if message.is_begin:
            if not self.is_open:
                return message.end
            return message.run

        if message.is_running:
            if not self.read_frame():
                self.exit()
                return message.end
            return message.run

        return message.discard

    def _slam(self, message: DeviceMessage):
        if message.is_begin:
            if self._camera_calibration_info is None:
                self.send_log_message("SLAM error: camera is not calibrated")
                return message.end
            self._slam_detector = SLAM(self._camera_calibration_info.camera_matrix)
            try:
                self._file_handle = open(self._file_name, "wt")
            except IOError as err:
                self.send_log_message(f"{err.args}")
                return message.end
            self._file_handle.write("{\n")
            self._file_handle.write(f"\t\"optical_odometry\": \"{datetime.datetime.now().strftime('%H; %M; %S')}\",\n")
            self._file_handle.write(f"\t\"way_points_transforms\": [\n")
            return message.run

        if message.is_running:
            self._slam_detector(self.curr_frame)
            tr = self._slam_detector.transform
            self._file_handle.write("\t{\n")
            self._file_handle.write(f"\t\t\"m00\": {tr[0][0]:20}, \"m01\": {tr[0][1]:20}, \"m02\": {tr[0][2]:20}, \"m03\": {tr[0][3]:20},\n")
            self._file_handle.write(f"\t\t\"m10\": {tr[1][0]:20}, \"m11\": {tr[1][1]:20}, \"m12\": {tr[1][2]:20}, \"m13\": {tr[1][3]:20},\n")
            self._file_handle.write(f"\t\t\"m20\": {tr[2][0]:20}, \"m21\": {tr[2][1]:20}, \"m22\": {tr[2][2]:20}, \"m23\": {tr[2][3]:20}\n")
            self._file_handle.write("\t},\n")
            return message.run

        if message.is_end:
            self._file_handle.seek(self._file_handle.tell() - 3, 0)
            self._file_handle.write("\n\t]\n}")
            try:
                self._file_handle.close()
            except RuntimeError as err:
                print(f"{err.args}")
            if "_slam_detector" in self.__dict__:
                del self._slam_detector

        return message.discard


def camera_cv_test():
    camera = CameraCV()
    camera.hide_video()
    camera.enable_logging = False
    camera.show_video()
    while not camera.is_complete:
        camera.update()


if __name__ == "__main__":
    camera_cv_test()

