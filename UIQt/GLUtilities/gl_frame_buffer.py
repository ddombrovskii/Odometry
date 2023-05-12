from UIQt.GLUtilities.gl_decorators import gl_error_catch
from OpenGL.GL import *


class FrameBufferGL:
    RGB_F_ATTACHMENT: int = 0
    RGBA_F_ATTACHMENT: int = 1
    RGB_8_ATTACHMENT: int = 2
    RGBA_8_ATTACHMENT: int = 3

    _frame_buffers = {}

    _bounded_id = 0

    @staticmethod
    def bounded_id() -> int:
        return FrameBufferGL._bounded_id

    @staticmethod
    def enumerate():
        for texture in FrameBufferGL._frame_buffers.items():
            yield texture[1]

    @staticmethod
    def delete_all():
        while len(FrameBufferGL._frame_buffers) != 0:
            item = FrameBufferGL._frame_buffers.popitem()
            item[1].delete_buffer()

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
               FrameBufferGL._create_texture(GL_RGB16F, width, height, GL_RGB, GL_FLOAT, GL_NEAREST, sampling)

    @staticmethod
    def _create_rgba_f_tex(width: int, height: int, sampling: int = 0) -> (int, int):
        return FrameBufferGL.RGBA_F_ATTACHMENT, \
               FrameBufferGL._create_texture(GL_RGBA16F, width, height, GL_RGBA, GL_FLOAT, GL_NEAREST, sampling)

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
        self._attachment_id = GL_COLOR_ATTACHMENT0
        self._fbo: int = glGenFramebuffers(1)
        self._clear_color: (int, int, int) = (0, 0, 0)
        FrameBufferGL._frame_buffers[self.bind_id] = self

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
    def clear_color(self) -> (int, int, int):
        return self._clear_color

    @clear_color.setter
    def clear_color(self, rgb: (int, int, int)) -> None:
        self.bind()
        self._clear_color = rgb
        glClearColor(rgb[0], rgb[1], rgb[2])

    def clear_buffer(self) -> None:
        self.bind()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    @gl_error_catch
    def delete_buffer(self):
        glDeleteFramebuffers(1, (self.bind_id,))
        for key, (tex_type, tex_id) in self._texture_attachments.items():
            glDeleteTextures(1, (tex_id,))
        glDeleteRenderbuffers(1, (self._texture_depth_attachment,))
        if self.bind_id in FrameBufferGL._frame_buffers:
            del FrameBufferGL._frame_buffers[self.bind_id]

    @gl_error_catch
    def __create_depth(self) -> None:
        self._texture_depth_attachment = FrameBufferGL._create_depth_stencil(self._width, self._height, self.samples)
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")

    @gl_error_catch
    def __create_color_attachment_rgb_8(self) -> (int, int):
        tex_type, tex_id = FrameBufferGL._create_rgb_8_tex(self._width, self._height, self.samples)
        if self.is_multisampling:
            glFramebufferTexture2D(GL_FRAMEBUFFER, self._attachment_id, GL_TEXTURE_2D_MULTISAMPLE, tex_id, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, self._attachment_id, GL_TEXTURE_2D, tex_id, 0)
        self._draw_buffers.append(self._attachment_id)
        self._attachment_id += 1
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")
        return tex_type, tex_id

    @gl_error_catch
    def __create_color_attachment_rgba_8(self) -> (int, int):
        tex_type, tex_id = FrameBufferGL._create_rgba_8_tex(self._width, self._height, self.samples)
        if self.is_multisampling:
            glFramebufferTexture2D(GL_FRAMEBUFFER, self._attachment_id, GL_TEXTURE_2D_MULTISAMPLE, tex_id, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, self._attachment_id, GL_TEXTURE_2D, tex_id, 0)

        self._draw_buffers.append(self._attachment_id)
        self._attachment_id += 1
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")
        return tex_type, tex_id

    @gl_error_catch
    def __create_color_attachment_rgb_f(self) -> (int, int):
        tex_type, tex_id = FrameBufferGL._create_rgb_f_tex(self._width, self._height, self.samples)
        if self.is_multisampling:
            glFramebufferTexture2D(GL_FRAMEBUFFER, self._attachment_id, GL_TEXTURE_2D_MULTISAMPLE, tex_id, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, self._attachment_id, GL_TEXTURE_2D, tex_id, 0)

        self._draw_buffers.append(self._attachment_id)
        self._attachment_id += 1
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")
        return tex_type, tex_id

    @gl_error_catch
    def __create_color_attachment_rgba_f(self) -> (int, int):
        tex_type, tex_id = FrameBufferGL._create_rgba_f_tex(self._width, self._height, self.samples)
        if self.is_multisampling:
            glFramebufferTexture2D(GL_FRAMEBUFFER, self._attachment_id, GL_TEXTURE_2D_MULTISAMPLE, tex_id, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, self._attachment_id, GL_TEXTURE_2D, tex_id, 0)
        self._draw_buffers.append(self._attachment_id)
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
        glDrawBuffers(len(self._draw_buffers), tuple(self._draw_buffers))
        if not FrameBufferGL._check_for_errors():
            raise RuntimeError("FrameBuffer creation error!!!")

    def bind(self) -> None:
        if FrameBufferGL.bounded_id() == self.bind_id:
            return
        glViewport(0, 0, self.width, self.height)
        FrameBufferGL._bounded_id = self.bind_id
        glBindFramebuffer(GL_FRAMEBUFFER, self.bind_id)

    def unbind(self) -> None:
        FrameBufferGL._bounded_id = 0
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def bind_buffer_texture_to_point(self, id_: int = 0) -> None:
        attachment = GL_TEXTURE0 + id_
        for key, (tex_type, tex_id) in self._texture_attachments.items():
            glActiveTexture(attachment)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            attachment += 1

    def blit(self) -> None:
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.bind_id)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        glBlitFramebuffer(0, 0, self.width, self.height, 0, 0, self.width, self.height, GL_COLOR_BUFFER_BIT, GL_NEAREST)
        self.unbind()
        # glBindFramebuffer(GL_FRAMEBUFFER, 0)
        # glEnable(GL_STENCIL_TEST)
        # glEnable(GL_DEPTH_TEST)
        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        # gl_globals.FRAME_BUFFER_BLIT_SHADER.bind()
        # self.bind_buffer_texture_to_point()
        # gl_globals.PLANE_MESH.draw()
