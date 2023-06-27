from UIQt.GLUtilities.gl_material import MaterialGL
from UIQt.GLUtilities.gl_shader import ShaderGL
from Utilities.Geometry import Vector3


class GridMaterial(MaterialGL):

    def __init__(self, shader: ShaderGL = None):
        super().__init__(shader)
        self._x_axis_color: Vector3 = Vector3(1, 0, 0)
        self._y_axis_color: Vector3 = Vector3(0, 1, 0)
        self._z_axis_color: Vector3 = Vector3(0, 0, 1)
        self._grid_color: Vector3 = Vector3(0.9, 0.9, 0.9)

        self._grid_fade: float = 1.5
        self._grid_fade_radius: float = 4.5

        self._grid_x_step: float = 1.0
        self._grid_y_step: float = 1.0

        self._grid_line_width: float = 0.01

    @property
    def grid_fade(self) -> float:
        return self._grid_fade

    @grid_fade.setter
    def grid_fade(self, val: float) -> None:
        self._grid_fade = val
        with self._shader:
            self._shader.send_float("fade", self._grid_fade)

    @property
    def grid_fade_radius(self) -> float:
        return self._grid_fade_radius

    @grid_fade_radius.setter
    def grid_fade_radius(self, val: float) -> None:
        self._grid_fade_radius = val
        with self._shader:
            self._shader.send_float("fade_radius", self._grid_fade_radius)

    @property
    def grid_x_step(self) -> float:
        return self._grid_x_step

    @grid_x_step.setter
    def grid_x_step(self, val: float) -> None:
        self._grid_x_step = val
        with self._shader:
            self._shader.send_float("grid_x_step", self._grid_x_step)

    @property
    def grid_y_step(self) -> float:
        return self._grid_x_step

    @grid_y_step.setter
    def grid_y_step(self, val: float) -> None:
        self._grid_y_step = val
        with self._shader:
            self._shader.send_float("grid_y_step", self._grid_y_step)

    @property
    def grid_line_width(self) -> float:
        return self._grid_line_width

    @grid_line_width.setter
    def grid_line_width(self, val: float) -> None:
        self._grid_line_width = val
        with self._shader:
            self._shader.send_float("line_size", self._grid_line_width)

    @property
    def x_axis_color(self) -> Vector3:
        return self._x_axis_color

    @x_axis_color.setter
    def x_axis_color(self, x_axis_color: Vector3) -> None:
        self._x_axis_color = x_axis_color
        with self._shader:
            self._shader.send_vec_3("x_axis_color", self.x_axis_color)

    @property
    def y_axis_color(self) -> Vector3:
        return self._y_axis_color

    @y_axis_color.setter
    def y_axis_color(self, y_axis_color: Vector3) -> None:
        self._y_axis_color = y_axis_color
        with self._shader:
            self._shader.send_vec_3("y_axis_color", self.y_axis_color)

    @property
    def z_axis_color(self) -> Vector3:
        return self._z_axis_color

    @z_axis_color.setter
    def z_axis_color(self, z_axis_color: Vector3) -> None:
        self._z_axis_color = z_axis_color
        with self._shader:
            self._shader.send_vec_3("z_axis_color", self.z_axis_color)

    @property
    def grid_color(self) -> Vector3:
        return self._grid_color

    @grid_color.setter
    def grid_color(self, grid_color: Vector3) -> None:
        self._grid_color = grid_color
        with self._shader:
            self._shader.send_vec_3("line_color", self.grid_color)

    def _update_shader(self):
        self._shader.send_float("fade", self.grid_fade)
        self._shader.send_float("fade_radius", self.grid_fade_radius)

        self._shader.send_float("grid_x_step", self.grid_x_step)
        self._shader.send_float("grid_y_step", self.grid_y_step)

        self._shader.send_float("line_size", self.grid_line_width)

        self._shader.send_vec_3("x_axis_color", self.x_axis_color)
        self._shader.send_vec_3("y_axis_color", self.y_axis_color)
        self._shader.send_vec_3("z_axis_color", self.z_axis_color)
        self._shader.send_vec_3("line_color",   self.grid_color)


