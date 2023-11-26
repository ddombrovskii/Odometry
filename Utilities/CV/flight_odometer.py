from Utilities.Geometry import Camera, Matrix3, Vector3, Plane, Vector2, Matrix4, Quaternion, Ray
from .image_matcher import ImageMatcher
from Utilities.Common import Timer
from typing import Tuple, Union
import numpy as np


class FlightOdometer:
    @staticmethod
    def _camera_frustum_ground_border(camera: Camera, ground_level: float = 0.0) -> Tuple[Vector2, ...]:
        p = Plane(origin=Vector3(0, -ground_level, 0), normal=Vector3(0, 0, 1))
        # {1.0, 1.0} | {1.0, -1.0} | {-1.0, -1.0} | {-1.0, 1.0}
        points = (p.intersect_by_ray(camera.emit_ray( 1.0,  1.0)).end_point,
                  p.intersect_by_ray(camera.emit_ray( 1.0, -1.0)).end_point,
                  p.intersect_by_ray(camera.emit_ray(-1.0, -1.0)).end_point,
                  p.intersect_by_ray(camera.emit_ray(-1.0,  1.0)).end_point)
        # [print(p) for p in points]
        # print('=======================================')
        return tuple(Vector2(p.x, p.y) for p in points)

    def __init__(self):
        # SIFT based image features matcher
        self._image_matcher: ImageMatcher = ImageMatcher()
        # Geometric camera
        self._camera: Camera = Camera()
        self._camera.aspect = 1.0
        self._camera.fov = 45
        # Projection matrix from image coordinates to earth space coordinates
        self._curr_proj_mat: Matrix3 = Matrix3.identity()
        self._prev_proj_mat: Matrix3 = Matrix3.identity()
        # Intersection of camera frustum edge rays with ground level
        # current camera frame
        self._curr_frame: Union[np.ndarray, None] = None
        # previous camera frame
        self._prev_frame: Union[np.ndarray, None] = None
        # ground level transform
        self._curr_gt_transform: Matrix3 = Matrix3.identity()
        self._prev_gt_transform: Matrix3 = Matrix3.identity()
        # real space transform
        self._curr_transform: Matrix4 = Matrix4.identity()
        self._prev_transform: Matrix4 = Matrix4.identity()
        # other physical params of flight
        self._curr_velocity: Vector3 = Vector3(0, 0, 0)
        self._prev_velocity: Vector3 = Vector3(0, 0, 0)
        self._curr_acceleration: Vector3 = Vector3(0, 0, 0)
        self._prev_acceleration: Vector3 = Vector3(0, 0, 0)
        # timer to measure time =)
        self._timer: Timer = Timer()

    def _update_camera_transform_transforms(self, rotation: Quaternion, altitude, image_w: int, image_h: int) -> None:
        # Geometric camera position an orientation updating
        # В соответствии с ROS:
        # 1. Движение вверх  - oZ
        # 2. Движение вперёд - oX
        # 3. Движение вправо - oY
        self._camera.transform.origin   = Vector3(0.0, 0.0, altitude)
        self._camera.transform.rotation = rotation  # Quaternion.from_euler_angles(90, 0, 0, False) * rotation
        # Ground level camera frustum border updating
        _border = FlightOdometer._camera_frustum_ground_border(self._camera)
        _image_border = (Vector2(image_w, image_h), Vector2(image_w, 0), Vector2(0, 0), Vector2(0, image_h))
        if self._prev_frame is None:
            self._curr_proj_mat = Matrix3.perspective_transform_from_eight_points(*_border, *_image_border)
            self._prev_proj_mat = Matrix3.perspective_transform_from_eight_points(*_border, *_image_border)
        else:
            self._prev_proj_mat  = self._curr_proj_mat
            self._curr_proj_mat  = Matrix3.perspective_transform_from_eight_points(*_border, *_image_border)

    def _build_transforms(self) -> None:
        self._prev_gt_transform  = self._curr_gt_transform
        self._curr_gt_transform *= self._image_matcher.homography_matrix
        # TODO refactor...
        plane = Plane(origin=Vector3(0, 0, 0), normal=Vector3(0, 0, 1))
        ray   = Ray(self._camera.transform.front, self._camera.transform.origin)
        plane.intersect_by_ray(ray)
        position = Vector3(self._curr_gt_transform.m02, self._curr_gt_transform.m12, 0.0) - ray.length * ray.direction
        # TODO end refactor
        self._prev_transform = self._curr_transform
        # 1. Движение вверх  - oZ
        # 2. Движение вперёд - oX
        # 3. Движение вправо - oY
        self._curr_transform = Matrix4.build_transform(self._camera.transform.up,
                                                       self._camera.transform.front,
                                                       self._camera.transform.right,
                                                       position)
        # Имеется ввиду суммарное время между текущим и предыдущим расчётом + само время на расчёт
        delta_time = 1.0 / (self._timer.delta_inner_time + self._timer.delta_outer_time)
        self._prev_velocity = self.velocity
        self._curr_velocity = (self.position - self.prev_position) * delta_time
        self._prev_acceleration = self.acceleration
        self._curr_acceleration = (self.velocity - self.prev_velocity ) * delta_time

    def _compute(self, image: np.ndarray, rotation: Quaternion, altitude: float) -> None:
        image_w, image_h = image.shape[1], image.shape[0]
        self._update_camera_transform_transforms(rotation, altitude, image_w, image_h)
        self._prev_frame = self._curr_frame
        self._curr_frame = image
        if self._prev_frame is None:
            return
        if self._image_matcher.match_images(self._prev_frame,
                                            self._curr_frame,
                                            self._prev_proj_mat,
                                            self._curr_proj_mat):
            self._build_transforms()
        else:
            # extrapolate values
            ...

    def compute(self, image: np.ndarray, rotation: Quaternion, altitude: float) -> None:
        """
        Основной метод, который вызывается для расчёта одометрии
        :param image: изображение, полученное с камеры (np.ndarray)
         должно быть полутоновым (cv2.imread(image_1_src, cv2.IMREAD_GRAYSCALE))
        :param rotation: кватернион системы координат акселерометра
        :param altitude: текущая высота полёта
        """
        with self._timer:
            self._compute(image, rotation, altitude)

    @property
    def velocity(self) -> Vector3:
        """
        Текущая скорость движения. Для определения необходимо минимум два вызова compute
        """
        return self._curr_velocity

    @property
    def acceleration(self) -> Vector3:
        """
        Текущее ускорение движения. Для определения необходимо минимум три вызова compute
        """
        return self._curr_acceleration

    @property
    def position(self) -> Vector3:
        """
        Текущее положение. Для определения необходимо минимум два вызова compute
        """
        return self._curr_transform.origin

    @property
    def prev_velocity(self) -> Vector3:
        """
        Предыдущая скорость движения. Для определения необходимо минимум два вызова compute
        """
        return self._prev_velocity

    @property
    def prev_acceleration(self) -> Vector3:
        """
        Предыдущее ускорение движения. Для определения необходимо минимум три вызова compute
        """
        return self._prev_acceleration

    @property
    def prev_position(self) -> Vector3:
        """
        Предыдущее положение. Для определения необходимо минимум два вызова compute
        """
        return self._prev_transform.origin

    @property
    def transform(self) -> Matrix4:
        """
        Текущая матрица трансформации для камеры в мировом пространстве.
        """
        return self._curr_transform

    @property
    def prev_transform(self) -> Matrix4:
        """
        Предыдущая матрица трансформации для камеры в мировом пространстве.
        """
        return self._prev_transform

    @property
    def view_frustum_ground_transform(self) -> Matrix3:
        """
        Текущая матрица трансформации для камеры в пространстве на поверхности земли.
        """
        return self._curr_gt_transform

    @property
    def prev_view_frustum_ground_transform(self) -> Matrix3:
        """
        Предыдущая матрица трансформации для камеры в пространстве на поверхности земли.
        """
        return self._prev_gt_transform
