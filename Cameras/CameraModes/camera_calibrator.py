from Cameras.utilities import load_camera_calib_info, CameraCalibrationInfo
from Cameras.CameraModes.camera_mode import CameraMode
from Utilities.Device import device_progres_bar
from Cameras import CameraCalibrationArgs
import datetime
import cv2
import os


class CameraCalibrator(CameraMode):

    @staticmethod
    def calib_results_file_path() -> str:
        return f"calibration_results {datetime.datetime.now().strftime('%H; %M; %S')}.json"

    def __init__(self, camera_cv):
        super().__init__(camera_cv)
        self._file_handle  = None
        self._file_name    = CameraCalibrator.calib_results_file_path()
        self._calib_params = CameraCalibrationArgs()

    @property
    def calibration_params(self) -> CameraCalibrationArgs:
        return self._calib_params

    @calibration_params.setter
    def calibration_params(self, params: CameraCalibrationArgs) -> None:
        self._calib_params = CameraCalibrationArgs() if params is None else params

    @property
    def save_calib_results_file_path(self) -> str:
        return self._file_name

    @save_calib_results_file_path.setter
    def save_calib_results_file_path(self, value: str) -> None:
        if value is None:
            self._file_name = CameraCalibrator.calib_results_file_path()
            return

        if len(value)  == 0:
            self._file_name = CameraCalibrator.calib_results_file_path()
            return

        self._file_name = value

    def search_for_calib_info(self):
        self._try_to_load_calib_info()

    def _try_to_load_calib_info(self) -> bool:
        file_dir = os.path.dirname(self.save_calib_results_file_path)
        if file_dir == "":
            file_dir = '.'
        for file in os.listdir(file_dir):
            if file.startswith("calibration_results"):
                self.camera.camera_calibration_info = load_camera_calib_info(file)
                self.save_calib_results_file_path = file
                if self.camera.camera_calibration_info is None:
                    return False
                self.camera.send_log_message(f"\n|------------------Loaded from file...------------------|\n")
                return True
        return False

    def _on_start(self, message: int) -> bool:
        if not super()._on_start(message):
            return False

        self.camera.send_log_message(f"\n|-----------------CameraCV calibrating...---------------|\n"
                                     f"|-------------Please stand by and hold still...---------|")

        self.camera.window_handle = "CameraCV calibration mode..."

        if self._calib_params.recalibrate:
            return True

        if self._try_to_load_calib_info():
            return False
        return True

    def _on_run(self, message: int) -> bool:
        # чтение текущего кадра
        self.camera.send_log_message(device_progres_bar((self.active_time / 2.0) % 1.0))
        ###############################################
        # Добавляет новый калибровочный кадр по клику #
        ###############################################
        if self.active_time % 1.0 <= 0.9:
            return True
        # перевод текущего кадра в серый цвет
        frame_gray = cv2.cvtColor(self.camera.curr_frame, cv2.COLOR_BGR2GRAY)
        # поиск углов шахматной доски
        ret, corners = cv2.findChessboardCorners(frame_gray, self.calibration_params.ches_board_size, None)
        if ret:
            self.calibration_params.obj_points.append(self.calibration_params.obj_points_array)
            self.calibration_params.image_points.append(corners)
            self.camera.send_log_message("\radded new calibration image")
            corners_2 = cv2.cornerSubPix(frame_gray, corners, (11, 11), (-1, -1), self.calibration_params.criteria)
            curr_frame = cv2.drawChessboardCorners(self.camera.curr_frame,
                                                   self.calibration_params.ches_board_size, corners_2, ret)
            cv2.imshow(self._window_handle, curr_frame)
        return True

    def _on_end(self, message: int) -> bool:
        if len(self.calibration_params.obj_points) > 0 and len(self.calibration_params.image_points) > 0:
            status, camera_matrix, distortion, r_vectors, t_vectors = \
                cv2.calibrateCamera(self.calibration_params.obj_points, self.calibration_params.image_points,
                                    (self.camera.width, self.camera.height), None, None)
            if status:
                self.camera_calibration_info = CameraCalibrationInfo(camera_matrix, distortion,
                                                                     t_vectors, r_vectors)
                with open(self.save_calib_results_file_path, 'wt') as calib_info:
                    print(self.camera_calibration_info, file=calib_info)
                self.save_calib_results_file_path, self._file_handle = "", None
        return False
