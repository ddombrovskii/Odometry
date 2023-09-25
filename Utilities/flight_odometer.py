from typing import Tuple, Union

import cv2

from .Geometry import Camera, Matrix3, Vector3, Plane, PerspectiveTransform2d, Vector2
from .image_matcher import ImageMatcher
import numpy as np


class FlightOdometer:
    @staticmethod
    def _camera_frustum_ground_border(camera: Camera, ground_level: float = 0.0) -> Tuple[Vector2, ...]:
        p = Plane(origin=Vector3(0, ground_level, 0))  # normal=Vector3(0, -1, 0))
        # {1.0, 1.0} | {1.0, -1.0} | {-1.0, -1.0} | {-1.0, 1.0}
        points = (p.intersect_by_ray(camera.emit_ray(1.0, 1.0)).end_point,
                  p.intersect_by_ray(camera.emit_ray(1.0, -1.0)).end_point,
                  p.intersect_by_ray(camera.emit_ray(-1.0, -1.0)).end_point,
                  p.intersect_by_ray(camera.emit_ray(-1.0, 1.0)).end_point)
        return tuple(Vector2(p.x, p.z) for p in points)

    def __init__(self):
        self._image_matcher: ImageMatcher = ImageMatcher()
        self._camera: Camera = Camera()
        self._camera.aspect = 1.0
        self._camera.fov = 30
        self._proj_transform_curr: PerspectiveTransform2d = PerspectiveTransform2d()
        self._proj_transform_prev: PerspectiveTransform2d = PerspectiveTransform2d()
        self._proj_transform_trans: PerspectiveTransform2d = PerspectiveTransform2d()
        self._border_curr = ()
        self._border_prev = ()
        self._curr_frame: Union[np.ndarray, None] = None
        self._prev_frame: Union[np.ndarray, None] = None

    def _update_transforms(self, ax: float, ay: float, az: float, altitude):
        self._camera.transform.origin = Vector3(0, altitude, 0)
        self._camera.transform.angles = Vector3(90 + ax, ay, az)
        _border = FlightOdometer._camera_frustum_ground_border(self._camera)
        if len(self._border_curr) == 0:
            self._border_curr = _border
            self._border_prev = _border
            self._proj_transform_curr = PerspectiveTransform2d.from_four_points(*_border)
            self._proj_transform_prev = PerspectiveTransform2d.from_four_points(*_border)
        else:
            self._border_prev = self._border_curr
            self._border_curr = _border
            self._proj_transform_prev  = self._proj_transform_curr
            self._proj_transform_curr  = PerspectiveTransform2d.from_four_points(*_border)
            self._proj_transform_trans = PerspectiveTransform2d.from_eight_points(*self._border_prev, *_border)

    def compute(self, image: np.ndarray, ax: float, ay: float, az: float, altitude):
        self._update_transforms(ax, ay, az, altitude)
        self._prev_frame = self._curr_frame
        # Проверить центровку относительно центра изображения
        self._curr_frame = cv2.warpPerspective(image, self._proj_transform_curr.transform_matrix.to_np_array(),
                                               (image.shape[0], image.shape[1]))
        if self._prev_frame is None:
            return
        self._image_matcher.match_images(self._prev_frame, self._curr_frame)


