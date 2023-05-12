# import UIQt.GLUtilities.gl_globals as gl_globals
from UIQt.GLUtilities.gl_shader import ShaderGL


class MaterialGL:

    __bounded_id = 0

    @staticmethod
    def bounded_id() -> int:
        return MaterialGL.__bounded_id

    def __init__(self, shader: ShaderGL = None):
        self._id = id(self)
        self._shader: ShaderGL = shader

    def __enter__(self):
        self.bind()

    @property
    def shader(self) -> ShaderGL:
        return self._shader

    @property
    def unique_id(self) -> int:
        return self._id

    def update_shader(self):
        with self._shader:
            self._update_shader()

    def _update_shader(self):
        pass

    def bind(self):
        self._shader.bind()
        if self.unique_id != MaterialGL.bounded_id():
            self._update_shader()
            MaterialGL.__bounded_id = self.unique_id
