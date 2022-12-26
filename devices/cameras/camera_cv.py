import datetime as datetime
from os import mkdir
import numpy as np
import cv2 as cv
import time


class CameraCV:  # (Camera):

    def __init__(self):
        self.__camera_stream: cv.VideoCapture
        self.__buffer_depth = 8
        self.__buffer: [np.ndarray] = []
        try:
            self.__camera_stream = cv.VideoCapture(0, cv.CAP_DSHOW)
            self.__camera_stream.set(cv.CAP_PROP_FPS, 60)
        except RuntimeError("CV Camera instantiate error") as ex:
            print(ex.args)

        if not self.__camera_stream.isOpened():
            raise RuntimeError("device init function call error")
        # super().__init__()

    @property
    def next_frame(self) -> np.ndarray:
        if not self.is_open:
            raise RuntimeError("Can't receive frame (stream end?). Exiting ...")

        has_frame, cam_frame = self.__camera_stream.read()

        if not has_frame:
            raise RuntimeError("Can't receive frame (stream end?). Exiting ...")
        self.__append_frames_buffer(cam_frame)
        return cam_frame

    def __del__(self):
        try:
            self.__camera_stream.release()
        except RuntimeError() as ex:
            print(f"dispose error {ex.args}")
            return False
        return True

    def __str__(self):
        res: str = "CV Camera: \n" \
                   f"CV_CAP_PROP_FRAME_WIDTH  : {self.__camera_stream.get(cv.CAP_PROP_FRAME_WIDTH)}\n" \
                   f"CV_CAP_PROP_FRAME_HEIGHT : {self.__camera_stream.get(cv.CAP_PROP_FRAME_HEIGHT)}\n" \
                   f"CAP_PROP_FPS             : {self.__camera_stream.get(cv.CAP_PROP_FPS)}\n" \
                   f"CAP_PROP_EXPOSUREPROGRAM : {self.__camera_stream.get(cv.CAP_PROP_EXPOSUREPROGRAM)}\n" \
                   f"CAP_PROP_POS_MSEC        : {self.__camera_stream.get(cv.CAP_PROP_POS_MSEC)}\n" \
                   f"CAP_PROP_FRAME_COUNT     : {self.__camera_stream.get(cv.CAP_PROP_FRAME_COUNT)}\n" \
                   f"CAP_PROP_BRIGHTNESS      : {self.__camera_stream.get(cv.CAP_PROP_BRIGHTNESS)}\n" \
                   f"CAP_PROP_CONTRAST        : {self.__camera_stream.get(cv.CAP_PROP_CONTRAST)}\n" \
                   f"CAP_PROP_SATURATION      : {self.__camera_stream.get(cv.CAP_PROP_SATURATION)}\n" \
                   f"CAP_PROP_HUE             : {self.__camera_stream.get(cv.CAP_PROP_HUE)}\n" \
                   f"CAP_PROP_GAIN            : {self.__camera_stream.get(cv.CAP_PROP_GAIN)}\n" \
                   f"CAP_PROP_CONVERT_RGB     : {self.__camera_stream.get(cv.CAP_PROP_CONVERT_RGB)}\n"
        return res

    __repr__ = __str__

    def __append_frames_buffer(self, frame: np.ndarray):
        if len(self.__buffer) == self.__buffer_depth:
            del self.__buffer[0]
        self.__buffer.append(frame)

    @property
    def is_buffer_empty(self) -> bool:
        return len(self.__buffer) == 0

    @property
    def is_open(self) -> bool:
        return self.__camera_stream.isOpened()

    @property
    def pixel_format(self) -> str:
        return self.__camera_stream.get(cv.CAP_PROP_FORMAT)

    @pixel_format.setter
    def pixel_format(self, pixel_format: str) -> None:
        raise RuntimeError("pixel format setter is unsupported for this camera")

    @property
    def camera_width(self) -> int:
        return int(self.__camera_stream.get(cv.CAP_PROP_FRAME_WIDTH))

    @camera_width.setter
    def camera_width(self, w: int) -> None:
        if not self.__camera_stream.set(cv.CAP_PROP_FRAME_WIDTH, w):
            print(f"incorrect devices width {w}")
            return
        self.aspect = self.camera_width / float(self.camera_height)

    @property
    def camera_height(self) -> int:
        return int(self.__camera_stream.get(cv.CAP_PROP_FRAME_HEIGHT))

    @camera_height.setter
    def camera_height(self, h: int) -> None:
        if not self.__camera_stream.set(cv.CAP_PROP_FRAME_HEIGHT, h):
            print(f"incorrect devices height {h}")
            return
        self.aspect = self.camera_width / float(self.camera_height)

    @property
    def offset_x(self) -> int:
        return int(self.__camera_stream.get(cv.CAP_PROP_XI_OFFSET_X))

    @offset_x.setter
    def offset_x(self, value) -> None:
        if not self.__camera_stream.set(cv.CAP_PROP_XI_OFFSET_X,
                                        min(max(-self.camera_width, value), self.camera_width)):
            print(f"incorrect devices x - offset {value}")

    @property
    def offset_y(self) -> int:
        return int(self.__camera_stream.get(cv.CAP_PROP_XI_OFFSET_Y))

    @offset_y.setter
    def offset_y(self, value) -> None:
        if not self.__camera_stream.set(cv.CAP_PROP_XI_OFFSET_Y,
                                        min(max(-self.camera_height, value), self.camera_height)):
            print(f"incorrect devices y - offset {value}")

    @property
    def exposure_mode(self) -> str:
        return str(self.__camera_stream.get(cv.CAP_PROP_EXPOSUREPROGRAM))

    @exposure_mode.setter
    def exposure_mode(self, value: str):
        raise RuntimeError("exposure mode setter is unsupported for this camera")

    @property
    def exposure(self) -> float:
        return float(self.__camera_stream.get(cv.CAP_PROP_EXPOSURE))

    @exposure.setter
    def exposure(self, value) -> None:
        if not self.__camera_stream.set(cv.CAP_PROP_EXPOSURE, min(max(-12, value), 12)):
            print(f"incorrect devices y - offset {value}")

    @property
    def frame_time(self) -> float:
        return 1.0 / float(self.__camera_stream.get(cv.CAP_PROP_FPS))

    @property
    def camera_fps(self) -> int:
        return self.__camera_stream.get(cv.CAP_PROP_FPS)

    @camera_fps.setter
    def camera_fps(self, fps: int) -> None:
        if not self.__camera_stream.set(cv.CAP_PROP_FPS, min(max(1, fps), 120)):
            print(f"incorrect devices fps {fps}")

    @property
    def last_frame(self) -> np.ndarray:
        if len(self.__buffer) == 0:
            return np.zeros((self.camera_width, self.camera_height), dtype=np.uint8)
        return self.__buffer[len(self.__buffer) - 1]

    def __keyboard_input(self) -> bool:
        key = cv.waitKey(2)
        if key == 27:
            # cv.destroyWindow("video")
            return False

        if key == ord('s') or key == 251:
            try:
                now = datetime.datetime.now()
                cv.imwrite(f'frame_at_time_{now.hour}_{now.minute}_{now.second}_{now.microsecond}.png', self.last_frame)
                return True
            except RuntimeError as ex:
                print(f"{ex.args}")
                return True
        if key == ord('e') or key == 243:
            return True
        return True

    def show_video(self):
        cv.namedWindow("video", cv.WINDOW_NORMAL)
        dt: float
        t0: float
        # th.setDaemon(True)
        while True:
            if not self.is_open:
                cv.destroyWindow("video")
                break
            if not self.__keyboard_input():
                cv.destroyWindow("video")
                break
            try:
                t0 = time.time()
                cv.imshow("video", self.next_frame)
                dt = time.time() - t0
                if dt > self.frame_time:
                    continue
                time.sleep(self.frame_time - dt)
            except RuntimeError as ex:
                print(f"{ex.args}")

    def record_frames(self, folder: str = None):
        while True:
            if folder is None:
                folder = f"camera record {datetime.datetime.now().strftime('%H; %M; %S')}"
                break
            if len(folder) == 0:
                folder = f"camera record {datetime.datetime.now().strftime('%H; %M; %S')}"
                break
            break
        try:
            mkdir(folder)
        except FileExistsError:
            print(f"directory {folder} exists already")

        cv.namedWindow("video", cv.WINDOW_NORMAL)
        dt: float
        t0: float
        while True:
            if not self.is_open:
                cv.destroyWindow("video")
                break
            # esc to exit
            if not self.__keyboard_input():
                cv.destroyWindow("video")
                break
            try:
                t0 = time.time()
                cv.imshow("video", self.next_frame)
                now = datetime.datetime.now()
                cv.imwrite(folder + f'/frame_at_time_{now.hour}_{now.minute}_{now.second}_{now.microsecond}.png',
                           self.last_frame)
                dt = time.time() - t0
                if dt > self.frame_time:
                    continue
                time.sleep(self.frame_time - dt)
            except RuntimeError as ex:
                print(f"{ex.args}")


def camera_cv_test():
    cam = CameraCV()
    cam.show_video()
    # cam.record_frames()


if __name__ == "__main__":
    camera_cv_test()
