from Cameras.CameraModes.camera_mode import CameraMode
from Cameras import SLAM
import datetime


class CameraSlam(CameraMode):
    @staticmethod
    def slam_record_path() -> str:
        return f"slam record {datetime.datetime.now().strftime('%H; %M; %S')}.json"

    def __init__(self, camera_cv):
        super().__init__(camera_cv)
        self._slam_detector = None
        self._file_handle = None
        self._file_name = CameraSlam.slam_record_path()

    @property
    def slam_record_file_path(self) -> str:
        return self._file_name

    @slam_record_file_path.setter
    def slam_record_file_path(self, value: str) -> None:
        if value is None:
            self._file_name = CameraSlam.slam_record_path()
            return

        if len(value)  == 0:
            self._file_name = CameraSlam.slam_record_path()
            return
        self._file_name = value

    def _on_start(self, message: int) -> bool:
        if not super()._on_start(message):
            return False
        if self.camera.camera_calibration_info is None:
            self.camera.send_log_message("SLAM error: camera is not calibrated")
            return False
        self._slam_detector = SLAM(self.camera.camera_calibration_info.camera_matrix)
        try:
            self._file_handle = open(self._file_name, "wt")
        except IOError as err:
            self.camera.send_log_message(f"{err.args}")
            return False
        self._file_handle.write("{\n")
        self._file_handle.write(f"\t\"optical_odometry\": \"{datetime.datetime.now().strftime('%H; %M; %S')}\",\n")
        self._file_handle.write(f"\t\"way_points_transforms\": [\n")
        return True

    def _on_run(self, message: int) -> bool:
        self._slam_detector(self.camera.curr_frame)
        tr = self._slam_detector.transform
        self._file_handle.write("\t{\n")
        self._file_handle.write(
            f"\t\t\"m00\": {tr[0][0]:20}, \"m01\": {tr[0][1]:20}, \"m02\": {tr[0][2]:20}, \"m03\": {tr[0][3]:20},\n")
        self._file_handle.write(
            f"\t\t\"m10\": {tr[1][0]:20}, \"m11\": {tr[1][1]:20}, \"m12\": {tr[1][2]:20}, \"m13\": {tr[1][3]:20},\n")
        self._file_handle.write(
            f"\t\t\"m20\": {tr[2][0]:20}, \"m21\": {tr[2][1]:20}, \"m22\": {tr[2][2]:20}, \"m23\": {tr[2][3]:20}\n")
        self._file_handle.write("\t},\n")
        return True

    def _on_end(self, message: int) -> bool:
        self._file_handle.seek(self._file_handle.tell() - 3, 0)
        self._file_handle.write("\n\t]\n}")
        try:
            self._file_handle.close()
        except RuntimeError as err:
            print(f"{err.args}")
        return False
