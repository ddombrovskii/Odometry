from UIQt.GLUtilities.gl_texture import TextureGL
from UIQt.GLUtilities.gl_shader import Shader
from Utilities import Vector3


class MaterialGL:
    # based on *.mtl file definition
    def __init__(self, shader: Shader = None):
        self._shader: Shader = Shader.SAMPLE_SHADER if shader is None else shader
        self._diffuse_color: Vector3 = Vector3(1, 1, 1)  # Kd: specifies diffuse color
        self._specular_color: Vector3 = Vector3(1, 1, 1)  # Ks: specifies specular color
        self._ns: float = 10  # defines the focus of specular highlights in the material.
        # Ns values normally range from 0 to 1000, with a high value resulting in a tight, concentrated highlight.
        self._ni: float = 1.5  # Ni: defines the optical density
        self._dissolve: float = 1.0  # d or Tr: specifies a factor for dissolve, how much this material dissolves into the background.
        # A factor of 1.0 is fully opaque. A factor of 0.0 is completely transparent.
        self._illum: float = 2.0  # illum: specifies an illumination model, using a numeric value
        self._diffuse: TextureGL = TextureGL.PINK_TEXTURE
        self._specular: TextureGL = TextureGL.PINK_TEXTURE
        self._normals: TextureGL = TextureGL.PINK_TEXTURE

    @property
    def shader(self) -> Shader:
        return self._shader

    @property
    def unique_id(self) -> int:
        return id(self)

    @property
    def ni(self) -> float:
        return self._ni
    
    @ni.setter
    def ni(self, val: float) -> None:
        self._ni = val
        with self._shader:
            self._shader.send_float("ni", self.ni)

    @property
    def ns(self) -> float:
        return self._ni

    @ns.setter
    def ns(self, val: float) -> None:
        self._ns = val
        with self._shader:
            self._shader.send_float("ns", self.ns)

    @property
    def dissolve(self) -> float:
        return self._dissolve

    @dissolve.setter
    def dissolve(self, val: float) -> None:
        self._dissolve = val
        with self._shader:
            self._shader.send_float("dissolve", self.dissolve)

    @property
    def illum(self) -> float:
        return self._illum

    @illum.setter
    def illum(self, val: float) -> None:
        self._illum = val
        with self._shader:
            self._shader.send_float("illum", self.illum)

    @property
    def specular_color(self) -> Vector3:
        return self._specular_color

    @specular_color.setter
    def specular_color(self, specular_color: Vector3) -> None:
        self._specular_color = specular_color
        with self._shader:
            self._shader.send_vec_3("specular_color", self.specular_color)

    @property
    def diffuse_color(self) -> Vector3:
        return self._diffuse_color

    @diffuse_color.setter
    def diffuse_color(self, diffuse_color: Vector3) -> None:
        self._diffuse_color = diffuse_color
        with self._shader:
            self._shader.send_vec_3("diffuse_color", self.diffuse_color)

    @property
    def diffuse_texture(self) -> TextureGL:
        return self._diffuse

    @diffuse_texture.setter
    def diffuse_texture(self, diffuse_texture: TextureGL) -> None:
        self._diffuse = TextureGL.PINK_TEXTURE if diffuse_texture is None else diffuse_texture
        with self._shader:
            self._diffuse.bind_to_channel(0)

    @property
    def specular_texture(self) -> TextureGL:
        return self._specular

    @specular_texture.setter
    def specular_texture(self, specular_texture: TextureGL) -> None:
        self._specular = TextureGL.PINK_TEXTURE if specular_texture is None else specular_texture
        with self._shader:
            self._specular.bind_to_channel(1)

    @property
    def normals_texture(self) -> TextureGL:
        return self._normals

    @normals_texture.setter
    def normals_texture(self, normals_texture: TextureGL) -> None:
        self._normals = TextureGL.PINK_TEXTURE if normals_texture is None else normals_texture
        with self._shader:
            self._normals.bind_to_channel(2)

    def update_shader(self):
        with self._shader:
            self._update_shader()

    def _update_shader(self):
        self._shader.send_float("ns", self.ns)
        self._shader.send_float("ni", self.ni)
        self._shader.send_float("dissolve", self.dissolve)
        self._shader.send_float("illum", self.illum)
        self._shader.send_vec_3("specular_color", self.specular_color)
        self._shader.send_vec_3("diffuse_color", self.diffuse_color)
        self._diffuse.bind_to_channel(0)
        self._specular.bind_to_channel(1)
        self._normals.bind_to_channel(2)

    def bind(self, update_shader_uniforms: bool = False ):
        self._shader.bind()
        if update_shader_uniforms:
            self._update_shader()
