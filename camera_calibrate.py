import cv2 as cv
import numpy as np


class CameraCalibrator:
    def __init__(self):
        self._flag: int = 0
        self._must_init_undistort: bool = True
        self._distorsion: np.ndarray
        self._camera_mat: np.ndarray

    @property
    def distorsion(self) -> np.ndarray:
        return self._distorsion

    @property
    def camera_matrix(self) -> np.ndarray:
        return self._camera_mat

    def triangulate(self):
        pass
    def calibrate(self, image: np.ndarray):
        pass