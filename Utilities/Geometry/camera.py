from .common import NUMERICAL_ACCURACY
from .bounding_box import BoundingBox
from .transform_3d import Transform3d
from .matrix4 import Matrix4
from .vector3 import Vector3
from .vector4 import Vector4
from .ray import Ray
import math

PERSPECTIVE_PROJECTION_MODE = 0
ORTHOGRAPHIC_PROJECTION_MODE = 1


class Camera:
    __slots__ = "_projection_mode", "_projection", "_inv_projection", "_transform",\
                "_z_far", "_z_near", "_fov", "_aspect", "_ortho_size", "_raw_projection"

    def __init__(self):
        self._projection_mode = PERSPECTIVE_PROJECTION_MODE
        self._projection:     Matrix4 = Matrix4.identity()
        self._inv_projection: Matrix4 = Matrix4.identity()
        self._transform: Transform3d = Transform3d()
        self._z_far: float = 1000
        self._z_near: float = 0.01
        self._fov: float = 70.0
        self._aspect: float = 10.0
        self._ortho_size: float = 10.0
        self._raw_projection = False
        self._build_projection()

    def __str__(self) -> str:
        return f"{{\n\t\"unique_id\" :{self.unique_id},\n" \
               f"\t\"z_far\"     :{self._z_far},\n" \
               f"\t\"z_near\"    :{self._z_near},\n" \
               f"\t\"fov\"       :{self.fov},\n" \
               f"\t\"aspect\"    :{self.aspect},\n" \
               f"\t\"projection\":\n{self._projection},\n" \
               f"\t\"transform\" :\n{self._transform}\n}}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Camera):
            return False
        if not (self._transform == other._transform):
            return False
        if not (self._projection == other._projection):
            return False
        return True

    def __hash__(self) -> int:
        return hash((self._transform, self._projection, self._inv_projection))

    def _build_projection(self):
        """
        Строит матрицу перспективного искажения.
        :return:
        """
        self._raw_projection = False
        if self.perspective_mode:
            self._projection = \
                Matrix4.build_perspective_projection_matrix(self.fov, self.aspect, self._z_near, self._z_far)
        else:
            size = self._ortho_size * 0.5
            self._projection = \
                Matrix4.build_ortho_projection_matrix(-size * self.aspect, size * self.aspect,
                                                      -size, size, self._z_near, self._z_far)
        self._inv_projection = self._projection.inverted

    def setting_from_json(self, camera):
        if "z_far" in camera:
            try:
                self.z_far = float(camera["z_far"])
            except ValueError as er:
                print(f"CameraGL :: from_json :: incorrect z_far : {camera['z_far']}\n{er.args}")
        if "z_near" in camera:
            try:
                self.z_near = float(camera["z_near"])
            except ValueError as er:
                print(f"CameraGL :: from_json :: incorrect z_near : {camera['z_near']}\n{er.args}")
        if "aspect" in camera:
            try:
                self.aspect = float(camera["aspect"])
            except ValueError as er:
                print(f"CameraGL :: from_json :: incorrect aspect : {camera['aspect']}\n{er.args}")
        if "fov" in camera:
            try:
                self.fov = float(camera["fov"])
            except ValueError as er:
                print(f"CameraGL :: from_json :: incorrect aspect : {camera['fov']}\n{er.args}")
        if "orthographic_size" in camera:
            try:
                self.ortho_size = float(camera["orthographic_size"])
            except ValueError as er:
                print(
                    f"CameraGL :: from_json :: incorrect orthographic_size : {camera['orthographic_size']}\n{er.args}")
        if "is_orthographic" in camera:
            try:
                self.perspective_mode = bool(camera["is_orthographic"])
            except ValueError as er:
                print(f"CameraGL :: from_json :: incorrect is_orthographic : {camera['is_orthographic']}\n{er.args}")
        if "transform" in camera:
            try:
                t = Matrix4(*(float(value) for value in camera["transform"].values()))
                self.transform.transform_matrix = t
            except ValueError as er:
                print(f"CameraGL :: from_json :: incorrect camera transform\n : {camera['transform']}\n{er.args}")

    @property
    def unique_id(self) -> int:
        return id(self)

    @property
    def transform(self) -> Transform3d:
        return self._transform

    @property
    def projection(self) -> Matrix4:
        if self._raw_projection:
            self._build_projection()
        return self._projection

    @property
    def inv_projection(self) -> Matrix4:
        if self._raw_projection:
            self._build_projection()
        return self._inv_projection

    @property
    def z_far(self) -> float:
        return self._z_far

    @z_far.setter
    def z_far(self, far_plane: float) -> None:
        self._z_far = far_plane
        self._raw_projection = True

    @property
    def z_near(self) -> float:
        return self._z_near

    @z_near.setter
    def z_near(self, near_plane: float) -> None:
        self._z_near = near_plane
        self._raw_projection = True

    @property
    def ortho_size(self) -> float:
        return self._ortho_size

    @ortho_size.setter
    def ortho_size(self, value: float) -> None:
        self._ortho_size = value
        self._raw_projection = True

    @property
    def perspective_mode(self) -> bool:
        return self._projection_mode == PERSPECTIVE_PROJECTION_MODE

    @perspective_mode.setter
    def perspective_mode(self, value: bool) -> None:
        self._projection_mode = PERSPECTIVE_PROJECTION_MODE if value else ORTHOGRAPHIC_PROJECTION_MODE
        self._raw_projection = True

    @property
    def fov(self) -> float:
        return self._fov

    @fov.setter
    def fov(self, fov_: float) -> None:
        self._fov = fov_
        self._raw_projection = True

    @property
    def aspect(self) -> float:
        return self._aspect

    @aspect.setter
    def aspect(self, aspect_: float) -> None:
        self._aspect = aspect_
        self._raw_projection = True

    @property
    def look_at_matrix(self) -> Matrix4:
        return self.transform.inv_transform_matrix.transpose()

    def look_at(self, target: Vector3, eye: Vector3, up: Vector3 = Vector3(0, 1, 0)) -> None:
        """
        Строит матрицу вида
        :param target:
        :param eye:
        :param up:
        :return:
        """
        self._transform.look_at(target, eye, up)

    def to_camera_space(self, v: Vector3) -> Vector3:
        """
        Переводит точку в пространстве в собственную систему координат камеры
        :param v:
        :return:
        """
        return self._transform.inv_transform_vect(v, 1)

    def to_clip_space(self, vect: Vector3) -> Vector3:
        """
        Переводит точку в пространстве сперва в собственную систему координат камеры,
        а после в пространство перспективной проекции
        :param vect:
        :return:
        """
        v = self.to_camera_space(vect)
        out: Vector4 = self.projection * Vector4(v.x, v.y, v.z, 1.0)
        if abs(out.w) > NUMERICAL_ACCURACY:  # normalize if w is different from 1
            # (convert from homogeneous to Cartesian coordinates)
            # танцы с бубном
            dist = 1.0 / (self.z_far + self.z_near)
            return Vector3(out.x * dist, out.y * dist, out.z * dist + dist)
        return Vector3(out.x, out.y, out.z)

    def screen_coord_to_camera_ray(self, x: float, y: float) -> Vector3:
        ray_eye = self.inv_projection * Vector4(x, y, -1.0, 1.0)
        ray_eye = self.look_at_matrix.inverted * Vector4(ray_eye.x, ray_eye.y, -1.0, 0.0)
        return Vector3(ray_eye.x, ray_eye.y, ray_eye.z).normalize()

    def emit_ray(self, x: float, y: float) -> Ray:
        # s_size / z_near = tan(a * 0.5)

        # x_size_min = z_near * tan(a * 0.5) / aspect
        # y_size_min = z_near * tan(a * 0.5)

        # x_size_max = z_far * tan(a * 0.5) / aspect
        # y_size_max = z_far * tan(a * 0.5)
        x = max(-1.0, min(x, 1.0))
        y = max(-1.0, min(y, 1.0))
        if self.perspective_mode:
            tan_a_half = math.tan(self.fov * 0.5 * math.pi / 180.0)
            pt1 = Vector3(tan_a_half * x * self.z_near, tan_a_half * y / self.aspect * self.z_near, self.z_near)
            pt2 = Vector3(tan_a_half * x * self.z_far,  tan_a_half * y / self.aspect * self.z_far,  self.z_far)
            # print(f"{pt1} | {pt2}")
            return Ray(self.transform.transform_vect((pt2 - pt1).normalize(), 0.0),
                       self.transform.transform_vect(pt1, 1.0))

        return Ray(self.transform.transform_vect(Vector3(0, 0, 1), 0.0),
                   self.transform.transform_vect(Vector3(x * 0.5 * self.ortho_size,
                                                         y * 0.5 * self.ortho_size / self.aspect, 0), 1.0))

    def cast_object(self, b_box: BoundingBox) -> bool:
        for pt in b_box.points:
            pt = self.to_clip_space(pt)
            if pt.x < -1.0:
                continue
            if pt.x > 1.0:
                continue
            if pt.y < -1.0:
                continue
            if pt.y > 1.0:
                continue
            if pt.z < -1.0:
                continue
            if pt.z > 0.0:
                continue
            return True
        return False
