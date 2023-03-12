from typing import Tuple, List
import datetime as datetime
from cgeo import LoopTimer
import numpy as np
import cv2 as cv
import sys


CALIBRATION_MODE = 0
SHOW_VIDEO_MODE = 1
RECORD_VIDEO_MODE = 2
SLAM_MODE = 3
STOP_MODE = 4
EXIT_MODE = 5
START_UP_MODE = 6
ANY_MODE = -1

# messages
BEGIN_MODE_MESSAGE   = 0
RUNNING_MODE_MESSAGE = 1
STOP_MODE_MESSAGE    = 2


def progres_bar(val: float, max_chars: int = 55, char_progress: str = '#', char_stand_by: str = '.' ):
    filler_l = int(min(max(0.0, val), 1.0) * max_chars)  # max_chars - title chars count
    filler_r = max_chars - filler_l
    sys.stdout.write(f'\r|{"":{char_progress}>{str(filler_l)}}{"":{char_stand_by}<{str(filler_r)}}|')
    if filler_r == 0:
        sys.stdout.write('\n')


class CameraCV:

    def __init__(self):

        self._camera_stream: cv.VideoCapture = None

        try:
            self._camera_stream = cv.VideoCapture(0, cv.CAP_DSHOW)
            self._camera_stream.set(cv.CAP_PROP_FPS, 30)
        except RuntimeError("CV Camera instantiate error") as ex:
            print(ex.args)

        if not self.is_open:
            raise RuntimeError("device init function call error")
        # TODO Calibration info...
        self._ches_board_size: Tuple[int, int] = (8, 8)
        self._objects_points: List[np.ndarray] = []
        self._image_points: List[np.ndarray] = []
        #
        self._start_up_time: float = 1.0  # время до начала оперирования
        self._record_time: float = 10.0  # время записи видео
        self._dtime: float = 1e-6  # временной шаг
        self._time: float = 0.0   # время существования в некотором режиме
        # (для режимов с неограниченным временем _time = -1.0)
        self._mode: int = -1  # текущий режим работы
        self._target_mode: int = START_UP_MODE  # предыдущий режим работы
        self._timer: LoopTimer = LoopTimer(1.0 / self.fps)  # таймер
        self._window_handle: str = ""  # имя текущего окна
        self._file_name:     str = ""  # имя текущего файла
        self._file_handle        = None  # дескриптор текущего файла
        self._curr_frame: np.ndarray = None
        self._prev_frame: np.ndarray = None
        self._curr_frame: np.ndarray = np.zeros((self.width, self.height, 3), dtype=np.uint8)
        self._prev_frame: np.ndarray = np.zeros((self.width, self.height, 3), dtype=np.uint8)

    def __del__(self):
        try:
            self.camera_cv.release()
        except RuntimeError() as ex:
            print(f"dispose error {ex.args}")
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
            print(f"incorrect devices width {w}")
            return

    @property
    def height(self) -> int:
        return int(self.camera_cv.get(cv.CAP_PROP_FRAME_HEIGHT))

    @height.setter
    def height(self, h: int) -> None:
        if not self.camera_cv.set(cv.CAP_PROP_FRAME_HEIGHT, h):
            print(f"incorrect devices height {h}")
            return

    @property
    def offset_x(self) -> int:
        return int(self.camera_cv.get(cv.CAP_PROP_XI_OFFSET_X))

    @offset_x.setter
    def offset_x(self, value) -> None:
        if not self.camera_cv.set(cv.CAP_PROP_XI_OFFSET_X, min(max(-self.width, value), self.width)):
            print(f"incorrect devices x - offset {value}")

    @property
    def offset_y(self) -> int:
        return int(self.camera_cv.get(cv.CAP_PROP_XI_OFFSET_Y))

    @offset_y.setter
    def offset_y(self, value) -> None:
        if not self.camera_cv.set(cv.CAP_PROP_XI_OFFSET_Y, min(max(-self.height, value), self.height)):
            print(f"incorrect devices y - offset {value}")

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
            print(f"incorrect devices y - offset {value}")

    @property
    def frame_time(self) -> float:
        return 1.0 / float(self.camera_cv.get(cv.CAP_PROP_FPS))

    @property
    def fps(self) -> int:
        return self.camera_cv.get(cv.CAP_PROP_FPS)

    @fps.setter
    def fps(self, fps: int) -> None:
        if not self.camera_cv.set(cv.CAP_PROP_FPS, min(max(1, fps), 120)):
            print(f"incorrect devices fps {fps}")

    @property
    def curr_frame(self) -> np.ndarray:
        return self._curr_frame

    @property
    def prev_frame(self) -> np.ndarray:
        return self._prev_frame

    def read_frame(self) -> bool:
        if not self.is_open:
            return False

        has_frame, cam_frame = self.camera_cv.read()

        if not has_frame:
            return False

        self._prev_frame = self._curr_frame
        self._curr_frame = cam_frame
        return True

    def calibrate(self, calib_results_save_path: str = None) -> bool:
        if self._mode == CALIBRATION_MODE:
            return False
        if self._mode == START_UP_MODE:
            return False
        if self._mode == EXIT_MODE:
            return False
        self._mode = CALIBRATION_MODE
        self._file_name = calib_results_save_path
        self._time = 0.0

    def record_video(self, recorded_video_save_path: str = None) -> bool:
        if self._mode == CALIBRATION_MODE:
            return False
        if self._mode == RECORD_VIDEO_MODE:
            return False
        if self._mode == EXIT_MODE:
            return False
        self._mode = RECORD_VIDEO_MODE
        self._file_name = recorded_video_save_path
        self._time = 0.0

    def show_video(self) -> bool:
        if self._mode == SHOW_VIDEO_MODE:
            return False
        if self._mode == CALIBRATION_MODE:
            return False
        if self._mode == RECORD_VIDEO_MODE:
            return False
        if self._mode == EXIT_MODE:
            return False
        self._mode = SHOW_VIDEO_MODE
        self._file_name = None
        self._time = 0.0

    def pause(self):
        # TODO починить
        self._prev_mode = self._mode
        self._mode = STOP_MODE

    def resume(self):
        # TODO починить
        self._mode = self._prev_mode

    def slam(self, slam_results_save_path: str = None) -> bool:
        return False

    def _start(self, message: Tuple[int, int]) -> bool:

        mode, message = message

        if mode != ANY_MODE:
            if mode != START_UP_MODE:
                return False

        if message == BEGIN_MODE_MESSAGE:
            print(f'\n|-------------------Camera start up...------------------|\n'
                    f'|-------------Please stand by and hold still...---------|')
            return True

        if message == RUNNING_MODE_MESSAGE:
            self._time += self._dtime
            progres_bar(self._time / self._start_up_time, 55, '|', '_')
            if self._time >= self._start_up_time:
                self._target_mode = SHOW_VIDEO_MODE
                self._time = 0.0
                print(f"\n|--------------------Warm up is done--------------------|")
                return False
            return True

        if message == STOP_MODE_MESSAGE:
            if mode != START_UP_MODE:
                return False
            self._time = 0.0
            print(f"\n|--------------------Warm up is done--------------------|")
            return False

        return False

    def _calibrate(self, message) -> bool:
        """
        "esc", "q" - Прекратить калибровку
        "r" - захват текущего изображения с камеры и калибровка по нему
        """
        mode, message = message

        if mode != ANY_MODE:
            if mode != CALIBRATION_MODE:
                return False

        if message == BEGIN_MODE_MESSAGE:
            self._time = -1.0
            print(f"\n|----------------CameraCV calibrating...--------------|\n"
                  f"|-------------Please stand by and hold still...---------|")
            if self._window_handle != "":
                cv.destroyWindow(self._window_handle)
            self._window_handle = "calibration-window"
            cv.namedWindow(self._window_handle, cv.WINDOW_NORMAL)
            return True

        if message == RUNNING_MODE_MESSAGE:
            if not self.read_frame():
                print(f"|---------------Calibration is interrupted--------------|")
                self._target_mode = EXIT_MODE
                return False

            key_code = cv.waitKey(2)

            # чтение текущего кадра
            frame_curr = self.curr_frame

            if key_code != ord('r'):  # or key_code == XXX (к - на русском ???):
                ###############################################
                # Добавляет новый калибровочный кадр по клику #
                ###############################################
                # перевод текущего кадра в серый цвет
                frame_gray = cv.cvtColor(frame_curr, cv.COLOR_BGR2GRAY)
                # поиск углов шахматной доски
                ret, corners = cv.findChessboardCorners(frame_gray, self._ches_board_size, None)
                if ret:
                    # TODO obj_points - а нужно ли их вообще в лист помещать???
                    obj_points = np.zeros((self._ches_board_size[0] * self._ches_board_size[1], 3), np.float32)
                    obj_points[:, :2] = np.mgrid[0:self._ches_board_size[0], 0:self._ches_board_size[1]].T.reshape(-1, 2)
                    self._objects_points.append(obj_points)
                    self._image_points.append(corners)
                    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                    corners_2 = cv.cornerSubPix(frame_gray, corners, (11, 11), (-1, -1), criteria)
                    cv.drawChessboardCorners(frame_curr, self._ches_board_size, corners_2, ret)
            cv.imshow(self._window_handle, frame_curr)
            return True

        if message == STOP_MODE_MESSAGE:
            if mode != CALIBRATION_MODE:
                return False
            # print(f"|------------------Calibration is done------------------|")
            if self._window_handle != "":
                cv.destroyWindow(self._window_handle)
                self._window_handle = ""

            self._time = 0.0
            # TODO завершение калибровки на основе данных из obj_points и _image_points
            # TODO открыть файл для записи данных калибровки
            # TODO записать данные калибровки
            # TODO закрыть файл и назначить None для self._file_name, self._file_handle
            return False
        return False

    def _record_video(self, message) -> bool:
        mode, message = message

        if mode != ANY_MODE:
            if mode != RECORD_VIDEO_MODE:
                return False

        if message == BEGIN_MODE_MESSAGE:
            print(f'\n|----------------CameraCV record video...---------------|')

            if self._window_handle != "":
                cv.destroyWindow(self._window_handle)
            self._window_handle = "video-recording-window"
            cv.namedWindow(self._window_handle, cv.WINDOW_NORMAL)

            if self._file_name is None:
                self._file_name = f"camera record {datetime.datetime.now().strftime('%H; %M; %S')}.avi"

            if len(self._file_name) == 0:
                self._file_name = f"camera record {datetime.datetime.now().strftime('%H; %M; %S')}.avi"

            try:
                fourcc = cv.VideoWriter_fourcc('m', 'p', '4', 'v')
                self._file_handle = cv.VideoWriter(self._file_name, fourcc, self.fps, (self.width, self.height))
            except:
                self._mode = SHOW_VIDEO_MODE
                self._time = 0.0
                return False
            return True

        if message == RUNNING_MODE_MESSAGE:
            if not self.read_frame():
                print(f"|--------------Record video is interrupted--------------|")
                self._target_mode = EXIT_MODE
                self._file_name = None
                try:
                    self._file_handle.release()
                except:
                    pass
                return False

            progres_bar((self._time / 10.0) % 1.0, 55, '|', '_')

            self._time += self._dtime

            cv.imshow(self._window_handle, self.curr_frame)

            self._file_handle.write(self.curr_frame)

            return True

        if message == STOP_MODE_MESSAGE:
            self._time = 0.0
            self._file_name = None
            if self._window_handle != "":
                cv.destroyWindow(self._window_handle)
                self._window_handle = ""
            try:
                self._file_handle.release()
            except:
                pass

            return False

        return False

    def _pause(self, message) -> bool:
        return  False
        """
         "esc", "q" - Прекратить калибровку
         "r" - захват текущего изображения с камеры и калибровка по нему
         """
        if self._mode != STOP_MODE:
            return False

        cv.imshow(self._window_handle, self.curr_frame)

        key_code = cv.waitKey(2)

        if key_code == 27 or key_code == ord('q'):
            self._mode = EXIT_MODE
            self._time = 0.0
            return False

        if key_code == ord('p'):  # or key_code == XXX (й - на русском ???):
            self._mode = self._prev_mode
            return False

        return True

    def _show_video(self, message) -> bool:

        mode, message = message

        if mode != ANY_MODE:
            if mode != SHOW_VIDEO_MODE:
                return False

        if message == BEGIN_MODE_MESSAGE:
            self._time = -1.0
            print(f"\n|-----------------CameraCV show video...----------------|")
            if self._window_handle != "":
                cv.destroyWindow(self._window_handle)
            self._window_handle = "show-video-window"
            cv.namedWindow(self._window_handle, cv.WINDOW_NORMAL)
            return True

        if message == RUNNING_MODE_MESSAGE:
            if not self.read_frame():
                self._target_mode = EXIT_MODE
                self._time = 0.0
                return False
            cv.imshow(self._window_handle, self.curr_frame)
            return True

        if message == STOP_MODE_MESSAGE:
            if self._window_handle != "":
                cv.destroyWindow(self._window_handle)
                self._window_handle = ""
            return False

        return False

    def _slam(self, message) -> bool:
        if self._mode != SLAM_MODE:
            return False
        return False

    def _build_message(self) -> List[Tuple[int, int]]:
        key_code = cv.waitKey(2)
        if key_code == -1:
            # случай завершения режима
            if self._target_mode != self._mode:
                self._mode = self._target_mode
                return [(self._mode, BEGIN_MODE_MESSAGE)]

            return [(self._mode, RUNNING_MODE_MESSAGE)]

        messages = []
        if key_code == ord('p'):
            # TODO починить
            if self._mode == STOP_MODE:
                self._mode = self._prev_mode
                messages.append((STOP_MODE, STOP_MODE_MESSAGE))
                messages.append((self._mode, RUNNING_MODE_MESSAGE))
            else:
                self._prev_mode = self._mode
                self._mode = STOP_MODE
                messages.append((STOP_MODE, RUNNING_MODE_MESSAGE))
            return messages

        # Завершение работы режима
        if key_code == ord('q'):
            self._target_mode = SHOW_VIDEO_MODE
            messages.append((ANY_MODE, STOP_MODE_MESSAGE))
            return messages

        # Выход из камеры
        if key_code == 27:
            messages.append((ANY_MODE,  STOP_MODE_MESSAGE))
            messages.append((EXIT_MODE, -1))
            return messages

        # Включение режима калибровки
        if key_code == ord('c'):
            # TODO доделать калибровку и проверить работу
            if self._mode != CALIBRATION_MODE:
                self._target_mode = CALIBRATION_MODE
                messages.append((ANY_MODE, STOP_MODE_MESSAGE))
                return messages

        # Включение режима записи
        if key_code == ord('r'):
            if self._mode != RECORD_VIDEO_MODE:
                self._target_mode = RECORD_VIDEO_MODE
                messages.append((ANY_MODE, STOP_MODE_MESSAGE))
                return messages

        # Включение режима видео
        if key_code == ord('v'):
            if self._mode != SHOW_VIDEO_MODE:
                self._target_mode = SHOW_VIDEO_MODE
                messages.append((ANY_MODE, STOP_MODE_MESSAGE))
                return messages

    def update(self):
        with self._timer:
            massages = self._build_message()
            for message in massages:
                self._start(message)
                self._pause(message)
                self._calibrate(message)
                self._show_video(message)
                self._record_video(message)
                self._slam(message)
                if message[0] == EXIT_MODE:
                    self._mode = EXIT_MODE

    def run(self):
        """ This function running in separated thread"""
        while self._mode != EXIT_MODE:
            self.update()
            self._dtime = max(self._timer.last_loop_time, self._timer.timeout)


def camera_cv_test():
    cam = CameraCV()
    cam.run()
    # cam.record_frames()


if __name__ == "__main__":
    camera_cv_test()
