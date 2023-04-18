from Utilities.Geometry import Transform, Matrix4, Vector3, BoundingBox


class CameraGL:
    def __init__(self):
        self._transform: Transform = Transform()
        self._projection: Matrix4 = Matrix4.identity()
        self._z_far: float  = 1000
        self._z_near: float = 0.01
        self._fov: float    = 70.0
        self._aspect: float = 10.0
        self.__build_projection()

    def __str__(self) -> str:
        return f"{{\n\t\"unique_id\" :{self.unique_id},\n" \
                   f"\t\"z_far\"     :{self._z_far},\n" \
                   f"\t\"z_near\"    :{self._z_near},\n" \
                   f"\t\"fov\"       :{self.fov},\n" \
                   f"\t\"aspect\"    :{self.aspect},\n" \
                   f"\t\"projection\":\n{self._projection},\n" \
                   f"\t\"transform\" :\n{self._transform}\n}}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, CameraGL):
            return False
        if not (self._transform == other._transform):
            return False
        if not (self._projection == other._projection):
            return False
        return True

    def __hash__(self) -> int:
        return hash((self._transform, self._projection))

    def __build_projection(self):
        """
        Строит матрицу перспективного искажения
        :return:
        """
        self._projection = Matrix4.build_projection_matrix(self.fov, self.aspect, self._z_near, self._z_far)

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
    def z_far(self) -> float:
        return self._z_far

    @z_far.setter
    def z_far(self, far_plane: float) -> None:
        self._z_far = far_plane
        self.__build_projection()

    @property
    def z_near(self) -> float:
        return self._z_near

    @z_near.setter
    def z_near(self, near_plane: float) -> None:
        self._z_near = near_plane
        self.__build_projection()

    @property
    def fov(self) -> float:
        return self._fov

    @fov.setter
    def fov(self, fov_: float) -> None:
        self._fov = fov_
        self.__build_projection()

    @property
    def aspect(self) -> float:
        return self._aspect

    @aspect.setter
    def aspect(self, aspect_: float) -> None:
        self._aspect = aspect_
        self.__build_projection()

    @property
    def look_at_matrix(self) -> Matrix4:
        xaxis = self.transform.right
        yaxis = self.transform.up
        zaxis = self.transform.front
        eye   = -self.transform.origin
        return Matrix4(xaxis.x, yaxis.x, zaxis.x, 0.0,
                       xaxis.y, yaxis.y, zaxis.y, 0.0,
                       xaxis.z, yaxis.z, zaxis.z, 0.0,
                       Vector3.dot(xaxis, eye), Vector3.dot(yaxis, eye), Vector3.dot(zaxis, eye), 1.0)

    # def orbit(self, angles: Vector3, target: Vector3 = None):

    def look_at(self, target: Vector3, eye: Vector3, up: Vector3 = Vector3(0, 1, 0)) -> None:
        """
        Cтроит матрицу вида
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
        w = v.x * self._projection.m03 + v.y *\
            self._projection.m13 + v.z * self._projection.m23 + self._projection.m33
        if w != 1 and abs(w) > 1e-6:  # normalize if w is different from 1 (convert from homogeneous to Cartesian coordinates)
            return out / w

        return out

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
