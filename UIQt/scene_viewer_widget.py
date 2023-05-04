import math

from OpenGL.GL.shaders import GL_TRUE
from PyQt5.QtGui import QOpenGLVersionProfile, QSurfaceFormat, QMouseEvent, QWheelEvent
from UIQt.GLUtilities.triangle_mesh import TrisMesh, read_obj_mesh, poly_strip
from Utilities.Geometry import Vector3, Transform, BoundingBox, Vector2
from UIQt.GLUtilities.gl_camera import CameraGL
from UIQt.GLUtilities.gl_model import ModelGL
from UIQt.Input.mouse_info import MouseInfo
from UIQt.GLUtilities.gl_mesh import MeshGL
from UIQt.GLUtilities import gl_globals
from collections import namedtuple
from PyQt5 import QtOpenGL
from typing import List
import OpenGL.GL as GL


class DrawCall(namedtuple('DrawCall', 'view, projection, cam_position, transform, material, mesh')):

    def __new__(cls, cam: CameraGL, model: ModelGL):
        return super().__new__(cls, cam.look_at_matrix, cam.projection, cam.transform.origin,
                               model.transform.transform_matrix, model.material, model.mesh)

    def __call__(self, *args, **kwargs):
        self.material.bind()
        self.material.shader.send_mat_4("view",         self.view)
        self.material.shader.send_mat_4("projection",   self.projection)
        self.material.shader.send_vec_3("cam_position", self.cam_position)
        self.material.shader.send_mat_4("model",        self.transform, GL_TRUE)
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

    @staticmethod
    def _get_opengl_info():
        return f"{{\n" \
               f"\t\"Vendor\":         \"{GL.glGetString(GL.GL_VENDOR).decode('utf-8')}\",\n" \
               f"\t\"Renderer\":       \"{GL.glGetString(GL.GL_RENDERER).decode('utf-8')}\",\n" \
               f"\t\"OpenGL Version\": \"{GL.glGetString(GL.GL_VERSION).decode('utf-8')}\",\n" \
               f"\t\"Shader Version\": \"{GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode('utf-8')}\"\n}}"

    def create_grid(self):
        model_gl = ModelGL()
        model_gl.transform.scale = Vector3(10, 10, 10)
        model_gl.material = gl_globals.GRID_MATERIAL
        model_gl.mesh = gl_globals.PLANE_MESH
        self._scene_models.append(model_gl)

    def load_model(self, file_path: str = None, t: Transform = None):
        if file_path is None:
            model_gl = ModelGL()
            model_gl.mesh = gl_globals.BOX_MESH
            self._scene_models.append(model_gl)
            if t is not None:
                model_gl.transform.transform_matrix *= t.transform_matrix
            return
        try:
            for m in read_obj_mesh(file_path):
                model_gl = ModelGL()
                model_gl.mesh = MeshGL(m)
                if t is not None:
                    model_gl.transform.transform_matrix *= t.transform_matrix
                self._scene_models.append(model_gl)
        except RuntimeError as err:
            pass

    def draw_line_2d(self, points: List[Vector2]):
        model_gl = ModelGL()
        model_gl.material = gl_globals.DEFAULT_MATERIAL
        model_gl.mesh = MeshGL(poly_strip(points))
        self._scene_models.append(model_gl)

    def initializeGL(self):
        self.fmt = QOpenGLVersionProfile()
        self.fmt.setVersion(3, 3)
        self.fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        GL.glClearColor(125/255, 135/255, 145/255, 1)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        print(SceneViewerWidget._get_opengl_info())
        gl_globals.init()
        self._main_camera.look_at(Vector3(0, 0, 0), Vector3(1, 1, 1))
        self.create_grid()
        self.load_model('../big_map.obj')
        self.load_model()
        self.spawn_obj()
        n = 257
        dt = 1.0 / (n - 1)
        dpi = dt * math.pi * 2.0
        r = 4.0
        line = [Vector2(math.sin(i * dpi) * r * (1.0 + 0.25 * math.cos(i * dpi * 8)),
                        math.cos(i * dpi) * r * (1.0 + 0.25 * math.cos(i * dpi * 8))) for i in range(n)]
        self.draw_line_2d(line)
        # self.draw_line()

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
        gl_globals.free()
        self.doneCurrent()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._mouse.update_position(event.pos().x(), event.pos().y(), self.width(), self.height())
        self._mouse.update_state(-1)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._mouse.update_position(event.pos().x(), event.pos().y(), self.width(), self.height())
        self._mouse.update_state(event.button())

    def spawn_obj(self):
        # pm * vm * p = v
        # vm^-1 * pm^-1 * v

        p = Vector3(self._mouse.x, self._mouse.y, 0.0)
        vm = self._main_camera.look_at_matrix.invert()
        pm = self._main_camera.projection.invert()
        tm = vm * pm
        pos = Vector3(tm.m00 * p.x + tm.m01 * p.y + tm.m03,
                      tm.m10 * p.x + tm.m11 * p.y + tm.m13,
                      tm.m20 * p.x + tm.m21 * p.y + tm.m23)
#
        model_gl = ModelGL()
        model_gl.transform.origin = pos
        model_gl.mesh = gl_globals.BOX_MESH
        self._scene_models.append(model_gl)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._mouse.update_position(event.pos().x(), event.pos().y(), self.width(), self.height())
        if self._mouse.is_left_button:
            self.spawn_obj()  # _main_camera.transform.angles += Vector3(self._mouse.y_delta, -self._mouse.x_delta, 0)

        if self._mouse.is_right_button:
            self._main_camera.transform.angles += Vector3(self._mouse.y_delta, -self._mouse.x_delta, 0)

            # bbox = BoundingBox()
            # for m in self._scene_models:
            #     bbox.encapsulate(m.mesh.bounds.max)
            #     bbox.encapsulate(m.mesh.bounds.min)
            # size = bbox.size
            # cntr = bbox.center
            # self._main_camera.look_at(cntr, cntr + size)

        if self._mouse.is_wheel_button:
            scale = self._main_camera.transform.origin.magnitude()
            self._main_camera.transform.origin += \
                (self._main_camera.transform.up * -self._mouse.y_delta * scale +
                 self._main_camera.transform.right * self._mouse.x_delta * scale)

    def wheelEvent(self, event: QWheelEvent) -> None:
        self._main_camera.transform.origin += self._main_camera.transform.front * event.angleDelta().y() / 120.0

    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)
        self._main_camera.aspect = float(height)/width

    def updateGL(self) -> None:
        print(f"len(self._scene_models): {len(self._scene_models)}")
        for m in self._scene_models:
            self.render_call(self._main_camera, m)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        while len(self._render_queue) != 0:
            self._render_queue.pop()()
        self.swapBuffers()


