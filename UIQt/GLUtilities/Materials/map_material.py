import UIQt.GLUtilities.gl_globals as gl_globals
from UIQt.GLUtilities.gl_texture import TextureGL
from UIQt.GLUtilities.gl_shader import Shader
from Utilities.Geometry import Vector3
from ..gl_material import MaterialGL


class MapMaterial(MaterialGL):
    # based on *.mtl file definition
    def __init__(self, shader: Shader = None):
        super().__init__(shader)
        self._bound_min: Vector3 = Vector3(-0.5, -0.5, -0.5)
        self._max_bound: Vector3 = Vector3(0.5, 0.5, 0.5)
        self._heat_or_height: int = 1

    @property
    def heat_or_height(self) -> int:
        return self._heat_or_height

    @heat_or_height.setter
    def heat_or_height(self, val: int) -> None:
        self._heat_or_height = max(min(1, val), 0)
        with self._shader:
            self._shader.send_int("heat_or_height", self.heat_or_height)

    @property
    def max_bound(self) -> Vector3:
        return self._max_bound

    @max_bound.setter
    def max_bound(self, max_bound: Vector3) -> None:
        self._max_bound = max_bound
        with self._shader:
            self._shader.send_vec_3("max_bound", self.max_bound)

    @property
    def min_bound(self) -> Vector3:
        return self._bound_min

    @min_bound.setter
    def min_bound(self, min_bound: Vector3) -> None:
        self._bound_min = min_bound
        with self._shader:
            self._shader.send_vec_3("min_bound", self.min_bound)

    def _update_shader(self):
        self._shader.send_int("heat_or_height", self.heat_or_height)
        self._shader.send_vec_3("max_bound", self.max_bound)
        self._shader.send_vec_3("min_bound", self.min_bound)

