from .common import RAD_TO_DEG, DEG_TO_RAD
from .matrix3 import Matrix3
from .vector2 import Vector2
import math


class Transform2d:

    __slots__ = ("_raw_i_t_m", "_t_m", "_i_t_m")

    def __init__(self):
        self._raw_i_t_m: bool = False
        self._t_m = Matrix3(1.0, 0.0, 0.0,
                            0.0, 1.0, 0.0,
                            0.0, 0.0, 1.0)
        self._i_t_m = Matrix3(1.0, 0.0, 0.0,
                              0.0, 1.0, 0.0,
                              0.0, 0.0, 1.0)

    def _build_i_t_m(self) -> None:
        self._raw_i_t_m = True

    def __str__(self) -> str:
        return f"{{\n\t\"unique_id\"   :{self.unique_id},\n" \
                   f"\t\"origin\"      :{self.origin},\n" \
                   f"\t\"scale\"       :{self.scale},\n" \
                   f"\t\"rotate\"      :{self.az / math.pi * 180},\n" \
                   f"\t\"transform_m\" :\n{self._t_m}}}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Transform2d):
            return False
        if not(self._t_m == other._t_m):
            return False
        return True

    def __hash__(self) -> int:
        return hash(self._t_m)

    def _build_basis(self, ex: Vector2, ey: Vector2) -> None:
        self._t_m = Matrix3(ex.x, ey.x, self._t_m.m02,
                            ex.y, ey.y, self._t_m.m12,
                            0.0,  0.0,  1.0)
        self._build_i_t_m()

    @property
    def unique_id(self) -> int:
        return id(self)

    @property
    def inv_transform_matrix(self) -> Matrix3:
        if self._raw_i_t_m:
            self._raw_i_t_m = False
            s = self.scale
            s = 1.0 / s
            r = Vector2(self._t_m.m00 * s.x, self._t_m.m10 * s.x, )
            u = Vector2(self._t_m.m01 * s.y, self._t_m.m11 * s.y)
            o = self.origin
            self._i_t_m = Matrix3(r.x * s.x, r.y * s.x, -Vector2.dot(o, r) * s.x,
                                  u.x * s.y, u.y * s.y, -Vector2.dot(o, u) * s.y,
                                  0.0, 0.0, 1.0)
        return self._i_t_m

    @property
    def transform_matrix(self) -> Matrix3:
        return self._t_m

    @property
    def front(self) -> Vector2:
        return Vector2(self._t_m.m00, self._t_m.m10).normalize()

    @property
    def up(self) -> Vector2:
        return Vector2(self._t_m.m01, self._t_m.m11).normalize()

    @property
    def scale(self) -> Vector2:
        return Vector2(self.sx, self.sy)

    @property
    def sx(self) -> float:
        """
        масштаб по Х
        """
        x = self._t_m.m00
        y = self._t_m.m10
        return math.sqrt(x * x + y * y)

    @property
    def sy(self) -> float:
        """
        масштаб по Y
        """
        x = self._t_m.m01
        y = self._t_m.m11
        return math.sqrt(x * x + y * y)

    @sx.setter
    def sx(self, s_x: float) -> None:
        """
        Установить масштаб по Х
        """
        if s_x == 0:
            return
        scl = s_x / self.sx
        self._t_m.m00 *= scl
        self._t_m.m10 *= scl
        self._build_i_t_m()

    @sy.setter
    def sy(self, s_y: float) -> None:
        """
        Установить масштаб по Y
        """
        if s_y == 0:
            return
        scl = s_y / self.sy
        self._t_m.m01 *= scl
        self._t_m.m11 *= scl
        self._build_i_t_m()

    @scale.setter
    def scale(self, sxy: Vector2) -> None:
        assert isinstance(sxy, Vector2)
        scl = sxy / self.scale
        self._t_m.m00 *= scl.x
        self._t_m.m10 *= scl.x

        self._t_m.m01 *= scl.y
        self._t_m.m11 *= scl.y
        self._build_i_t_m()

    @property
    def x(self) -> float:
        return self._t_m.m02

    @property
    def y(self) -> float:
        return self._t_m.m12

    @property
    def origin(self) -> Vector2:
        return Vector2(self.x, self.y)

    @x.setter
    def x(self, x: float) -> None:
        self._t_m.m02 = x

    @y.setter
    def y(self, y: float) -> None:
        self._t_m.m12 = y

    @origin.setter
    def origin(self, xy: Vector2) -> None:
        assert isinstance(xy, Vector2)
        self._t_m.m02 = xy.x
        self._t_m.m12 = xy.y
        self._build_i_t_m()

    @property
    def az(self) -> float:
        sx = self.sx
        cos_a = self._t_m.m00 / sx
        if abs(cos_a) > 1e-3:
            return math.acos(cos_a) * RAD_TO_DEG
        return math.acos(self._t_m.m10 / sx) * RAD_TO_DEG

    @az.setter
    def az(self, angle: float) -> None:
        cos_a = math.cos(angle * DEG_TO_RAD)
        sin_a = math.sin(angle * DEG_TO_RAD)
        i = Matrix3(cos_a, sin_a, 0.0,
                    -sin_a, cos_a, 0.0,
                     0.0,     0.0, 1.0)
        scl  = self.scale
        self._t_m = Matrix3(i.m00 * scl.x, i.m01 * scl.y, self._t_m.m02,
                            i.m10 * scl.x, i.m11 * scl.y, self._t_m.m12,
                            0.0,           0.0,           1.0)
        # Matrix3.build_transform(i.right * scl.x, i.up * scl.y, orig)
        self._build_i_t_m()

    def transform_vect(self, vec: Vector2, w=1.0) -> Vector2:
        """
        переводит вектор в собственное пространство координат
        :param vec:
        :param w:
        :return:
        """
        return self.transform_matrix.multiply_by_direction(vec) if w == 0 else \
            self.transform_matrix.multiply_by_point(vec)

    def inv_transform_vect(self, vec: Vector2, w=1.0) -> Vector2:
        """
        не переводит вектор в собственное пространство координат =)
        :param vec:
        :param w:
        :return:
        """
        return self.inv_transform_matrix.multiply_by_direction(vec) if w == 0 else \
            self.inv_transform_matrix.multiply_by_point(vec)


def transform_2d_test():
    t = Transform2d()
    t.x = 1.2
    t.y = -3.44

    t.sx = 0.2
    t.sy = 0.44

    # t.ax = 41.2
    # t.ay = 14.44
    # t.az = 51.5

    v = Vector2(1, 2)
    vt = t.transform_vect(v)
    print(v)
    print(vt)
    print(t.inv_transform_vect(vt))
    print(f'[{", ".join(str(v)for v in t.transform_matrix)}]')