from typing import Tuple

from OpenGL.GL.VERSION import GL_1_1
from PIL import Image

from UIQt.GLUtilities.gl_decorators import gl_error_catch
from UIQt.GLUtilities.objects_pool import ObjectsPool
from OpenGL.GL import *


class FrameBufferGL:
    COLOR_ATTACHMENTS = \
        {0: GL_COLOR_ATTACHMENT0,
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
         11: GL_COLOR_ATTACHMENT11}
    RGB_F_ATTACHMENT: int = 0
    RGBA_F_ATTACHMENT: int = 1
    RGB_8_ATTACHMENT: int = 2
    RGBA_8_ATTACHMENT: int = 3

    frame_buffers = ObjectsPool()

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
        return FrameBufferGL.RGB_8_ATTACHMENT, \
               FrameBufferGL._create_texture(GL_RGB8, width, height, GL_RGB, GL_UNSIGNED_BYTE, GL_NEAREST, sampling)

    @staticmethod
    def _create_rgba_8_tex(width: int, height: int, sampling: int = 0) -> (int, int):
        return FrameBufferGL.RGBA_8_ATTACHMENT, \
               FrameBufferGL._create_texture(GL_RGBA8, width, height, GL_RGBA, GL_UNSIGNED_BYTE, GL_NEAREST, sampling)

    @staticmethod
    def _create_rgb_f_tex(width: int, height: int, sampling: int = 0) -> (int, int):
        return FrameBufferGL.RGB_F_ATTACHMENT, \
               FrameBufferGL._create_texture(GL_RGB32F, width, height, GL_RGB, GL_FLOAT, GL_NEAREST, sampling)

    @staticmethod
    def _create_rgba_f_tex(width: int, height: int, sampling: int = 0) -> (int, int):
        return FrameBufferGL.RGBA_F_ATTACHMENT, \
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

    def __init__(self, w=800, h=600):
        self._multisampling = 16
        self._width: int = w
        self._height: int = h
        self._texture_attachments = {}
        self._draw_buffers = []
        self._texture_depth_attachment = 0
        self._attachment_id = 0
        self._fbo: int = glGenFramebuffers(1)
        self._name = f"frame_buffer_{self._fbo}"
        self._clear_color: Tuple[int, int, int] = (0, 0, 0)
        FrameBufferGL.frame_buffers.register_object(self)

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_multisampling(self) -> bool:
        return self._multisampling != 0

    @property
    def samples(self) -> int:
        return self._multisampling

    @gl_error_catch
    def resize(self, w: int, h: int) -> None:
        while True:
            if w != self._width:
                break
            if h != self._height:
                break
            return
        self._attachment_id = GL_COLOR_ATTACHMENT0

        self._draw_buffers.clear()

        self._width = w

        self._height = h

        attachments = {}

        for key, (tex_type, tex_id) in self._texture_attachments.items():
            attachments.update({key: tex_type})
            glDeleteTextures(1, (tex_id,))

        self._texture_attachments.clear()

        for key, value in attachments.items():
            if value == FrameBufferGL.RGB_8_ATTACHMENT:
                self.create_color_attachment_rgb_8(key)
                continue
            if value == FrameBufferGL.RGBA_8_ATTACHMENT:
                self.create_color_attachment_rgba_8(key)
                continue
            if value == FrameBufferGL.RGB_F_ATTACHMENT:
                self.create_color_attachment_rgb_f(key)
                continue
            if value == FrameBufferGL.RGBA_F_ATTACHMENT:
                self.create_color_attachment_rgba_f(key)
                continue
        glDeleteRenderbuffers(1, (self._texture_depth_attachment,))
        self._texture_depth_attachment = 0
        self.create_depth()
        self.clear_buffer()

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

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
        glDeleteFramebuffers(1, (self.bind_id,))
        for key, (tex_type, tex_id) in self._texture_attachments.items():
            glDeleteTextures(1, (tex_id,))
        glDeleteRenderbuffers(1, (self._texture_depth_attachment,))
        FrameBufferGL.frame_buffers.unregister_object(self)

    @gl_error_catch
    def __create_depth(self) -> None:
        self._texture_depth_attachment = FrameBufferGL._create_depth_stencil(self._width, self._height, self.samples)
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")

    @gl_error_catch
    def __create_color_attachment_rgb_8(self) -> Tuple[int, int]:
        tex_type, tex_id = FrameBufferGL._create_rgb_8_tex(self._width, self._height, self.samples)
        if self._attachment_id not in FrameBufferGL.COLOR_ATTACHMENTS:
            raise RuntimeError("FrameBufferGL::Exceed maximum amount of color attachments...")
        attachment = FrameBufferGL.COLOR_ATTACHMENTS[self._attachment_id]
        if self.is_multisampling:
            glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, GL_TEXTURE_2D_MULTISAMPLE, tex_id, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, GL_TEXTURE_2D, tex_id, 0)
        self._draw_buffers.append(attachment)
        self._attachment_id += 1
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")
        return tex_type, tex_id

    @gl_error_catch
    def __create_color_attachment_rgba_8(self) -> Tuple[int, int]:
        tex_type, tex_id = FrameBufferGL._create_rgba_8_tex(self._width, self._height, self.samples)
        if self._attachment_id not in FrameBufferGL.COLOR_ATTACHMENTS:
            raise RuntimeError("FrameBufferGL::Exceed maximum amount of color attachments...")
        attachment = FrameBufferGL.COLOR_ATTACHMENTS[self._attachment_id]
        if self.is_multisampling:
            glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, GL_TEXTURE_2D_MULTISAMPLE, tex_id, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, GL_TEXTURE_2D, tex_id, 0)
        self._draw_buffers.append(attachment)
        self._attachment_id += 1
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")
        return tex_type, tex_id

    @gl_error_catch
    def __create_color_attachment_rgb_f(self) -> Tuple[int, int]:
        tex_type, tex_id = FrameBufferGL._create_rgb_f_tex(self._width, self._height, self.samples)
        if self._attachment_id not in FrameBufferGL.COLOR_ATTACHMENTS:
            raise RuntimeError("FrameBufferGL::Exceed maximum amount of color attachments...")
        attachment = FrameBufferGL.COLOR_ATTACHMENTS[self._attachment_id]
        if self.is_multisampling:
            glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, GL_TEXTURE_2D_MULTISAMPLE, tex_id, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, GL_TEXTURE_2D, tex_id, 0)

        self._draw_buffers.append(attachment)
        self._attachment_id += 1
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")
        return tex_type, tex_id

    @gl_error_catch
    def __create_color_attachment_rgba_f(self) -> Tuple[int, int]:
        tex_type, tex_id = FrameBufferGL._create_rgba_f_tex(self._width, self._height, self.samples)
        if self._attachment_id not in FrameBufferGL.COLOR_ATTACHMENTS:
            raise RuntimeError("FrameBufferGL::Exceed maximum amount of color attachments...")
        attachment = FrameBufferGL.COLOR_ATTACHMENTS[self._attachment_id]
        if self.is_multisampling:
            glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, GL_TEXTURE_2D_MULTISAMPLE, tex_id, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, GL_TEXTURE_2D, tex_id, 0)
        self._draw_buffers.append(attachment)
        self._attachment_id += 1
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")
        return tex_type, tex_id

    def create_depth(self) -> None:
        if self._texture_depth_attachment != 0:
            return
        self.bind()
        self.__create_depth()

    def create_color_attachment_rgb_8(self, attachment_name: str) -> None:
        if attachment_name in self._texture_attachments:
            return
        self.bind()
        self._texture_attachments.update({attachment_name: self.__create_color_attachment_rgb_8()})

    def create_color_attachment_rgba_8(self, attachment_name: str) -> None:
        if attachment_name in self._texture_attachments:
            return
        self.bind()
        self._texture_attachments.update({attachment_name: self.__create_color_attachment_rgba_8()})

    def create_color_attachment_rgb_f(self, attachment_name: str) -> None:
        if attachment_name in self._texture_attachments:
            return
        self.bind()
        self._texture_attachments.update({attachment_name: self.__create_color_attachment_rgb_f()})

    def create_color_attachment_rgba_f(self, attachment_name: str) -> None:
        if attachment_name in self._texture_attachments:
            return
        self.bind()
        self._texture_attachments.update({attachment_name: self.__create_color_attachment_rgba_f()})

    def validate(self):
        buffers_count = len(self._draw_buffers)
        buffers_draw = tuple(self._draw_buffers)
        glDrawBuffers(buffers_count, buffers_draw)
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")

    def bind(self) -> None:
        if not FrameBufferGL.frame_buffers.bounded_update(self.bind_id):
            return
        glViewport(0, 0, self.width, self.height)
        glBindFramebuffer(GL_FRAMEBUFFER, self.bind_id)

    def unbind(self) -> None:
        FrameBufferGL.frame_buffers.bounded_update(0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def bind_buffer_texture_to_point(self, id_: int = 0) -> None:
        attachment = GL_TEXTURE0 + id_
        if self.is_multisampling:
            for key, (tex_type, tex_id) in self._texture_attachments.items():
                glActiveTexture(attachment)
                glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, tex_id)
                attachment += 1
            return
        for key, (tex_type, tex_id) in self._texture_attachments.items():
            glActiveTexture(attachment)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            attachment += 1

    def _read_buffer_attachment(self, attachment_id: int, x0: int, y0: int, width: int, height: int):
        if attachment_id not in FrameBufferGL.COLOR_ATTACHMENTS:
            return None
        self.bind()
        glReadBuffer(FrameBufferGL.COLOR_ATTACHMENTS[attachment_id])
        frame = glReadPixels(x0, y0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
        self.unbind()
        return frame

    def _read_buffer_depth_attachment(self, x0: int, y0: int, width: int, height: int):
        if self._texture_depth_attachment == 0:
            return
        self.bind()
        frame = glReadPixels(x0, y0, width, height, GL_DEPTH_COMPONENT, GL_FLOAT)
        self.unbind()
        return frame

    def _read_buffer_stencil_attachment(self, x0: int, y0: int, width: int, height: int):
        if self._texture_depth_attachment == 0:
            return
        self.bind()
        frame = glReadPixels(x0, y0, width, height, GL_STENCIL_ATTACHMENT, GL_FLOAT)
        self.unbind()
        return frame

    @gl_error_catch
    def grab_snap_shot(self):
        pixels = self._read_buffer_attachment(0, 0, 0, self.width, self.height)
        if pixels is None:
            return
        image = Image.frombytes('RGB', (self.width, self.height), pixels)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image.save("snap_shot.png")

    @gl_error_catch
    def grab_depth_snap_shot(self):
        pixels = self._read_buffer_depth_attachment(0, 0, self.width, self.height)
        depth = Image.frombytes('RGB', (self.width, self.height), pixels)
        depth = depth.transpose(Image.FLIP_TOP_BOTTOM)
        depth.save("depth_snap_shot.bmp")

    def blit(self) -> None:
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.bind_id)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        glBlitFramebuffer(0, 0, self.width, self.height, 0, 0, self.width, self.height, GL_COLOR_BUFFER_BIT, GL_NEAREST)
        self.unbind()
    # https://www.programcreek.com/python/example/8811/PIL.Image.fromstring
    # https://gist.github.com/yuyu2172/95e406260b2497c4d4c4948f18de827d
    # https://github.com/trevorvanhoof/sqrmelon/blob/76df51c2cf936cbb9be8b6cf45f19b2497758c9f/SqrMelon/buffers.py#L120
    # https://python.hotexamples.com/examples/OpenGL/GL/glReadPixels/python-gl-glreadpixels-method-examples.html
    # http://www.opengl-tutorial.org/miscellaneous/clicking-on-objects/picking-with-an-opengl-hack/
    # https://ogldev.org/www/tutorial29/tutorial29.html
