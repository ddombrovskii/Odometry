from PyQt5.QtGui import QOpenGLVersionProfile, QSurfaceFormat, QMouseEvent, QWheelEvent

from UIQt.GLUtilities.gl_camera import CameraGL
from UIQt.GLUtilities.gl_material import MaterialGL
from UIQt.GLUtilities.gl_mesh import MeshGL
from UIQt.GLUtilities.gl_model import ModelGL
from UIQt.GLUtilities.gl_shader import Shader
from UIQt.GLUtilities.gl_texture import TextureGL
from UIQt.GLUtilities.triangle_mesh import create_plane, TrisMesh, read_obj_mesh, create_box
from UIQt.Input.mouse_info import MouseInfo
from Utilities.Geometry import Matrix4, Vector3, Transform
from collections import namedtuple
from PyQt5 import QtOpenGL
from typing import List
import OpenGL.GL as GL


currently_bounded_material = -1


class DrawCall(namedtuple('DrawCall', 'view, projection, cam_position, transform, material, mesh')):

    def __new__(cls, cam: CameraGL, model: ModelGL):
        return super().__new__(cls, cam.look_at_matrix, cam.projection, cam.transform.origin,
                               model.transform.transform_matrix, model.material, model.mesh)

    def __call__(self, *args, **kwargs):
        global currently_bounded_material
        if currently_bounded_material != self.material.unique_id:
            self.material.bind(True)
            currently_bounded_material = self.material.unique_id
        else:
            self.material.bind()
        self.material.shader.send_mat_4("view",         self.view)
        self.material.shader.send_mat_4("projection",   self.projection)
        self.material.shader.send_vec_3("cam_position", self.cam_position)
        self.material.shader.send_mat_4("model",        self.transform)
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
        #     print("non-cast")
        #     self._render_queue.append(DrawCall(cam, model))
        #     return
        # print("cast")
        self._render_queue.append(DrawCall(cam, model))

    def _get_opengl_info(self):
        return f"{{\n" \
               f"\t\"Vendor\":         \"{GL.glGetString(GL.GL_VENDOR).decode('utf-8')}\",\n" \
               f"\t\"Renderer\":       \"{GL.glGetString(GL.GL_RENDERER).decode('utf-8')}\",\n" \
               f"\t\"OpenGL Version\": \"{GL.glGetString(GL.GL_VERSION).decode('utf-8')}\",\n" \
               f"\t\"Shader Version\": \"{GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode('utf-8')}\"\n}}"

    def initializeGL(self):
        self.fmt = QOpenGLVersionProfile()
        self.fmt.setVersion(3, 3)
        self.fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        GL.glClearColor(125/255, 135/255, 145/255, 1)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        # GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        print(f"GL version {GL.glGetString(GL.GL_VERSION)}")
        print(self._get_opengl_info())
        Shader.init_globals()
        TextureGL.init_globals()
        MeshGL.init_globals()
        MaterialGL.init_globals()
        model_gl = ModelGL()
        self._main_camera.look_at(Vector3(0, 0, 0), Vector3(1, 1, 1))
        model_gl.mesh = MeshGL.SPHERE_MESH     # (create_box(0.9))
        model_gl.transform.scale = Vector3(2, 2, 2)
        self._scene_models.append(model_gl)
        # print(self._main_camera.projection)
        # print(self._main_camera.projection.invert())
        # print(self._main_camera.projection*self._main_camera.projection.invert())

        #model_gl = ModelGL()
        #model_gl.mesh = MeshGL.SPHERE_MESH  # (create_plane(2., 2.))
        #model_gl.transform.x = 1
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

    def clean_up(self) -> None:
        self.makeCurrent()
        TextureGL.delete_all_textures()
        Shader.delete_all_shaders()
        MeshGL.delete_all_meshes()
        self.doneCurrent()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._mouse.update_position(event.pos().x(), event.pos().y(), self.width(), self.height())
        self._mouse.update_state(-1)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._mouse.update_position(event.pos().x(), event.pos().y(), self.width(), self.height())
        self._mouse.update_state(event.button())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._mouse.update_position(event.pos().x(), event.pos().y(), self.width(), self.height())
        if self._mouse.is_left_button:
            self._main_camera.transform.angles += Vector3(self._mouse.y_delta, -self._mouse.x_delta, 0)
        if self._mouse.is_right_button:
            self._main_camera.transform.origin += \
                (self._main_camera.transform.up * -self._mouse.y_delta +
                 self._main_camera.transform.right * self._mouse.x_delta )

    def wheelEvent(self, event: QWheelEvent) -> None:
        # print(event.angleDelta())
        self._main_camera.transform.origin += self._main_camera.transform.front * event.angleDelta().y() / 120.0

    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)
        self._main_camera.aspect = float(height)/width
        # print(self._main_camera.projection)

    def updateGL(self) -> None:
        # self._main_camera.transform.angles += Vector3(0.005, 0.005, 0.005)
        for m in self._scene_models:
            # m.transform.angles += Vector3(0.005, 0.005, 0.005)
            self.render_call(self._main_camera, m)

    def paintGL(self):
        # GL.glClearColor(0.1, 0.2, 0.7, 0)
        global currently_bounded_material
        currently_bounded_material = -1
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        while len(self._render_queue) != 0:
            self._render_queue.pop()()
        self.swapBuffers()


