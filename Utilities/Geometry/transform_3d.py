from .common import DEG_TO_RAD, RAD_TO_DEG
from .quaternion import Quaternion
from .vector3 import Vector3
from .matrix4 import Matrix4
import math


def deg_to_rad(deg: float) -> float:
    """
    :param deg: угол в градусах
    :return: угол в радианах
    """
    return deg / 180.0 * math.pi


class Transform3d:

    __slots__ = ("_raw_i_t_m", "_t_m", "_i_t_m", "_angles")

    def __init__(self):
        self._raw_i_t_m: bool = False
        self._angles: Vector3 = Vector3(0.0, 0.0, 0.0)
        self._t_m = Matrix4(1.0, 0.0, 0.0, 0.0,
                            0.0, 1.0, 0.0, 0.0,
                            0.0, 0.0, 1.0, 0.0,
                            0.0, 0.0, 0.0, 1.0)
        self._i_t_m = Matrix4(1.0, 0.0, 0.0, 0.0,
                              0.0, 1.0, 0.0, 0.0,
                              0.0, 0.0, 1.0, 0.0,
                              0.0, 0.0, 0.0, 1.0)

    def _build_i_t_m(self) -> None:
        self._raw_i_t_m = True

    def __str__(self) -> str:
        return f"{{\n" \
               f"\t\"unique_id\"   :{self.unique_id},\n" \
               f"\t\"origin\"      :{self.origin},\n" \
               f"\t\"scale\"       :{self.scale},\n" \
               f"\t\"rotate\"      :{self.angles / math.pi * 180.0},\n" \
               f"\t\"transform_m\" :\n{self._t_m}" \
               f"\n}}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Transform3d):
            return False
        if not(self._t_m == other._t_m):
            return False
        return True

    def __hash__(self) -> int:
        return hash(self._t_m)

    def _build_basis(self, ex: Vector3, ey: Vector3, ez: Vector3) -> None:
        self._t_m = Matrix4(ex.x, ey.x, ez.x, self._t_m.m03,
                            ex.y, ey.y, ez.y, self._t_m.m13,
                            ex.z, ey.z, ez.z, self._t_m.m23,
                            0.0, 0.0, 0.0, 1.0)
        self._build_i_t_m()

    @property
    def unique_id(self) -> int:
        return id(self)

    @property
    def inv_transform_matrix(self) -> Matrix4:
        if self._raw_i_t_m:
            self._raw_i_t_m = False
            s = 1.0 / self.scale
            r = Vector3(self._t_m.m00 * s.x, self._t_m.m10 * s.x, self._t_m.m20 * s.x)
            u = Vector3(self._t_m.m01 * s.y, self._t_m.m11 * s.y, self._t_m.m21 * s.y)
            f = Vector3(self._t_m.m02 * s.z, self._t_m.m12 * s.z, self._t_m.m22 * s.z)
            o = self.origin
            self._i_t_m = Matrix4(r.x * s.x, r.y * s.x, r.z * s.x, -Vector3.dot(o, r) * s.x,
                                  u.x * s.y, u.y * s.y, u.z * s.y, -Vector3.dot(o, u) * s.y,
                                  f.x * s.z, f.y * s.z, f.z * s.z, -Vector3.dot(o, f) * s.z,
                                  0.0, 0.0, 0.0, 1.0)
        return self._i_t_m

    @property
    def transform_matrix(self) -> Matrix4:
        return self._t_m

    @transform_matrix.setter
    def transform_matrix(self, t: Matrix4) -> None:
        self._t_m = Matrix4(t.m00, t.m01, t.m02, t.m03,
                            t.m10, t.m11, t.m12, t.m13,
                            t.m20, t.m21, t.m22, t.m23,
                            0.0,   0.0,   0.0,   1.0)
        self._build_i_t_m()

    @property
    def front(self) -> Vector3:
        return Vector3(self._t_m.m02, self._t_m.m12, self._t_m.m22).normalize()

    @front.setter
    def front(self, front_: Vector3) -> None:
        length_ = front_.magnitude()
        if length_ < 1e-9:
            raise ArithmeticError("Error transform front set")
        front_dir_ = front_ / length_
        right_ = Vector3.cross(front_dir_, Vector3(0.0, 1.0, 0.0)).normalize()
        up_ = Vector3.cross(right_, front_dir_).normalize()
        sx = self.sx
        sy = self.sy
        self._t_m = Matrix4(right_.x * sx, up_.x * sy, front_.x, self._t_m.m03,
                            right_.y * sx, up_.y * sy, front_.y, self._t_m.m13,
                            right_.z * sx, up_.z * sy, front_.z, self._t_m.m23,
                            0.0,   0.0,   0.0,   1.0)
        self._build_i_t_m()

    @property
    def up(self) -> Vector3:
        return Vector3(self._t_m.m01, self._t_m.m11, self._t_m.m21).normalize()

    @up.setter
    def up(self, up_: Vector3) -> None:
        length_ = up_.magnitude()
        if length_ < 1e-9:
            raise ArithmeticError("Error transform up set")
        up_dir_ = up_ / length_
        front_ = Vector3.cross(up_dir_, Vector3(1.0, 0.0, 0.0)).normalize()
        right_ = Vector3.cross(up_dir_, front_).normalize()
        sx = self.sx
        sz = self.sz
        self._t_m = Matrix4(right_.x * sx, up_.x, front_.x * sz, self._t_m.m03,
                            right_.y * sx, up_.y, front_.y * sz, self._t_m.m13,
                            right_.z * sx, up_.z, front_.z * sz, self._t_m.m23,
                            0.0,   0.0,   0.0,   1.0)
        self._build_i_t_m()

    @property
    def right(self) -> Vector3:
        return Vector3(self._t_m.m00, self._t_m.m10, self._t_m.m20).normalize()

    @right.setter
    def right(self, right_: Vector3) -> None:
        length_ = right_.magnitude()
        if length_ < 1e-9:
            raise ArithmeticError("Error transform up set")
        right_dir_ = right_ / length_
        front_ = Vector3.cross(right_dir_, Vector3(0.0, 1.0, 0.0)).normalize()
        up_ = Vector3.cross(front_, right_dir_).normalize()
        sy = self.sy
        sz = self.sz
        self._t_m = Matrix4(right_.x, up_.x * sy, front_.x * sz, self._t_m.m03,
                            right_.y, up_.y * sy, front_.y * sz, self._t_m.m13,
                            right_.z, up_.z * sy, front_.z * sz, self._t_m.m23,
                            0.0,   0.0,   0.0,   1.0)
        self._build_i_t_m()

    @property
    def sx(self) -> float:
        x = self._t_m.m00
        y = self._t_m.m10
        z = self._t_m.m20
        return math.sqrt(x * x + y * y + z * z)

    @property
    def sy(self) -> float:
        x = self._t_m.m01
        y = self._t_m.m11
        z = self._t_m.m21
        return math.sqrt(x * x + y * y + z * z)

    @property
    def sz(self) -> float:
        """
        установить масштаб по Х
        :return:
        """
        x = self._t_m.m02
        y = self._t_m.m12
        z = self._t_m.m22
        return math.sqrt(x * x + y * y + z * z)

    @sx.setter
    def sx(self, s_x: float) -> None:
        assert isinstance(s_x, float)
        if s_x == 0.0:
            return
        scl = s_x / self.sx
        self._t_m.m00 *= scl
        self._t_m.m10 *= scl
        self._t_m.m20 *= scl
        self._build_i_t_m()

    @sy.setter
    def sy(self, s_y: float) -> None:
        """
        установить масштаб по Y
        :param s_y:
        :return:
        """
        assert isinstance(s_y, float)
        if s_y == 0.0:
            return
        scl = s_y / self.sy
        self._t_m.m01 *= scl
        self._t_m.m11 *= scl
        self._t_m.m21 *= scl
        self._build_i_t_m()

    # установить масштаб по Z
    @sz.setter
    def sz(self, s_z: float) -> None:
        assert isinstance(s_z, float)
        if s_z == 0.0:
            return
        scl = s_z / self.sz
        self._t_m.m02 *= scl
        self._t_m.m12 *= scl
        self._t_m.m22 *= scl
        self._build_i_t_m()

    @property
    def scale(self) -> Vector3:
        return Vector3(self.sx, self.sy, self.sz)

    @scale.setter
    def scale(self, xyz: Vector3):
        assert isinstance(xyz, Vector3)
        scl = xyz / self.scale
        self._t_m.m00 *= scl.z
        self._t_m.m10 *= scl.z
        self._t_m.m20 *= scl.z

        self._t_m.m01 *= scl.z
        self._t_m.m11 *= scl.z
        self._t_m.m21 *= scl.z

        self._t_m.m02 *= scl.z
        self._t_m.m12 *= scl.z
        self._t_m.m22 *= scl.z
        self._build_i_t_m()

    @property
    def x(self) -> float:
        return self._t_m.m03

    @property
    def y(self) -> float:
        return self._t_m.m13

    @property
    def z(self) -> float:
        return self._t_m.m23

    @x.setter
    def x(self, x: float) -> None:
        self._t_m.m03 = x
        self._build_i_t_m()

    @y.setter
    def y(self, y: float) -> None:
        self._t_m.m13 = y
        self._build_i_t_m()

    @z.setter
    def z(self, z: float) -> None:
        self._t_m.m23 = z
        self._build_i_t_m()

    @property
    def origin(self) -> Vector3:
        return Vector3(self.x, self.y, self.z)

    @origin.setter
    def origin(self, xyz: Vector3) -> None:
        assert isinstance(xyz, Vector3)
        self._t_m.m03 = xyz.x
        self._t_m.m13 = xyz.y
        self._t_m.m23 = xyz.z
        self._build_i_t_m()

    @property
    def rotation(self) -> Quaternion:
        return Quaternion.from_euler_angles(self._angles.x * DEG_TO_RAD,
                                            self._angles.y * DEG_TO_RAD,
                                            self._angles.z * DEG_TO_RAD)

    @rotation.setter
    def rotation(self, q: Quaternion) -> None:
        assert isinstance(q, Quaternion)
        i = q.to_rotation_matrix()
        scl  = self.scale
        self._angles = q.to_euler_angles() * RAD_TO_DEG
        self._t_m =  Matrix4(i.m00 * scl.x, i.m01 * scl.y, i.m02 * scl.z, self._t_m.m03,
                             i.m10 * scl.x, i.m11 * scl.y, i.m12 * scl.z, self._t_m.m13,
                             i.m20 * scl.x, i.m21 * scl.y, i.m22 * scl.z, self._t_m.m23,
                             0.0,   0.0,   0.0,   1.0)
        self._build_i_t_m()

    @property
    def angles(self) -> Vector3:
        return self._angles

    @angles.setter
    def angles(self, xyz: Vector3) -> None:
        assert isinstance(xyz, Vector3)
        self._angles = xyz
        i: Matrix4 = Matrix4.rotate_x(xyz.x)
        i = Matrix4.rotate_y(xyz.y) * i
        i = Matrix4.rotate_z(xyz.z) * i
        scl  = self.scale
        self._t_m =  Matrix4(i.m00 * scl.x, i.m01 * scl.y, i.m02 * scl.z, self._t_m.m03,
                             i.m10 * scl.x, i.m11 * scl.y, i.m12 * scl.z, self._t_m.m13,
                             i.m20 * scl.x, i.m21 * scl.y, i.m22 * scl.z, self._t_m.m23,
                             0.0,   0.0,   0.0,   1.0)
        self._build_i_t_m()

    @property
    def ax(self) -> float:
        return self.angles.x  # Matrix4.to_euler_angles(self.rotation_mat()).x

    @property
    def ay(self) -> float:
        return self.angles.y  # Matrix4.to_euler_angles(self.rotation_mat()).y

    @property
    def az(self) -> float:
        return self.angles.z  # Matrix4.to_euler_angles(self.rotation_mat()).z

    @ax.setter
    def ax(self, x: float) -> None:
        assert isinstance(x, float)
        _angles = self.angles
        self.angles = Vector3(deg_to_rad(x), _angles.y, _angles.z)

    @ay.setter
    def ay(self, y: float) -> None:
        assert isinstance(y, float)
        _angles = self.angles
        self.angles = Vector3(_angles.x, deg_to_rad(y), _angles.z)

    @az.setter
    def az(self, z: float) -> None:
        assert isinstance(z, float)
        _angles = self.angles
        self.angles = Vector3(_angles.x, _angles.y, deg_to_rad(z))

    def rotation_mat(self) -> Matrix4:
        scl = 1.0 / self.scale
        return Matrix4(self._t_m.m00 * scl.x, self._t_m.m01 * scl.y, self._t_m.m02 * scl.z, 0.0,
                       self._t_m.m10 * scl.x, self._t_m.m11 * scl.y, self._t_m.m12 * scl.z, 0.0,
                       self._t_m.m20 * scl.x, self._t_m.m21 * scl.y, self._t_m.m22 * scl.z, 0.0,
                       0.0, 0.0, 0.0, 1.0)

    def look_at(self, target: Vector3, eye: Vector3, up: Vector3 = Vector3(0.0, 1.0, 0.0)) -> None:
        self._t_m = Matrix4.transform_look_at(target, eye, up)
        self._build_i_t_m()
        self._angles = Matrix4.to_euler_angles(self._t_m)

    def transform_vect(self, vec: Vector3, w=1.0) -> Vector3:
        """
        переводит вектор в собственное пространство координат
        :param vec:
        :param w:
        :return:
        """
        return self.transform_matrix.multiply_by_direction(vec) if w == 0 else \
            self.transform_matrix.multiply_by_point(vec)

    def inv_transform_vect(self, vec: Vector3, w=1.0) -> Vector3:
        """
        не переводит вектор в собственное пространство координат =)
        :param vec:
        :param w:
        :return:
        """
        return self.inv_transform_matrix.multiply_by_direction(vec) if w == 0 else \
            self.inv_transform_matrix.multiply_by_point(vec)


def transform_3d_test():
    t = Transform3d()
    t.x = 1.2
    t.y = -3.44
    t.z = 12.1

    t.sx = 0.2
    t.sy = 0.44
    t.sz = 1.5

    # t.ax = 41.2
    # t.ay = 14.44
    # t.az = 51.5

    v = Vector3(1, 2, 3)
    vt = t.transform_vect(v)
    print(v)
    print(vt)
    print(t.inv_transform_vect(vt))
    print(t)
