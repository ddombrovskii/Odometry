from UIQt.GLUtilities.gl_decorators import gl_error_catch
from UIQt.GLUtilities.objects_pool import ObjectsPool
from typing import Union, List
from Utilities import Color
from OpenGL.GL import *
from PIL import Image
import numpy as np
# TODO texture_cube


class TextureGL:

    textures = ObjectsPool()

    def __init__(self, w: int = 16, h: int = 16, col: Color = Color(np.uint8(255), np.uint8(0), np.uint8(0)),
                 alpha=False):

        self._source_file = "no-name"
        self._name = "no-name"
        self._width: int = w
        self._height: int = h
        self._bpp: int = 4 if alpha else 3
        self._id: int = 0
        self._filtering_mode = (GL_LINEAR_MIPMAP_LINEAR, GL_LINEAR)
        self._bind_target: GLenum = GL_TEXTURE_2D
        self._warp_mode = GL_REPEAT
        self._load_data(col)
        self.repeat()
        self.bi_linear()
        TextureGL.textures.register_object(self)

    def __repr__(self):
        return f"{{\n" \
               f"\t\"name\":        \"{self.name}\",\n" \
               f"\t\"asset_src\":   \"{self.source_file_path}\",\n" \
               f"\t\"bind_id\":     {self.bind_id},\n" \
               f"\t\"width\":       {self.width},\n" \
               f"\t\"height\":      {self.height},\n" \
               f"\t\"bpp\":         {self.bpp},\n" \
               f"\t\"use_mip_map\": False,\n" \
               f"\t\"wrap_mode\":   {int(self._warp_mode)},\n" \
               f"\t\"filter_mode\": [{int(self._filtering_mode[0])},{int(self._filtering_mode[1])}]\n}}"

    def __str__(self):
        # todo:
        # "mip_map": 0,
        # "tex_type": 123,
        # "tex_warp": 123,
        # "tex_filt": [123, 123]
        return f"{{\n" \
               f"\t\"tex_name\"   :\"{self.name}\",\n" \
               f"\t\"tex_source\" :\"{self.source_file_path}\"" \
               f"\n}}"

    def __del__(self):
        self.delete()

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        glBindTexture(self.bind_target, 0)
        TextureGL._bounded_id = 0

    def _create(self):
        self._id = glGenTextures(1)
        self.bind()
        self.repeat()
        self.bi_linear()

    @gl_error_catch
    def _load_data(self, resource: Union[Color, str]):

        if self._id == 0:
            self._create()
        else:
            self.delete()
            self._create()

        if self.texture_byte_size == 0:
            self.delete()
            return
        if isinstance(resource, str):
            if self.source_file_path == resource:
                return
            im = Image.open(resource)
            self._source_file = resource
            _name: List[str] = self._source_file.split("/")
            _name = _name[-1].split(".")
            self._name = _name[0] if len(_name) < 2 else _name[-2]
            self._width, self._height = im.size
            pixel_data = (np.asarray(im, dtype=np.uint8)).ravel()
            self._bpp = pixel_data.size // self.width // self.height

        elif isinstance(resource, Color):
            self._name = f"gl_texture_{self.bind_id}"
            pixel_data = [resource[i % self.bpp] for i in range(self.width * self.height * self.bpp)]

        else:
            self._name = f"gl_texture_{self.bind_id}"
            resource = (255, 0, 0, 0)
            pixel_data = [resource[i % self.bpp] for i in range(self.width * self.height * self.bpp)]

        if self.bpp == 1:
            if im.format == 'PNG':
                glTexImage2D(self.bind_target, 0, GL_LUMINANCE8, self.width, self.height, 0, GL_LUMINANCE8,
                             GL_UNSIGNED_BYTE, pixel_data)
                glGenerateMipmap(self.bind_target)
                return
            glTexImage2D(self.bind_target, 0, GL_LUMINANCE8, self.width, self.height, 0, GL_LUMINANCE8,
                         GL_UNSIGNED_BYTE, pixel_data)
            glGenerateMipmap(self.bind_target)
            return

        if self.bpp == 3:
            glTexImage2D(self.bind_target, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, pixel_data)
            glGenerateMipmap(self.bind_target)
            return

        if self.bpp == 4:
            glTexImage2D(self.bind_target, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixel_data)
            glGenerateMipmap(self.bind_target)

    @property
    def pixel_data(self) -> np.ndarray:
        return self.read_back_texture_data()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        TextureGL.textures.unregister_object(self)
        self._name = value if value != "" else self._name
        TextureGL.textures.register_object(self)

    @property
    def source_file_path(self) -> str:
        return self._source_file

    @source_file_path.setter
    def source_file_path(self, path: str) -> None:
        if path == self.source_file_path:
            return
        self.load(path)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def bpp(self) -> int:
        return self._bpp

    @property
    def texture_pixel_size(self) -> int:
        return self._height * self._width

    @property
    def texture_byte_size(self) -> int:
        return self._bpp * self.texture_pixel_size

    @property
    def bind_id(self) -> int:
        return self._id

    @property
    def bind_target(self) -> GLenum:
        return self._bind_target

    def repeat(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_T, GL_REPEAT)
        self._warp_mode = GL_REPEAT

    def mirrored_repeat(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
        self._warp_mode = GL_MIRRORED_REPEAT

    def clamp_to_edge(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        self._warp_mode = GL_CLAMP_TO_EDGE

    def clamp_to_border(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        self._warp_mode = GL_CLAMP_TO_BORDER

    def nearest(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(self.bind_target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self._filtering_mode = (GL_NEAREST, GL_LINEAR)

    def bi_linear(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(self.bind_target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self._filtering_mode = (GL_LINEAR_MIPMAP_LINEAR, GL_LINEAR)

    def tri_linear(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(self.bind_target, GL_TEXTURE_MAG_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        self._filtering_mode = (GL_LINEAR_MIPMAP_LINEAR, GL_LINEAR_MIPMAP_LINEAR)

    def bind(self):
        if TextureGL.textures.bounded_update(self.bind_id):
            glBindTexture(self.bind_target, self.bind_id)

    def unbind(self):
        glBindTexture(self.bind_target, 0)
        TextureGL.textures.bounded_update(0)

    def bind_to_channel(self, channel: int):
        glActiveTexture(GL_TEXTURE0 + channel)
        glBindTexture(self.bind_target, self.bind_id)

    @gl_error_catch
    def delete(self):
        if self._id == 0:
            return
        glDeleteTextures(1, (self.bind_id,))
        TextureGL.textures.unregister_object(self)
        self._id = 0

    def load(self, origin: str):
        TextureGL.textures.unregister_object(self)
        self._load_data(origin)
        TextureGL.textures.register_object(self)

    @gl_error_catch
    def read_back_texture_data(self) -> np.ndarray:
        # todo check!
        self.bind()  # _to_channel(0)
        data = None
        if self.bpp == 1:
            data = glGetTexImage(self.bind_target, 0, GL_R, GL_UNSIGNED_BYTE)
        if self.bpp == 3:
            data = glGetTexImage(self.bind_target, 0, GL_RGB, GL_UNSIGNED_BYTE)
        if self.bpp == 4:
            data = glGetTexImage(self.bind_target, 0, GL_RGBA, GL_UNSIGNED_BYTE)
        return data

    def save_texture(self, file_path: str) -> bool:
        data = self.read_back_texture_data()

        if data is None:
            return False
        try:
            image = None
            if self.bpp == 1:
                image = Image.frombytes('L', (self.width, self.height), data)
            if self.bpp == 3:
                image = Image.frombytes('RGB', (self.width, self.height), data)
            if self.bpp == 4:
                image = Image.frombytes('RGBA', (self.width, self.height), data)
            if image is None:
                return False
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image.save(file_path)
            return True
        except Exception as _ex:
            print(f"save_texture {self.name} to file {file_path} error...\n {_ex.args}")
            return False
