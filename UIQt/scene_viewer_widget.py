from PyQt5.QtGui import QOpenGLVersionProfile, QSurfaceFormat

from UIQt.GLUtilities.gl_camera import CameraGL
from UIQt.GLUtilities.gl_material import MaterialGL
from UIQt.GLUtilities.gl_mesh import MeshGL
from UIQt.GLUtilities.gl_model import ModelGL
from UIQt.GLUtilities.gl_shader import Shader
from UIQt.GLUtilities.gl_texture import TextureGL
from UIQt.GLUtilities.triangle_mesh import create_plane, TrisMesh, read_obj_mesh
from UIQt.Input.mouse_info import MouseInfo
from Utilities import Matrix4, Vector3, Transform
from collections import namedtuple
from PyQt5 import QtOpenGL
from typing import List
import OpenGL.GL as GL


currently_bounded_material = -1


class DrawCall(namedtuple('DrawCall', 'view, projection, transform, material, mesh')):

    def __new__(cls, cam: CameraGL, model: ModelGL):
        return super().__new__(cls, cam.transform.transform_matrix, cam.projection,
                               model.transform.transform_matrix, model.material, model.mesh)

    def __call__(self, *args, **kwargs):
        global currently_bounded_material
        if currently_bounded_material != self.material.unique_id:
            self.material.bind(True)
            currently_bounded_material = self.material.unique_id
        else:
            self.material.bind()
        self.material.shader.send_mat_4("view",       self.view)
        self.material.shader.send_mat_4("projection", self.projection)
        self.material.shader.send_mat_4("transform",  self.transform)
        self.mesh.draw()


class SceneViewerWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self._main_camera: CameraGL = CameraGL()
        self._mouse: MouseInfo = MouseInfo()
        self.parent = parent
        self._render_queue: List[DrawCall] = []
        self._scene_models: List[ModelGL] = []
        self.fmt: QOpenGLVersionProfile = None

    def render_call(self, cam: CameraGL, model: ModelGL):
        # if cam.cast_object(model.mesh.bounds):
        #     self._render_queue.append(DrawCall(cam, model))
        self._render_queue.append(DrawCall(cam, model))

    def initializeGL(self):
        self.fmt = QOpenGLVersionProfile()
        self.fmt.setVersion(3, 3)
        self.fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        TextureGL.init_globals()
        Shader.init_globals()
        MeshGL.init_globals()
        MaterialGL.init_globals()
        print(f"GL version {GL.glGetString(GL.GL_VERSION)}")
        model_gl = ModelGL()
        model_gl.mesh = MeshGL(create_plane(0.9, 0.9))
        model_gl.transform.sx = 0.5
        self._scene_models.append(model_gl)

    def _load_model(self, src: str):
        # вызов по нажатию на кнопку или чего ещё
        try:
            tris_models: List[TrisMesh] = read_obj_mesh(src)
            for m in tris_models:
                model_gl = ModelGL()
                model_gl.mesh = MeshGL(m)
                self._scene_models.append(model_gl)
        except:
            pass

    def __del__(self):
        # НЕ РАБОТАЕТ.
        # Причина: GL контекст освобождается раньше функции __del__
        # Что делать?
        if not self.isValid():
            return
        TextureGL.delete_all_textures()
        Shader.delete_all_shaders()
        MeshGL.delete_all_meshes()

    def mousePressEvent(self, event):
        self._mouse.update_position(event.pos().x(), event.pos().y(), self.width(), self.height())
        self._mouse.update_state(event.buttons())

    def mouseMoveEvent(self, event):
        self._mouse.update_position(event.pos().x(), event.pos().y(), self.width(), self.height())
        if self._mouse.is_left_button:
            self._main_camera.transform.angles += Vector3(8 * self._mouse.y_delta, 8 * self._mouse.x_delta, 0)

    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)
        self._main_camera.aspect = width / float(height)

    def updateGL(self) -> None:
        for m in self._scene_models:
            self.render_call(self._main_camera, m)

    def paintGL(self):
        GL.glClearColor(0.1, 0.2, 0.7, 0)
        global currently_bounded_material
        currently_bounded_material = -1
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        while len(self._render_queue) != 0:
            self._render_queue.pop()()
