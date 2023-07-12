from .gl_objects_pool import ObjectsPoolGL
from .gl_decorators import gl_error_catch
from collections import namedtuple
from typing import Tuple, Dict
from PIL import Image
from OpenGL.GL import *


class FrameBufferAttachment(namedtuple("FrameBufferAttachment", "name, bind_id, location, gl_type")):
    def __new__(cls, name: str, bind_id, location: int, gl_type: int):
        return super().__new__(cls, name, bind_id, location, gl_type)

    @property
    def format(self):
        if self.gl_type == GL_RGB8 or self.gl_type == GL_RGB32F:
            return GL_RGB
        if self.gl_type == GL_RGBA8 or self.gl_type == GL_RGBA32F:
            return GL_RGBA
        return GL_R

    @property
    def data_type(self):
        if self.gl_type == GL_RGB8 or self.gl_type == GL_RGBA8:
            return GL_UNSIGNED_BYTE
        if self.gl_type == GL_RGB32F or self.gl_type == GL_RGBA32F:
            return GL_FLOAT
        return GL_UNSIGNED_BYTE

    def __str__(self):
        return f"{{\n" \
               f"\t\"name\"    : \"{self.name}\"," \
               f"\t\"bind_id\" : {self.bind_id}," \
               f"\t\"location\": {self.location}," \
               f"\t\"gl_type\" : {self.gl_type}" \
               f"\n}}"


class FrameBufferGL:
    COLOR_ATTACHMENTS = \
        {
            0: GL_COLOR_ATTACHMENT0,
            1: GL_COLOR_ATTACHMENT1,
            2: GL_COLOR_ATTACHMENT2,
            3: GL_COLOR_ATTACHMENT3,
            4: GL_COLOR_ATTACHMENT4,
            5: GL_COLOR_ATTACHMENT5,
            6: GL_COLOR_ATTACHMENT6,
            7: GL_COLOR_ATTACHMENT7,
            8: GL_COLOR_ATTACHMENT8,
            9: GL_COLOR_ATTACHMENT9,
            10: GL_COLOR_ATTACHMENT10,
            11: GL_COLOR_ATTACHMENT11
        }

    PIXEL_FORMAT_TO_LAYOUT =\
        {
            GL_RGB8: GL_RGB,
            GL_RGBA8: GL_RGBA,
            GL_RGB32F: GL_RGB,
            GL_RGBA32F: GL_RGBA,
        }
    frame_buffers = ObjectsPoolGL()

    MAIN_SCREEN_FRAME_BUFFER = "main-screen-frame-buffer"

    @staticmethod
    def get_main_frame_buffer():
        return FrameBufferGL.frame_buffers.get_by_name(FrameBufferGL.MAIN_SCREEN_FRAME_BUFFER)

    @staticmethod
    def _create_texture(in_format_: int, w_: int, h_: int, format_: int, type_: int, filtering_: int,
                        _sampling: int = 0) -> int:

        tex_id = glGenTextures(1)

        if _sampling != 0:
            glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, tex_id)
            glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, _sampling, in_format_, w_, h_, GL_TRUE)
            return tex_id

        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filtering_)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filtering_)
        glTexImage2D(GL_TEXTURE_2D, 0, in_format_, w_, h_, 0, format_, type_, None)
        return tex_id

    @staticmethod
    def _create_depth_stencil(width: int, height: int, _sampling: int = 0) -> int:
        tex_id = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, tex_id)
        if _sampling != 0:
            glRenderbufferStorageMultisample(GL_RENDERBUFFER, _sampling, GL_DEPTH24_STENCIL8, width, height)
        else:
            glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, tex_id)
        return tex_id

    @staticmethod
    def _create_depth_shadow(width: int, height: int, _sampling: int = 0) -> int:
        tex_id = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, tex_id)
        if _sampling != 0:
            glRenderbufferStorageMultisample(GL_RENDERBUFFER, _sampling, GL_DEPTH_COMPONENT32F, width, height)
        else:
            glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT32F, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, tex_id)
        return tex_id

    @staticmethod
    def _create_rgb_8_tex(width: int, height: int, sampling: int = 0) -> (int, int):
        return GL_RGB8, \
               FrameBufferGL._create_texture(GL_RGB8, width, height, GL_RGB, GL_UNSIGNED_BYTE, GL_NEAREST, sampling)

    @staticmethod
    def _create_rgba_8_tex(width: int, height: int, sampling: int = 0) -> (int, int):
        return GL_RGBA8, \
               FrameBufferGL._create_texture(GL_RGBA8, width, height, GL_RGBA, GL_UNSIGNED_BYTE, GL_NEAREST, sampling)

    @staticmethod
    def _create_rgb_f_tex(width: int, height: int, sampling: int = 0) -> (int, int):
        return GL_RGB32F, \
               FrameBufferGL._create_texture(GL_RGB32F, width, height, GL_RGB, GL_FLOAT, GL_NEAREST, sampling)

    @staticmethod
    def _create_rgba_f_tex(width: int, height: int, sampling: int = 0) -> (int, int):
        return GL_RGBA32F, \
               FrameBufferGL._create_texture(GL_RGBA32F, width, height, GL_RGBA, GL_FLOAT, GL_NEAREST, sampling)

    @staticmethod
    def _get_texture_size(tex_id):
        glBindTexture(GL_TEXTURE_2D, tex_id)
        return glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH), \
               glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT)

    @staticmethod
    def _check_for_errors():
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            return False
        return True

    def __init__(self, w: int = 800, h: int = 600):
        assert isinstance(w, int)
        assert isinstance(h, int)
        h = max(h, 10)
        w = max(w, 10)
        self._fbo: int = glGenFramebuffers(1)
        glClearColor(125 / 255, 135 / 255, 145 / 255, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self._fbo_depth_attachment = 0
        self._samples = 16
        self._width: int = w
        self._height: int = h
        self._fbo_attachments_by_id: Dict[int, FrameBufferAttachment] = {}
        self._fbo_attachments_by_name: Dict[str, FrameBufferAttachment] = {}
        self._name = f"frame_buffer_{self._fbo}"
        self._clear_color: Tuple[int, int, int] = (0, 0, 0)
        FrameBufferGL.frame_buffers.register_object(self)

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def __del__(self):
        self.delete()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not FrameBufferGL.frame_buffers.check_if_name_valid(value):
            return
        FrameBufferGL.frame_buffers.unregister_object(self)
        self._name = value
        FrameBufferGL.frame_buffers.register_object(self)

    @property
    def is_multisampled(self) -> bool:
        return self._samples != 0

    @property
    def samples(self) -> int:
        return self._samples

    @samples.setter
    def samples(self, samples: int) -> None:
        assert isinstance(samples, int)
        if samples not in {0, 4, 8, 16, 32}:
            return
        self._samples = samples

    @gl_error_catch
    def resize(self, w: int, h: int) -> None:
        assert isinstance(w, int)
        assert isinstance(h, int)
        while True:
            if w != self._width:
                break
            if h != self._height:
                break
            return
        self._width = w
        self._height = h
        attachments = {}

        for attachment in self._fbo_attachments_by_id.values():
            attachments.update({attachment.bind_id: attachment})
            glDeleteTextures(1, (attachment.bind_id,))

        self._fbo_attachments_by_id.clear()
        self._fbo_attachments_by_name.clear()

        for attachment in attachments.values():
            if attachment.gl_type == GL_RGB8:
                self.create_color_attachment_rgb_8(attachment.name)
                continue
            if attachment.gl_type == GL_RGBA8:
                self.create_color_attachment_rgba_8(attachment.name)
                continue
            if attachment.gl_type == GL_RGB32F:
                self.create_color_attachment_rgb_f(attachment.name)
                continue
            if attachment.gl_type == GL_RGBA32F:
                self.create_color_attachment_rgba_f(attachment.name)
                continue

        glDeleteRenderbuffers(1, (self._fbo_depth_attachment,))
        self._fbo_depth_attachment = 0
        self.create_depth()
        self.clear_buffer()

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def shape(self) -> Tuple[int, int]:
        return self.width, self.height

    @property
    def bind_id(self) -> int:
        return self._fbo

    @property
    def clear_color(self) -> Tuple[int, int, int]:
        return self._clear_color

    @clear_color.setter
    def clear_color(self, rgb: Tuple[int, int, int]) -> None:
        self.bind()
        self._clear_color = rgb
        glClearColor(rgb[0], rgb[1], rgb[2])

    def clear_buffer(self) -> None:
        self.bind()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    @gl_error_catch
    def delete(self):
        if self.bind_id == 0:
            return
        glDeleteFramebuffers(1, (self.bind_id,))
        for attachment in self._fbo_attachments_by_id.values():
            glDeleteTextures(1, (attachment.bind_id,))
        glDeleteRenderbuffers(1, (self._fbo_depth_attachment,))
        FrameBufferGL.frame_buffers.unregister_object(self)
        self._fbo = 0

    @gl_error_catch
    def __create_depth(self) -> None:
        self._fbo_depth_attachment = FrameBufferGL._create_depth_stencil(self._width, self._height, self.samples)
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")

    @gl_error_catch
    def __create_color_attachment_rgb_8(self, attachment_id: int):
        if attachment_id not in FrameBufferGL.COLOR_ATTACHMENTS:
            raise RuntimeError("FrameBufferGL::Exceed maximum amount of color attachments...")
        tex_type, tex_id = FrameBufferGL._create_rgb_8_tex(self._width, self._height, self.samples)
        tex_location = FrameBufferGL.COLOR_ATTACHMENTS[attachment_id]
        if self.is_multisampled:
            glFramebufferTexture2D(GL_FRAMEBUFFER, tex_location, GL_TEXTURE_2D_MULTISAMPLE, tex_id, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, tex_location, GL_TEXTURE_2D, tex_id, 0)
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")
        return tex_type, tex_id, tex_location

    @gl_error_catch
    def __create_color_attachment_rgba_8(self, attachment_id: int):
        if attachment_id not in FrameBufferGL.COLOR_ATTACHMENTS:
            raise RuntimeError("FrameBufferGL::Exceed maximum amount of color attachments...")
        tex_type, tex_id = FrameBufferGL._create_rgba_8_tex(self._width, self._height, self.samples)
        tex_location = FrameBufferGL.COLOR_ATTACHMENTS[attachment_id]
        if self.is_multisampled:
            glFramebufferTexture2D(GL_FRAMEBUFFER, tex_location, GL_TEXTURE_2D_MULTISAMPLE, tex_id, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, tex_location, GL_TEXTURE_2D, tex_id, 0)
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")
        return tex_type, tex_id, tex_location

    @gl_error_catch
    def __create_color_attachment_rgb_f(self, attachment_id: int):
        if attachment_id not in FrameBufferGL.COLOR_ATTACHMENTS:
            raise RuntimeError("FrameBufferGL::Exceed maximum amount of color attachments...")
        tex_type, tex_id = FrameBufferGL._create_rgb_f_tex(self._width, self._height, self.samples)
        tex_location = FrameBufferGL.COLOR_ATTACHMENTS[attachment_id]
        if self.is_multisampled:
            glFramebufferTexture2D(GL_FRAMEBUFFER, tex_location, GL_TEXTURE_2D_MULTISAMPLE, tex_id, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, tex_location, GL_TEXTURE_2D, tex_id, 0)
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")
        return tex_type, tex_id, tex_location

    @gl_error_catch
    def __create_color_attachment_rgba_f(self, attachment_id: int):
        if attachment_id not in FrameBufferGL.COLOR_ATTACHMENTS:
            raise RuntimeError("FrameBufferGL::Exceed maximum amount of color attachments...")
        tex_type, tex_id = FrameBufferGL._create_rgba_f_tex(self._width, self._height, self.samples)
        tex_location = FrameBufferGL.COLOR_ATTACHMENTS[attachment_id]
        if self.is_multisampled:
            glFramebufferTexture2D(GL_FRAMEBUFFER, tex_location, GL_TEXTURE_2D_MULTISAMPLE, tex_id, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, tex_location, GL_TEXTURE_2D, tex_id, 0)
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")
        return tex_type, tex_id, tex_location

    def create_depth(self) -> None:
        if self._fbo_depth_attachment != 0:
            return
        self.bind()
        self.__create_depth()

    def create_color_attachment_rgb_8(self, attachment_name: str) -> None:
        if attachment_name in self._fbo_attachments_by_name:
            return
        self.bind()
        self.__create_color_attachment_rgb_8()
        t_type, t_id, t_location = self.__create_color_attachment_rgb_8(len(self._fbo_attachments_by_id))
        attachment = FrameBufferAttachment(attachment_name, t_id, t_location, t_type)
        self._fbo_attachments_by_id.update({attachment.bind_id: attachment})
        self._fbo_attachments_by_name.update({attachment.name: attachment})

    def create_color_attachment_rgba_8(self, attachment_name: str) -> None:
        if attachment_name in self._fbo_attachments_by_name:
            return
        self.bind()
        t_type, t_id, t_location = self.__create_color_attachment_rgba_8(len(self._fbo_attachments_by_id))
        attachment = FrameBufferAttachment(attachment_name, t_id, t_location, t_type)
        self._fbo_attachments_by_id.update({attachment.bind_id: attachment})
        self._fbo_attachments_by_name.update({attachment.name: attachment})

    def create_color_attachment_rgb_f(self, attachment_name: str) -> None:
        if attachment_name in self._fbo_attachments_by_name:
            return
        self.bind()
        t_type, t_id, t_location = self.__create_color_attachment_rgb_f(len(self._fbo_attachments_by_id))
        attachment = FrameBufferAttachment(attachment_name, t_id, t_location, t_type)
        self._fbo_attachments_by_id.update({attachment.bind_id: attachment})
        self._fbo_attachments_by_name.update({attachment.name: attachment})

    def create_color_attachment_rgba_f(self, attachment_name: str) -> None:
        if attachment_name in self._fbo_attachments_by_name:
            return
        self.bind()
        t_type, t_id, t_location = self.__create_color_attachment_rgba_f(len(self._fbo_attachments_by_id))
        attachment = FrameBufferAttachment(attachment_name, t_id, t_location, t_type)
        self._fbo_attachments_by_id.update({attachment.bind_id: attachment})
        self._fbo_attachments_by_name.update({attachment.name: attachment})

    def validate(self):
        self.bind()
        glDrawBuffers(len(self._fbo_attachments_by_id), *(v.location for v in self._fbo_attachments_by_id.values()))
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")

    def bind(self) -> None:
        if not FrameBufferGL.frame_buffers.bounded_update(self.bind_id):
            return
        glBindFramebuffer(GL_FRAMEBUFFER, self.bind_id)
        glViewport(0, 0, self.width, self.height)

    def unbind(self) -> None:
        FrameBufferGL.frame_buffers.bounded_update(0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def bind_buffer_texture_to_point(self, id_: int = 0) -> None:
        attachment_0 = GL_TEXTURE0 + id_
        if self.is_multisampled:
            for attachment_id, attachment in enumerate(self._fbo_attachments_by_id.values()):
                glActiveTexture(attachment_0 + attachment_id)
                glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, attachment.bind_id)
                attachment += 1
            return
        for attachment_id, attachment in enumerate(self._fbo_attachments_by_id.values()):
            glActiveTexture(attachment_0 + attachment_id)
            glBindTexture(GL_TEXTURE_2D, attachment.bind_id)
            attachment += 1

    def _read_buffer_attachment(self, attachment_name: str, x0: int, y0: int, width: int, height: int):
        # reading from multisampled FBO not allowed (((
        if attachment_name not in self._fbo_attachments_by_name:
            self.unbind()
            return glReadPixels(x0, y0, width, height, GL_RGB, GL_UNSIGNED_BYTE)

        if not self.is_multisampled:
            # self.bind()
            # glBindFramebuffer(GL_READ_FRAMEBUFFER, self.bind_id)
            attachment = self._fbo_attachments_by_name[attachment_name]
            glReadBuffer(attachment.location)
            frame = glReadPixels(x0, y0, width, height, attachment.format, attachment.data_type)
            self.unbind()
            return frame

        self.unbind()
        return glReadPixels(x0, y0, width, height, GL_RGB, GL_UNSIGNED_BYTE)

    def _read_buffer_depth_attachment(self, x0: int, y0: int, width: int, height: int):
        if self._fbo_depth_attachment == 0:
            return
        self.bind()
        frame = glReadPixels(x0, y0, width, height, GL_RGBA, GL_FLOAT)
        self.unbind()
        return frame

    def _read_buffer_stencil_attachment(self, x0: int, y0: int, width: int, height: int):
        if self._fbo_depth_attachment == 0:
            return
        self.bind()
        frame = glReadPixels(x0, y0, width, height, GL_STENCIL_ATTACHMENT, GL_FLOAT)
        self.unbind()
        return frame

    @gl_error_catch
    def read_depth_pixel(self, x0: int, y0: int) -> float:
        if self.is_multisampled:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            frame = glReadPixels(x0, y0, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)
            return frame
        if self._fbo_depth_attachment == 0:
            return 0.0
        with self:
            return glReadPixels(x0, y0, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)

    @gl_error_catch
    def read_pixel(self,  x0: int, y0: int, text_attachment: str = "attachment_0"):
        return self._read_buffer_attachment(text_attachment, x0,  y0, x0 + 1, y0 + 1)

    @gl_error_catch
    def grab_snap_shot(self, text_attachment: str = "attachment_0"):
        pixels = self._read_buffer_attachment(text_attachment, 0, 0, self.width, self.height)
        if pixels is None:
            return
        bpp = len(pixels) // self.width // self.height
        if bpp == 4:
            image = Image.frombytes('RGBA', (self.width, self.height), pixels)
        elif bpp == 3:
            image = Image.frombytes('RGB', (self.width, self.height), pixels)
        elif bpp == 1:
            image = Image.frombytes('L', (self.width, self.height), pixels)
        else:
            raise ValueError()

        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        return image
        # image.save(path)

    @gl_error_catch
    def grab_depth_snap_shot(self, path: str = "depth_snap_shot.bmp"):
        pixels = self._read_buffer_depth_attachment(0, 0, self.width, self.height)
        depth = Image.frombytes('RGB', (self.width, self.height), pixels)
        depth = depth.transpose(Image.FLIP_TOP_BOTTOM)
        depth.save(path)

    def blit(self) -> None:
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.bind_id)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        glBlitFramebuffer(0, 0, self.width, self.height, 0, 0, self.width, self.height, GL_COLOR_BUFFER_BIT, GL_NEAREST)
        glBlitFramebuffer(0, 0, self.width, self.height, 0, 0, self.width, self.height, GL_DEPTH_BUFFER_BIT, GL_NEAREST)
        glBlitFramebuffer(0, 0, self.width, self.height, 0, 0, self.width, self.height, GL_STENCIL_BUFFER_BIT, GL_NEAREST)
        self.unbind()


    # https://www.programcreek.com/python/example/8811/PIL.Image.fromstring
    # https://gist.github.com/yuyu2172/95e406260b2497c4d4c4948f18de827d
    # https://github.com/trevorvanhoof/sqrmelon/blob/76df51c2cf936cbb9be8b6cf45f19b2497758c9f/SqrMelon/buffers.py#L120
    # https://python.hotexamples.com/examples/OpenGL/GL/glReadPixels/python-gl-glreadpixels-method-examples.html
    # http://www.opengl-tutorial.org/miscellaneous/clicking-on-objects/picking-with-an-opengl-hack/
    # https://ogldev.org/www/tutorial29/tutorial29.html
