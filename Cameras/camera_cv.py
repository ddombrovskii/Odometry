from Utilities import Device, START_MODE, BEGIN_MODE_MESSAGE, RUNNING_MODE_MESSAGE, \
    END_MODE_MESSAGE, DeviceMessage, device_progres_bar
from typing import Tuple, List
import datetime as datetime
import numpy as np
import cv2 as cv

from Utilities.device import DISCARD_MODE_MESSAGE

CALIBRATION_MODE = 7
SHOW_VIDEO_MODE = 8
RECORD_VIDEO_MODE = 9
READ_FRAME_MODE = 10
SLAM_MODE = 11


# TODO Подумать как можно организовать ввод с клавиатуры без cv2.waitKey(timeout)
#  вроде Keyboard либа может решить эту проблему(если она кроссплатформенная)
# TODO исправить запись камеры в рапиде (self._record_video)
# TODO доделать и калибровку (все ли параметры нужны, которые тут используются)
# TODO проверить адекватность работы LoopTimer DONE
# TODO что не так с цветом? почему постоянно серый?
# TODO что сделать с синхронизацией, если например камера работает в одном потоке,
#  а мы запрашиваем изображение или ещё что из другого потока
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
                self._camera_stream = cv.VideoCapture(self._camera_port, cv.CAP_DSHOW)
            else:
                if CameraCV._MAX_CAMERA_PORTS_SUPPORT < CameraCV._LAST_CAMERA_PORT:
                    raise RuntimeError("CV Camera exceed max amount of instances...")
                self._camera_port = CameraCV._LAST_CAMERA_PORT
                self._camera_stream = cv.VideoCapture(self._camera_port, cv.CAP_DSHOW)

                CameraCV._LAST_CAMERA_PORT += 1

        except RuntimeError("CV Camera instantiate error") as ex:
            print(ex.args)

        if not self.is_open:
            raise RuntimeError("device init function call error")
        super().__init__()
        # TODO Calibration info...
        # calibration info:
        self._ches_board_size: Tuple[int, int] = (7, 5)
        self._objects_points: List[np.ndarray] = []  # калибровочные точки в мировом пространстве
        self._image_points: List[np.ndarray] = []  # калибровочные точки в пространстве изображения
        self._criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self._camera_matrix: List[np.ndarray] = []
        self._distortion: List[np.ndarray] = []
        self._rotation_vectors: Tuple[np.ndarray] = None
        self._translation_vectors: Tuple[np.ndarray] = None
        self.obj_p: np.ndarray = np.zeros((self._ches_board_size[0] * self._ches_board_size[1], 3), np.float32)
        self.obj_p[:, :2] = np.mgrid[0:self._ches_board_size[0], 0:self._ches_board_size[1]].T.reshape(-1, 2)
        # common camera info
        self._window_handle: str = ""  # имя текущего окна
        self._file_name:     str = ""  # имя текущего файла
        self._file_handle        = None  # дескриптор текущего файла
        self._curr_frame: np.ndarray = np.zeros((self.width, self.height, 3), dtype=np.uint8)  # текущий кадр
        self._prev_frame: np.ndarray = np.zeros((self.width, self.height, 3), dtype=np.uint8)  # предыдущий кадр
        # modes callbacks e.t.c...
        self._start_up_time: float = 1.0  # время до начала оперирования
        # инициализация новых режимов работы
        self.register_callback(CALIBRATION_MODE, self._calibrate)
        self.register_callback(SHOW_VIDEO_MODE, self._show_video)
        self.register_callback(RECORD_VIDEO_MODE, self._record_video)
        self.register_callback(READ_FRAME_MODE, self._grab_frame)
        # self.register_callback(SLAM_MODE, self._slam)
        self.fps = 30
        self.width = 1000
        self.height = 1000
        print(self)

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
                   f"\"CAP_PROP_EXPOSUREPROGRAM\" : {self.camera_cv.get(cv.CAP_PROP_EXPOSUREPROGRAM)},\n" \
                   f"\"CAP_PROP_POS_MSEC\"        : {self.camera_cv.get(cv.CAP_PROP_POS_MSEC)},\n" \
                   f"\"CAP_PROP_FRAME_COUNT\"     : {self.camera_cv.get(cv.CAP_PROP_FRAME_COUNT)},\n" \
                   f"\"CAP_PROP_BRIGHTNESS\"      : {self.camera_cv.get(cv.CAP_PROP_BRIGHTNESS)},\n" \
                   f"\"CAP_PROP_CONTRAST\"        : {self.camera_cv.get(cv.CAP_PROP_CONTRAST)},\n" \
                   f"\"CAP_PROP_SATURATION\"      : {self.camera_cv.get(cv.CAP_PROP_SATURATION)},\n" \
                   f"\"CAP_PROP_HUE\"             : {self.camera_cv.get(cv.CAP_PROP_HUE)},\n" \
                   f"\"CAP_PROP_GAIN\"            : {self.camera_cv.get(cv.CAP_PROP_GAIN)},\n" \
                   f"\"CAP_PROP_CONVERT_RGB\"     : {self.camera_cv.get(cv.CAP_PROP_CONVERT_RGB)}\n}}"
        return res

    __repr__ = __str__

    @property
    def camera_cv(self) -> cv.VideoCapture:
        return self._camera_stream

    @property
    def is_open(self) -> bool:
        return self.camera_cv.isOpened()

    @property
    def pixel_format(self) -> str:
        return self.camera_cv.get(cv.CAP_PROP_FORMAT)

    @pixel_format.setter
    def pixel_format(self, pixel_format: str) -> None:
        raise RuntimeError("pixel format setter is unsupported for this camera")

    @property
    def width(self) -> int:
        return int(self.camera_cv.get(cv.CAP_PROP_FRAME_WIDTH))

    @width.setter
    def width(self, w: int) -> None:
        if not self.camera_cv.set(cv.CAP_PROP_FRAME_WIDTH, w):
            self.send_log_message(f"incorrect devices width {w}\n")
            return

    @property
    def height(self) -> int:
        return int(self.camera_cv.get(cv.CAP_PROP_FRAME_HEIGHT))

    @height.setter
    def height(self, h: int) -> None:
        if not self.camera_cv.set(cv.CAP_PROP_FRAME_HEIGHT, h):
            self.send_log_message(f"incorrect devices height {h}\n")
            return

    @property
    def offset_x(self) -> int:
        return int(self.camera_cv.get(cv.CAP_PROP_XI_OFFSET_X))

    @offset_x.setter
    def offset_x(self, value) -> None:
        if not self.camera_cv.set(cv.CAP_PROP_XI_OFFSET_X, min(max(-self.width, value), self.width)):
            self.send_log_message(f"incorrect devices x - offset {value}\n")

    @property
    def offset_y(self) -> int:
        return int(self.camera_cv.get(cv.CAP_PROP_XI_OFFSET_Y))

    @offset_y.setter
    def offset_y(self, value) -> None:
        if not self.camera_cv.set(cv.CAP_PROP_XI_OFFSET_Y, min(max(-self.height, value), self.height)):
            self.send_log_message(f"incorrect devices y - offset {value}\n")

    @property
    def aspect(self) -> float:
        return float(self.width) / float(self.height)

    @property
    def exposure_mode(self) -> str:
        return str(self.camera_cv.get(cv.CAP_PROP_EXPOSUREPROGRAM))

    @exposure_mode.setter
    def exposure_mode(self, value: str):
        raise RuntimeError("exposure mode setter is unsupported for this camera")

    @property
    def exposure(self) -> float:
        return float(self.camera_cv.get(cv.CAP_PROP_EXPOSURE))

    @exposure.setter
    def exposure(self, value) -> None:
        if not self.camera_cv.set(cv.CAP_PROP_EXPOSURE, min(max(-12, value), 12)):
            self.send_log_message(f"incorrect devices y - offset {value}\n")

    @property
    def frame_time(self) -> float:
        return 1.0 / float(self.camera_cv.get(cv.CAP_PROP_FPS))

    @property
    def fps(self) -> int:
        return self.camera_cv.get(cv.CAP_PROP_FPS)

    @fps.setter
    def fps(self, fps: int) -> None:
        if not self.camera_cv.set(cv.CAP_PROP_FPS, min(max(1, fps), 60)):
            self.send_log_message(f"incorrect devices fps {fps}\n")
        self._timer.timeout = 1.0 / self.camera_cv.get(cv.CAP_PROP_FPS)

    @property
    def curr_frame(self) -> np.ndarray:
        return self._curr_frame

    @property
    def prev_frame(self) -> np.ndarray:
        return self._prev_frame

    @property
    def undistorted_frame(self) -> np.ndarray:
        if len(self._camera_matrix) > 0:
            h, w = self.height, self.width
            new_camera_matrix, roi = cv.getOptimalNewCameraMatrix(self._camera_matrix, self._distortion, (w, h), 1, (w, h))
            # undistorted image
            undistorted_image = cv.undistort(self.curr_frame, self._camera_matrix, self._distortion, None, new_camera_matrix)
            # crop the image
            x, y, w, h = roi
            undistorted_image = undistorted_image[y: y + h, x: x + w]
            # resize the image
            undistorted_image = cv.resize(undistorted_image, (self.width, self.height), interpolation=cv.INTER_AREA)
            return undistorted_image
        return self.curr_frame

    def read_frame(self) -> bool:
        if not self.is_open:
            return False
        has_frame, cam_frame = self.camera_cv.read()
        if not has_frame:
            return False
        self._prev_frame = self._curr_frame
        self._curr_frame = cam_frame
        return True

    def calibrate(self, calib_results_save_path: str = "calibration_results.json"):
        if self.mode_active(CALIBRATION_MODE):
            return

        if self.mode_active(RECORD_VIDEO_MODE):
            self.send_message(RECORD_VIDEO_MODE, END_MODE_MESSAGE)

        if self.mode_active(SLAM_MODE):
            self.send_message(SLAM_MODE, END_MODE_MESSAGE)

        self.send_message(CALIBRATION_MODE, BEGIN_MODE_MESSAGE)
        self._file_name = self._file_name if calib_results_save_path is None else calib_results_save_path

    def record_video(self, recorded_video_save_path: str = None):
        if self.mode_active(RECORD_VIDEO_MODE):
            return

        if self.mode_active(CALIBRATION_MODE):
            self.send_message(CALIBRATION_MODE, END_MODE_MESSAGE)

        if self.mode_active(SLAM_MODE):
            self.send_message(SLAM_MODE, END_MODE_MESSAGE)

        self.send_message(RECORD_VIDEO_MODE, BEGIN_MODE_MESSAGE)
        self._file_name = self._file_name if recorded_video_save_path is None else recorded_video_save_path

    def show_video(self):
        if self.mode_active(SHOW_VIDEO_MODE):
            return
        # self.stop_all_except(READ_FRAME_MODE)
        self.send_message(SHOW_VIDEO_MODE, BEGIN_MODE_MESSAGE)

    def slam(self, slam_results_save_path: str = None) -> bool:
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
                self.send_message(READ_FRAME_MODE, BEGIN_MODE_MESSAGE)
                self.send_message(SHOW_VIDEO_MODE, BEGIN_MODE_MESSAGE)
                return END_MODE_MESSAGE
            return RUNNING_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def on_reset(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self.stop_all()
            self.send_message(START_MODE, BEGIN_MODE_MESSAGE)
            return RUNNING_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def on_reboot(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self.stop_all()
            self.send_message(READ_FRAME_MODE, BEGIN_MODE_MESSAGE)
            self.send_message(SHOW_VIDEO_MODE, BEGIN_MODE_MESSAGE)
            return RUNNING_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def on_exit(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            if self._file_handle != "":
                try:
                    cv.destroyWindow(self._file_handle)
                except:
                    pass
            return END_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def on_messages_wait(self, key_code: int) -> None:
        # Завершение работы режима
        if key_code == ord('q'):
            self.show_video()
            return
        # Включение режима калибровки
        if key_code == ord('c'):
            self.calibrate()
            return
        # Включение режима записи
        if key_code == ord('r'):
            self.record_video()
            return
        # Включение режима видео
        if key_code == ord('v'):
            self.show_video()
            return
        # Включение режима SLAM
        if key_code == ord('s'):
            self.show_video()  # <- затычка
            return

    def _calibrate(self, message: DeviceMessage) -> int:
        """
        "esc", "q" - Прекратить калибровку
        "r" - захват текущего изображения с камеры и калибровка по нему
        """
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self.send_log_message(f"\n|-----------------CameraCV calibrating...---------------|\n"
                                  f"|-------------Please stand by and hold still...---------|")
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == RUNNING_MODE_MESSAGE:
            # чтение текущего кадра
            frame_curr = self.curr_frame
            self.send_log_message(device_progres_bar((self._mode_times[CALIBRATION_MODE] / 2.0)  % 1.0))
            ###############################################
            # Добавляет новый калибровочный кадр по клику #
            ###############################################
            # перевод текущего кадра в серый цвет
            frame_gray = cv.cvtColor(frame_curr, cv.COLOR_BGR2GRAY)
            # поиск углов шахматной доски
            ret, corners = cv.findChessboardCorners(frame_gray, self._ches_board_size, None)
            if ret:
                # TODO obj_points - а нужно ли их вообще в лист помещать???
                # ответ: нужно, но можно каждый раз не создавать obj_points заново
                if self._mode_times[CALIBRATION_MODE] > 2.0:
                    self._objects_points.append(self.obj_p)
                    self._image_points.append(corners)
                    self.send_log_message("\radded new calibration image")

                corners_2 = cv.cornerSubPix(frame_gray, corners, (11, 11), (-1, -1), self._criteria)
                self._curr_frame = cv.drawChessboardCorners(frame_curr, self._ches_board_size, corners_2, ret)
            cv.imshow(self._window_handle, frame_curr)
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == END_MODE_MESSAGE:
            # TODO завершение калибровки на основе данных из obj_points и _image_points
            if len(self._image_points) > 0 and len(self._objects_points) > 0:
                status, camera_matrix, dist, r_vectors, t_vectors = \
                    cv.calibrateCamera(self._objects_points, self._image_points, (self.width, self.height), None, None)

                if status:
                    self._camera_matrix = camera_matrix
                    self._distortion = dist
                    self._rotation_vectors = r_vectors
                    self._translation_vectors = t_vectors
                    self._file_name = "calibration_results.json"

                    with open(self._file_name, 'wt') as calib_info:
                        print("{\n\t\"camera_matrix\": \n\t{", file=calib_info, end="\n\t")
                        for index, value in enumerate(self._camera_matrix.flat):
                            row, col = divmod(index, 3)
                            if index == 8:
                                print(f"\"m{row}{col}\": {value:20}", file=calib_info, end="\n\t},")
                                continue
                            end = "\n\t" if col == 2 else ""
                            print(f"\"m{row}{col}\": {value:20}, ", file=calib_info, end=end)

                        print("\n\t\"distortion\": \n\t[\n\t", file=calib_info, end="")
                        print(', '.join(f"{value:20}"for value in self._distortion.flat), file=calib_info, end="\n\t],")

                        print("\n\t\"rotation_vectors\": \n\t[\n\t", file=calib_info, end="")
                        print(',\n\t'.join(f"\t{{\"x\": {v[0][0]:20}, \"y\": {v[1][0]:20}, \"z\": {v[2][0]:20}}}"
                                         for v in self._rotation_vectors), file=calib_info, end="")
                        print("\n\t],", file=calib_info, end="")

                        print("\n\t\"translation_vectors\": \n\t[\n\t", file=calib_info, end="")
                        print(',\n\t'.join(f"\t{{\"x\": {v[0][0]:20}, \"y\": {v[1][0]:20}, \"z\": {v[2][0]:20}}}"
                                         for v in self._translation_vectors), file=calib_info, end="")
                        print("\n\t]\n}", file=calib_info, end="")

                    self._file_name, self._file_handle = None, None
                self._objects_points, self._image_points = [], []
            return DISCARD_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def _record_video(self, message: DeviceMessage) -> int:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
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
                return END_MODE_MESSAGE
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == RUNNING_MODE_MESSAGE:
            self.send_log_message(device_progres_bar((self._mode_times[RECORD_VIDEO_MODE] / 10.0) % 1.0, "", 55, '|', '_'))

            self._file_handle.write(self.curr_frame)

            return RUNNING_MODE_MESSAGE

        if message.mode_arg == END_MODE_MESSAGE:
            try:
                self._file_handle.release()
                self._file_handle = None
            except Exception as _ex:
                self.send_log_message(f"\nVideo recording file release failed...\n{_ex.args}")
            return DISCARD_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def on_pause(self, message: int) -> int:
        if message == BEGIN_MODE_MESSAGE:
            self.send_log_message(f"\n|--------------------CameraCV stop...-------------------|")
            return RUNNING_MODE_MESSAGE

        if message == RUNNING_MODE_MESSAGE:
            if len(self._camera_matrix) > 0:
                cv.imshow(self._window_handle, self.undistorted_frame)
            else:
                cv.imshow(self._window_handle, self.curr_frame)
            return RUNNING_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def _show_video(self, message: DeviceMessage) -> int:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            self.send_log_message(f"\n|-----------------CameraCV show video...----------------|")
            if self._window_handle != "":
                cv.destroyWindow(self._window_handle)
            self._window_handle = "show-video-window"
            cv.namedWindow(self._window_handle, cv.WINDOW_NORMAL)
            return RUNNING_MODE_MESSAGE
        frame = None
        if message.mode_arg == RUNNING_MODE_MESSAGE:
            if len(self._camera_matrix) > 0:
                frame = self.undistorted_frame
            else:
                frame = self.curr_frame
            while True:
                if self.mode_active(CALIBRATION_MODE):
                    frame = cv.putText(frame, "Calibration mode...", (10, 20), cv.FONT_HERSHEY_SIMPLEX, 1, (50, 45, 240), 2,
                                       cv.LINE_AA)
                    break
                if self.mode_active(RECORD_VIDEO_MODE):
                    frame = cv.putText(frame, "Recording mode...", (10, 20), cv.FONT_HERSHEY_SIMPLEX, 1, (250, 45, 40), 2,
                                           cv.LINE_AA)
                    break
                if self.mode_active(SHOW_VIDEO_MODE):
                    frame = cv.putText(frame, "Video mode...", (10, 20), cv.FONT_HERSHEY_SIMPLEX, 1, (50, 245, 40), 2,
                                           cv.LINE_AA)
                    break
                break
            cv.imshow(self._window_handle, frame)
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == END_MODE_MESSAGE:
            # if self._window_handle == "show-video-window":
            #     cv.destroyWindow(self._window_handle)
            #     self._window_handle = ""
            return DISCARD_MODE_MESSAGE
        return DISCARD_MODE_MESSAGE

    def _grab_frame(self, message: DeviceMessage) -> int:
        if message.mode_arg == BEGIN_MODE_MESSAGE:
            if not self.is_open:
                return END_MODE_MESSAGE
            return RUNNING_MODE_MESSAGE

        if message.mode_arg == RUNNING_MODE_MESSAGE:
            if not self.read_frame():
                self.exit()
                return END_MODE_MESSAGE
            return RUNNING_MODE_MESSAGE

        return DISCARD_MODE_MESSAGE

    def _slam(self, message: int):
        ...



def camera_cv_test():
    cam = CameraCV()
    cam.run()

    # cam.record_frames()


if __name__ == "__main__":
    camera_cv_test()
