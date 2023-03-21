from .vector3 import Vector3
from .matrix4 import Matrix4
import math


def deg_to_rad(deg: float) -> float:
    """
    :param deg: угол в градусах
    :return: угол в радианах
    """
    return deg / 180.0 * math.pi


class Transform:

    __slots__ = "__transform_m"

    def __init__(self):
        self.__transform_m = Matrix4(1.0, 0.0, 0.0, 0.0,
                                     0.0, 1.0, 0.0, 0.0,
                                     0.0, 0.0, 1.0, 0.0,
                                     0.0, 0.0, 0.0, 1.0)

    def __str__(self) -> str:
        return f"{{\n\t\"unique_id\"   :{self.unique_id},\n" \
                   f"\t\"origin\"      :{self.origin},\n" \
                   f"\t\"scale\"       :{self.scale},\n" \
                   f"\t\"rotate\"      :{self.angles / math.pi * 180},\n" \
                   f"\t\"transform_m\" :\n{self.__transform_m}\n}}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Transform):
            return False
        if not(self.__transform_m == other.__transform_m):
            return False
        return True

    def __hash__(self) -> int:
        return hash(self.__transform_m)

    def __build_basis(self, ex: Vector3, ey: Vector3, ez: Vector3) -> None:
        self.__transform_m = Matrix4.build_transform(ex, ey, ez, self.origin)

    @property
    def unique_id(self) -> int:
        return id(self)

    @property
    def transform_matrix(self) -> Matrix4:
        return self.__transform_m

    @transform_matrix.setter
    def transform_matrix(self, t: Matrix4) -> None:
        self.__transform_m = Matrix4.build_transform(t.right, t.up, t.front, t.origin)

    @property
    def front(self) -> Vector3:
        return Vector3(self.__transform_m.m02,
                       self.__transform_m.m12,
                       self.__transform_m.m22).normalize()

    @front.setter
    def front(self, front_: Vector3) -> None:
        length_ = front_.magnitude()
        if length_ < 1e-9:
            raise ArithmeticError("Error transform front set")
        front_dir_ = front_ / length_
        right_ = Vector3.cross(front_dir_, Vector3(0, 1, 0)).normalized()
        up_ = Vector3.cross(right_, front_dir_).normalized()
        self.__build_basis(right_ * self.sx, up_ * self.sy, front_)

    @property
    def up(self) -> Vector3:
        return Vector3(self.__transform_m.m01,
                       self.__transform_m.m11,
                       self.__transform_m.m21).normalize()

    @up.setter
    def up(self, up_: Vector3) -> None:
        length_ = up_.magnitude()
        if length_ < 1e-9:
            raise ArithmeticError("Error transform up set")
        up_dir_ = up_ / length_
        front_ = Vector3.cross(up_dir_, Vector3(1, 0, 0)).normalized()
        right_ = Vector3.cross(up_dir_, front_).normalized()
        self.__build_basis(right_ * self.sx, up_, front_ * self.sz)

    @property
    def right(self) -> Vector3:
        return Vector3(self.__transform_m.m00,
                       self.__transform_m.m10,
                       self.__transform_m.m20).normalize()

    @right.setter
    def right(self, right_: Vector3) -> None:
        length_ = right_.magnitude()
        if length_ < 1e-9:
            raise ArithmeticError("Error transform up set")
        right_dir_ = right_ / length_
        front_ = Vector3.cross(right_dir_, Vector3(0, 1, 0)).normalized()
        up_ = Vector3.cross(front_, right_dir_).normalized()
        self.__build_basis(right_, up_ * self.sy, front_ * self.sz)

    @property
    def sx(self) -> float:
        x = self.__transform_m.m00
        y = self.__transform_m.m10
        z = self.__transform_m.m20
        return math.sqrt(x * x + y * y + z * z)

    @property
    def sy(self) -> float:
        x = self.__transform_m.m01
        y = self.__transform_m.m11
        z = self.__transform_m.m21
        return math.sqrt(x * x + y * y + z * z)

    @property
    def sz(self) -> float:
        """
        установить масштаб по Х
        :return:
        """
        x = self.__transform_m.m02
        y = self.__transform_m.m12
        z = self.__transform_m.m22
        return math.sqrt(x * x + y * y + z * z)

    @sx.setter
    def sx(self, s_x: float) -> None:
        if s_x == 0:
            return
        scl = self.sx
        self.__transform_m = Matrix4.build_transform(self.__transform_m.right * s_x / scl,
                                                     self.__transform_m.up,
                                                     self.__transform_m.front, self.origin)

    @sy.setter
    def sy(self, s_y: float) -> None:
        """
        установить масштаб по Y
        :param s_y:
        :return:
        """
        if s_y == 0:
            return
        scl = self.sy
        self.__transform_m = Matrix4.build_transform(self.__transform_m.right,
                                                     self.__transform_m.up    *  s_y / scl,
                                                     self.__transform_m.front, self.origin)

    # установить масштаб по Z
    @sz.setter
    def sz(self, s_z: float) -> None:
        if s_z == 0:
            return
        scl = self.sz
        self.__transform_m = Matrix4.build_transform(self.__transform_m.right,
                                                     self.__transform_m.up   ,
                                                     self.__transform_m.front *  s_z / scl, self.origin)

    @property
    def scale(self) -> Vector3:
        return Vector3(self.sx, self.sy, self.sz)

    @scale.setter
    def scale(self, xyz: Vector3):
        scl = self.scale
        self.__transform_m = Matrix4.build_transform(self.__transform_m.right *  xyz.x / scl.x,
                                                     self.__transform_m.up    *  xyz.y / scl.y,
                                                     self.__transform_m.front *  xyz.z / scl.z, self.origin)

    @property
    def x(self) -> float:
        return self.__transform_m.m03

    @property
    def y(self) -> float:
        return self.__transform_m.m13

    @property
    def z(self) -> float:
        return self.__transform_m.m23

    @x.setter
    def x(self, x: float) -> None:
        self.origin = Vector3(x, self.y, self.z)

    @y.setter
    def y(self, y: float) -> None:
        self.origin = Vector3(self.x, y, self.z)

    @z.setter
    def z(self, z: float) -> None:
        self.origin = Vector3(self.x, self.y, z)

    @property
    def origin(self) -> Vector3:
        return Vector3(self.x, self.y, self.z)

    @origin.setter
    def origin(self, xyz: Vector3) -> None:
        self.__transform_m = Matrix4.build_transform(self.__transform_m.right,
                                                     self.__transform_m.up,
                                                     self.__transform_m.front, xyz)

    @property
    def angles(self) -> Vector3:
        return Matrix4.to_euler_angles(self.rotation_mat())

    @angles.setter
    def angles(self, xyz: Vector3) -> None:
        i: Matrix4 = Matrix4.rotate_x(xyz.x)
        i = Matrix4.rotate_y(xyz.y) * i
        i = Matrix4.rotate_z(xyz.z) * i
        scl = self.scale
        orig = self.origin
        self.__transform_m = Matrix4.build_transform(i.right * scl.x, i.up * scl.y, i.front * scl.z, orig)

    @property
    def ax(self) -> float:
        return Matrix4.to_euler_angles(self.rotation_mat()).x

    @property
    def ay(self) -> float:
        return Matrix4.to_euler_angles(self.rotation_mat()).y

    @property
    def az(self) -> float:
        return Matrix4.to_euler_angles(self.rotation_mat()).z

    @ax.setter
    def ax(self, x: float) -> None:
        _angles = self.angles
        self.angles = Vector3(deg_to_rad(x), _angles.y, _angles.z)

    @ay.setter
    def ay(self, y: float) -> None:
        _angles = self.angles
        self.angles = Vector3(_angles.x, deg_to_rad(y), _angles.z)

    @az.setter
    def az(self, z: float) -> None:
        _angles = self.angles
        self.angles = Vector3(_angles.x, _angles.y, deg_to_rad(z))

    def rotation_mat(self) -> Matrix4:
        scl = 1.0 / self.scale
        return Matrix4(self.__transform_m.m00 * scl.x, self.__transform_m.m01 * scl.y, self.__transform_m.m02 * scl.z, 0,
                       self.__transform_m.m10 * scl.x, self.__transform_m.m11 * scl.y, self.__transform_m.m12 * scl.z, 0,
                       self.__transform_m.m20 * scl.x, self.__transform_m.m21 * scl.y, self.__transform_m.m22 * scl.z, 0,
                       0, 0, 0, 1)

    def look_at(self, target: Vector3, eye: Vector3, up: Vector3 = Vector3(0, 1, 0)) -> None:
        self.__transform_m = Matrix4.look_at(target, eye, up)

    def transform_vect(self, vec: Vector3, w=1.0) -> Vector3:
        """
        переводит вектор в собственное пространство координат
        :param vec:
        :param w:
        :return:
        """
        if w == 0:
            return Vector3(self.__transform_m.m00 * vec.x + self.__transform_m.m01 * vec.y + self.__transform_m.m02 * vec.z,
                           self.__transform_m.m10 * vec.x + self.__transform_m.m11 * vec.y + self.__transform_m.m12 * vec.z,
                           self.__transform_m.m20 * vec.x + self.__transform_m.m21 * vec.y + self.__transform_m.m22 * vec.z)

        return Vector3(
            self.__transform_m.m00 * vec.x + self.__transform_m.m01 * vec.y + self.__transform_m.m02 * vec.z + self.__transform_m.m03,
            self.__transform_m.m10 * vec.x + self.__transform_m.m11 * vec.y + self.__transform_m.m12 * vec.z + self.__transform_m.m13,
            self.__transform_m.m20 * vec.x + self.__transform_m.m21 * vec.y + self.__transform_m.m22 * vec.z + self.__transform_m.m23)

    def inv_transform_vect(self, vec: Vector3, w=1.0) -> Vector3:
        """
        не переводит вектор в собственное пространство координат =)
        :param vec:
        :param w:
        :return:
        """
        scl: Vector3 = self.scale
        scl = Vector3(1.0 / (scl.x * scl.x), 1.0 / (scl.y * scl.y), 1.0 / (scl.z * scl.z))
        if w == 0:
            return Vector3((self.__transform_m.m00 * vec.x + self.__transform_m.m10 * vec.y + self.__transform_m.m20 * vec.z) * scl.x,
                           (self.__transform_m.m01 * vec.x + self.__transform_m.m11 * vec.y + self.__transform_m.m21 * vec.z) * scl.y,
                           (self.__transform_m.m02 * vec.x + self.__transform_m.m12 * vec.y + self.__transform_m.m22 * vec.z) * scl.z)

        vec_ = Vector3(vec.x - self.x, vec.y - self.y, vec.z - self.z)
        return Vector3((self.__transform_m.m00 * vec_.x + self.__transform_m.m10 * vec_.y + self.__transform_m.m20 * vec_.z) * scl.x,
                       (self.__transform_m.m01 * vec_.x + self.__transform_m.m11 * vec_.y + self.__transform_m.m21 * vec_.z) * scl.y,
                       (self.__transform_m.m02 * vec_.x + self.__transform_m.m12 * vec_.y + self.__transform_m.m22 * vec_.z) * scl.z)
