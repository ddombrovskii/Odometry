from .bounding_box import BoundingBox
from .transform import Transform
from .matrix4 import Matrix4
from .vector3 import Vector3
from .vector4 import Vector4
from .ray import Ray

PERSPECTIVE_PROJECTION_MODE = 0
ORTHOGRAPHIC_PROJECTION_MODE = 1


class Camera:
    __slots__ = "_projection_mode", "_projection", "_inv_projection","_transform",\
                "_z_far", "_z_near", "_fov", "_aspect", "_ortho_size"

    def __init__(self):
        self._projection_mode = PERSPECTIVE_PROJECTION_MODE
        self._projection: Matrix4 = Matrix4.identity()
        self._inv_projection: Matrix4 = Matrix4.identity()
        self._transform: Transform = Transform()
        self._z_far: float = 1000
        self._z_near: float = 0.01
        self._fov: float = 70.0
        self._aspect: float = 10.0
        self._ortho_size: float = 10.0
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
        if self.perspective_mode:
            self._projection = \
                Matrix4.build_perspective_projection_matrix(self.fov, self.aspect, self._z_near, self._z_far)
        else:
            size = self._ortho_size * 0.5
            self._projection = \
                Matrix4.build_ortho_projection_matrix(-size * self.aspect, size * self.aspect,
                                                      -size, size, self._z_near, self._z_far)
        self._inv_projection = self._projection.invert()

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
    def transform(self) -> Transform:
        return self._transform

    @property
    def projection(self) -> Matrix4:
        return self._projection

    @property
    def inv_projection(self) -> Matrix4:
        return self._inv_projection

    @property
    def z_far(self) -> float:
        return self._z_far

    @z_far.setter
    def z_far(self, far_plane: float) -> None:
        self._z_far = far_plane
        self._build_projection()

    @property
    def z_near(self) -> float:
        return self._z_near

    @z_near.setter
    def z_near(self, near_plane: float) -> None:
        self._z_near = near_plane
        self._build_projection()

    @property
    def ortho_size(self) -> float:
        return self._ortho_size

    @ortho_size.setter
    def ortho_size(self, value: float) -> None:
        self._ortho_size = value
        self._build_projection()

    @property
    def perspective_mode(self) -> bool:
        return self._projection_mode == PERSPECTIVE_PROJECTION_MODE

    @perspective_mode.setter
    def perspective_mode(self, value: bool) -> None:
        self._projection_mode = PERSPECTIVE_PROJECTION_MODE if value else ORTHOGRAPHIC_PROJECTION_MODE
        self._build_projection()

    @property
    def fov(self) -> float:
        return self._fov

    @fov.setter
    def fov(self, fov_: float) -> None:
        self._fov = fov_
        self._build_projection()

    @property
    def aspect(self) -> float:
        return self._aspect

    @aspect.setter
    def aspect(self, aspect_: float) -> None:
        self._aspect = aspect_
        self._build_projection()

    @property
    def look_at_matrix(self) -> Matrix4:
        x_axis = self.transform.right
        y_axis = self.transform.up
        z_axis = self.transform.front
        eye    = -self.transform.origin
        return Matrix4(x_axis.x, y_axis.x, z_axis.x, 0.0,
                       x_axis.y, y_axis.y, z_axis.y, 0.0,
                       x_axis.z, y_axis.z, z_axis.z, 0.0,
                       Vector3.dot(x_axis, eye), Vector3.dot(y_axis, eye), Vector3.dot(z_axis, eye), 1.0)

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
        out = Vector3(
            v.x * self._projection.m00 + v.y *
            self._projection.m10 + v.z * self._projection.m20 + self._projection.m30,
            v.x * self._projection.m01 + v.y *
            self._projection.m11 + v.z * self._projection.m21 + self._projection.m31,
            v.x * self._projection.m02 + v.y *
            self._projection.m12 + v.z * self._projection.m22 + self._projection.m32)
        w = v.x * self._projection.m03 + v.y * \
            self._projection.m13 + v.z * self._projection.m23 + self._projection.m33
        if w != 1 and abs(w) > 1e-6:  # normalize if w is different from 1
            # (convert from homogeneous to Cartesian coordinates)
            return out / w

        return out

    def screen_coord_to_camera_ray(self, x: float, y: float) -> Vector3:
        ray_eye = self.projection.invert() * Vector4(x, y, -1.0, 1.0)
        ray_eye = self.look_at_matrix.invert() * Vector4(ray_eye.x, ray_eye.y, -1.0, 0.0)
        return Vector3(ray_eye.x, ray_eye.y, ray_eye.z).normalized()

    # def emit_ray(self, x: float, y: float):

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
            if pt.z > 1.0:
                continue
            return True
        return False
