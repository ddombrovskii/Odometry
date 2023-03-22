from typing import Union, List
from Utilities import Color
from PIL.Image import Image
from OpenGL.GL import *
import numpy as np
# TODO texture_cube


class TextureGL:

    __textures_instances = {}

    WHITE_TEXTURE = None

    RED_TEXTURE = None

    GREEN_TEXTURE = None

    BLUE_TEXTURE = None

    PINK_TEXTURE = None

    GRAY_TEXTURE = None

    @staticmethod
    def init_globals():
        TextureGL.WHITE_TEXTURE = TextureGL(100, 100, Color(np.uint8(255), np.uint8(255), np.uint8(255)))

        TextureGL.RED_TEXTURE = TextureGL(100, 100, Color(np.uint8(255), np.uint8(0), np.uint8(0)))

        TextureGL.GREEN_TEXTURE = TextureGL(100, 100, Color(np.uint8(0), np.uint8(255), np.uint8(0)))

        TextureGL.BLUE_TEXTURE = TextureGL(100, 100, Color(np.uint8(0), np.uint8(0), np.uint8(255)))

        TextureGL.PINK_TEXTURE = TextureGL(100, 100, Color(np.uint8(255), np.uint8(0), np.uint8(255)))

        TextureGL.GRAY_TEXTURE = TextureGL(100, 100, Color(np.uint8(125), np.uint8(125), np.uint8(125)))

    @staticmethod
    def textures_enumerate():
        for texture in TextureGL.__textures_instances.items():
            yield texture[1]

    @staticmethod
    def textures_write(file, start="", end=""):
        file.write(f"{start}\"textures\":[\n")
        file.write(',\n'.join(str(m) for m in TextureGL.__textures_instances.values()))
        file.write(f"]\n{end}")

    @staticmethod
    def delete_all_textures():
        while len(TextureGL.__textures_instances) != 0:
            item = TextureGL.__textures_instances.popitem()
            item[1].delete_texture()

    def __init__(self, w: int = 16, h: int = 16, col: Color = Color(np.uint8(255), np.uint8(0), np.uint8(0)),
                 alpha=False):

        self.__source_file = "no-name"
        self.__width  = w
        self.__height = h
        self.__bpp = 4 if alpha else 3
        self.__id: int = 0
        self.__filtering_mode = (GL_LINEAR_MIPMAP_LINEAR, GL_LINEAR)
        self.__bind_target: GLenum = GL_TEXTURE_2D
        self.__warp_mode = GL_REPEAT
        self.__load_data(col)
        self.repeat()
        self.bi_linear()
        TextureGL.__textures_instances[self.__id] = self

    def __str__(self):
        return f"{{\n\t\"unique_id\":   {self.__id},\n" \
               f"\t\"asset_src\":   \"{self.source_file_path}\",\n" \
               f"\t\"width\":       {self.width},\n" \
               f"\t\"height\":      {self.height},\n" \
               f"\t\"bpp\":         {self.bpp},\n" \
               f"\t\"use_mip_map\": False,\n" \
               f"\t\"wrap_mode\":   {int(self.__warp_mode)},\n" \
               f"\t\"filter_mode\": [{int(self.__filtering_mode[0])},{int(self.__filtering_mode[1])}]\n}}"

    def __del__(self):
        pass # self.delete_texture()

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        glBindTexture(self.bind_target, 0)

    def __create(self):
        self.__id = glGenTextures(1)
        self.bind()
        self.repeat()
        self.bi_linear()

    def __load_data(self, resource: Union[Color, str]):

        if self.__id == 0:
            self.__create()
        else:
            self.delete_texture()
            self.__create()

        if self.texture_byte_size == 0:
            self.delete_texture()
            return

        TextureGL.__textures_instances[self.__id] = self

        if isinstance(resource, str):
            im = Image.open(resource)
            self.__width, self.__height = im.size
            pixel_data: List[np.uint8] = (np.asarray(im, dtype=np.uint8)).ravel()
            self.__bpp = int(len(pixel_data) / self.__width / self.__height)
        elif isinstance(resource, Color):
            pixel_data =  [resource[i % self.__bpp] for i in range(self.__width * self.__height * self.__bpp)]
        else:
            resource = (255, 0, 0, 0)
            pixel_data =  [resource[i % self.__bpp] for i in range(self.__width * self.__height * self.__bpp)]

        if self.bpp == 1:
            glTexImage2D(self.bind_target, 0, GL_R, self.width, self.height, 0,
                         GL_R, GL_UNSIGNED_BYTE, pixel_data)
            glGenerateMipmap(self.bind_target)
            return

        if self.bpp == 3:
            glTexImage2D(self.bind_target, 0, GL_RGB, self.width, self.height, 0,
                         GL_RGB, GL_UNSIGNED_BYTE, pixel_data)
            glGenerateMipmap(self.bind_target)
            return

        if self.bpp == 4:
            glTexImage2D(self.bind_target, 0, GL_RGBA, self.width, self.height, 0,
                         GL_RGBA, GL_UNSIGNED_BYTE, pixel_data)
            glGenerateMipmap(self.bind_target)

    @property
    def pixel_data(self) -> np.ndarray:
        return self.read_back_texture_data()

    @property
    def name(self) -> str:
        if len(self.__source_file) == 0:
            return ""
        name: List[str] = self.__source_file.split("\\")

        if len(name) == 0:
            return ""

        name = name[len(name) - 1].split(".")

        if len(name) == 0:
            return ""

        if len(name) < 2:
            return name[0]
        return name[len(name) - 2]

    @property
    def source_file_path(self) -> str:
        return self.__source_file

    @source_file_path.setter
    def source_file_path(self, path: str) -> None:
        if path == self.__source_file:
            return
        self.load(path)

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def bpp(self) -> int:
        return self.__bpp

    @property
    def texture_pixel_size(self) -> int:
        return self.__height * self.__width

    @property
    def texture_byte_size(self) -> int:
        return self.__bpp * self.__height * self.__width

    @property
    def bind_id(self) -> int:
        return self.__id

    @property
    def bind_target(self) -> GLenum:
        return self.__bind_target

    def repeat(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_T, GL_REPEAT)
        self.__warp_mode = GL_REPEAT

    def mirrored_repeat(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
        self.__warp_mode = GL_MIRRORED_REPEAT

    def clamp_to_edge(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        self.__warp_mode = GL_CLAMP_TO_EDGE

    def clamp_to_border(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(self.bind_target, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        self.__warp_mode = GL_CLAMP_TO_BORDER

    def nearest(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(self.bind_target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self.__filtering_mode = (GL_NEAREST, GL_LINEAR)

    def bi_linear(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(self.bind_target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self.__filtering_mode = (GL_LINEAR_MIPMAP_LINEAR, GL_LINEAR)

    def tri_linear(self):
        self.bind()
        glTexParameteri(self.bind_target, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(self.bind_target, GL_TEXTURE_MAG_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        self.__filtering_mode = (GL_LINEAR_MIPMAP_LINEAR, GL_LINEAR_MIPMAP_LINEAR)

    def bind(self):
        glBindTexture(self.bind_target, self.__id)

    def bind_to_channel(self, channel: int):
        glActiveTexture(GL_TEXTURE0 + channel)
        glBindTexture(self.bind_target, self.__id)

    def delete_texture(self):
        if self.__id == 0:
            return
        glDeleteTextures(1, (self.__id,))
        if self.__id in TextureGL.__textures_instances:
            del TextureGL.__textures_instances[self.__id]
        self.__id = 0

    def load(self, origin: str):
        self.__load_data(origin)

    def read_back_texture_data(self) -> np.ndarray:
        # todo check!
        self.bind()
        # b_data = np.zeros((1, elements_number), dtype=np.float32)
        b_data = glGetBufferSubData(self.__bind_target, 0, self.texture_byte_size)
        # print(b_data.astype('<f4'))
        if self.bind_target == GL_ELEMENT_ARRAY_BUFFER:
            return b_data.view('<i4')
        if self.bind_target == GL_ARRAY_BUFFER:
            return b_data.view('<f4')
        return b_data

