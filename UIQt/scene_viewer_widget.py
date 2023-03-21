from PyQt5.QtGui import QOpenGLVersionProfile, QSurfaceFormat

from UIQt.GLUtilities.gl_camera import CameraGL
from UIQt.GLUtilities.gl_material import MaterialGL
from UIQt.GLUtilities.gl_mesh import MeshGL
from UIQt.GLUtilities.gl_shader import Shader
from UIQt.GLUtilities.gl_texture import TextureGL
from UIQt.GLUtilities.triangle_mesh import create_plane
from UIQt.Input.mouse_info import MouseInfo
from Utilities import Matrix4, Vector3, Transform
from collections import namedtuple
from PyQt5 import QtOpenGL
from typing import List
import OpenGL.GL as GL


currently_bounded_material = -1


class DrawCall(namedtuple('DrawCall', 'view, transform, material, mesh')):

    def __new__(cls, view: Matrix4, transform: Matrix4, material, mesh: MeshGL):
        return super().__new__(cls, view, transform, material, mesh)

    def __call__(self, *args, **kwargs):
        global currently_bounded_material
        if currently_bounded_material != self.material.unique_id:
            self.material.bind(True)
            currently_bounded_material = self.material.unique_id
        else:
            self.material.bind()
        self.material.shader.send_mat_4("view",      self.view)
        self.material.shader.send_mat_4("transform", self.transform)
        self.mesh.draw()


class SceneViewerWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self._main_camera: CameraGL = CameraGL()
        self._curr_view = self._main_camera.projection * self._main_camera.transform.transform_matrix
        self._mouse: MouseInfo = MouseInfo()
        self.parent = parent
        self._render_queue: List[DrawCall] = []
        QtOpenGL.QGLWidget.__init__(self, parent)

    def render_call(self, transform: Matrix4, material, mesh: MeshGL):
        self._render_queue.append(DrawCall(self._curr_view, transform, material, mesh))

    def initializeGL(self):
        self.fmt = QOpenGLVersionProfile()
        self.fmt.setVersion(3, 3)
        self.fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        print(f"GL version {GL.glGetString(GL.GL_VERSION)}")
        TextureGL.init_globals()
        Shader.init_globals()
        self._material  = MaterialGL()
        self._transform = Transform()
        self._model     = MeshGL(create_plane(0.9, 0.9))
        # self.glWidget.render_call(self._transform.transform_matrix, self._material, self._model)

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

    def paintGL(self):
        self.render_call(self._transform.transform_matrix, self._material, self._model)

        global currently_bounded_material
        currently_bounded_material = -1
        self._curr_view = self._main_camera.projection * self._main_camera.transform.transform_matrix
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        while len(self._render_queue) != 0:
            self._render_queue.pop()()
