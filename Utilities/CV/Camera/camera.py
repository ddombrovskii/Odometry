from .CameraActions import CameraFramesRecorder
from .CameraActions import CameraVideoRecorder
from .CameraActions import CameraFrameGrabber
from .CameraActions import CameraCVController
from .CameraActions import CameraFrameSaver
from .camera_handle import CameraHandle
from Utilities.ActionsLoop import ActionsLoop


_DEFAULT_DIR_NAME = "camera_records\\"
_DEFAULT_VIDEO_RECORDS_DIR_NAME = "camera_records\\recorded_videos\\"
_DEFAULT_FRAMES_RECORDS_DIR_NAME = "camera_records\\recorded_frames\\"
_DEFAULT_FRAMES_DIR_NAME = "camera_records\\saved_frames\\"


# TODO specify calib params path / frames saving directory path / frames recording directory path / video recording path
class Camera(ActionsLoop):
    """
    q - quite
    s - save frames with time interval (default 1 second)
    r - record video (default 30 fps)
    f - save single frame
    esq - stop saving frames or recording video
    """
    def __init__(self, port: int = 0):
        super().__init__()
        self._camera_cv: CameraHandle = CameraHandle(port)
        self.update_time = self._camera_cv.frame_time
        self._frames_grabber  = CameraFrameGrabber(self)
        self._frame_saver     = CameraFrameSaver(self)
        self._frames_recorder = CameraFramesRecorder(self)
        self._video_recorder  = CameraVideoRecorder(self)
        self._cv_controller   = CameraCVController(self)
        self.register_action(self._frames_grabber, True)
        self.register_action(self._cv_controller  )
        self.register_action(self._frame_saver    )
        self.register_action(self._frames_recorder)
        self.register_action(self._video_recorder )

    @property
    def camera_cv(self) -> CameraHandle:
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
        return self.camera_cv.is_open

    def camera_read_only(self):
        self.stop_all_except(self._frames_grabber)

    def record_video(self, video_path: str = _DEFAULT_VIDEO_RECORDS_DIR_NAME, ext: str = 'mp4') -> bool:
        if self.action_active(self._video_recorder):
            return False
        self._video_recorder.video_ext = ext
        self._video_recorder.video_record_directory = video_path
        return self.start_action(self._video_recorder)

    def record_frames(self, video_path: str = _DEFAULT_FRAMES_RECORDS_DIR_NAME, ext: str = 'png'):
        if self.action_active(self._frames_recorder):
            return False
        self._frames_recorder.frames_ext = ext
        self._frames_recorder.frames_directory = video_path
        return self.start_action(self._frames_recorder)

    def save_frame(self, video_path: str = _DEFAULT_FRAMES_DIR_NAME, ext: str = 'png'):
        if self.action_active(self._frame_saver):
            return False
        self._frame_saver.frames_ext = ext
        self._frame_saver.frames_directory = video_path
        return self.start_action(self._frame_saver)

    def run_cv(self):
        self.start_action(self._cv_controller)
        self.run()
