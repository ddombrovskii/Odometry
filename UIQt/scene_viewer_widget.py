from PyQt5.QtGui import QOpenGLVersionProfile, QSurfaceFormat, QMouseEvent, QWheelEvent, QKeyEvent

from UIQt.GLUtilities.gl_decorators import gl_error_catch
from UIQt.GLUtilities.gl_frame_buffer import FrameBufferGL
from UIQt.GLUtilities.gl_material import MaterialGL
from UIQt.GLUtilities.triangle_mesh import TrisMesh, read_obj_mesh, poly_strip
from Utilities.Geometry import Vector3, Transform, Vector2
from UIQt.GLUtilities.gl_camera import CameraGL
from UIQt.GLUtilities.gl_model import ModelGL
from UIQt.GLUtilities.gl_mesh import MeshGL
from UIQt.GLUtilities import gl_globals
from OpenGL.GL.shaders import GL_TRUE
from collections import namedtuple
from PyQt5 import QtOpenGL, QtCore
from typing import List
import OpenGL.GL as GL
import math


class DrawCall(namedtuple('DrawCall', 'view, projection, cam_position, transform, material, mesh')):

    def __new__(cls, cam: CameraGL, model: ModelGL):
        return super().__new__(cls, cam.look_at_matrix, cam.projection, cam.transform.origin,
                               model.transform.transform_matrix, model.material, model.mesh)

    def __call__(self, material: MaterialGL = None):
        material = material if material is not None else self.material
        material.bind()
        material.shader.send_mat_4("view", self.view)
        material.shader.send_mat_4("projection", self.projection)
        material.shader.send_vec_3("cam_position", self.cam_position)
        material.shader.send_mat_4("model", self.transform, GL_TRUE)
        self.mesh.draw()


class SceneViewerWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.fmt: QOpenGLVersionProfile = None
        self.parent = parent
        self._render_queue: List[DrawCall] = []
        self._scene_models: List[ModelGL] = []
        self._frame_buffer = None
        self.setFocusPolicy(QtCore.Qt.ClickFocus)

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

    def _reset_frame_buffer(self):
        if self._frame_buffer is not None:
            self._frame_buffer.delete()
        self._frame_buffer = FrameBufferGL(self.width(), self.height())
        self._frame_buffer.create_color_attachment_rgba_8("attachment_0")
        self._frame_buffer.create_depth()
        self._frame_buffer.validate()
        self._frame_buffer.clear_buffer()
        self._frame_buffer.unbind()

    def initializeGL(self):
        self.fmt = QOpenGLVersionProfile()
        self.fmt.setVersion(3, 3)
        self.fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        GL.glClearColor(125 / 255, 135 / 255, 145 / 255, 1)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        # GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        print(SceneViewerWidget._get_opengl_info())
        gl_globals.init()
        gl_globals.MAIN_CAMERA.look_at(Vector3(0, 0, 0), Vector3(1, 1, 1))
        self._reset_frame_buffer()

        self.create_grid()
        # self.load_model('../big_map.obj')
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

    def keyPressEvent(self, event: QKeyEvent) -> None:
        gl_globals.KEYBOARD_CONTROLLER.update_on_press(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        gl_globals.KEYBOARD_CONTROLLER.update_on_release(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        gl_globals.MOUSE_CONTROLLER.update_on_wheel(event)
        ###############################################
        gl_globals.MAIN_CAMERA.transform.origin += \
            gl_globals.MAIN_CAMERA.transform.front * gl_globals.MOUSE_CONTROLLER.wheel_delta / 120.0

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        gl_globals.MOUSE_CONTROLLER.update_on_release(event)
        ###############################################

    def mousePressEvent(self, event: QMouseEvent) -> None:
        gl_globals.MOUSE_CONTROLLER.update_on_press(event)
        ###############################################

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        gl_globals.MOUSE_CONTROLLER.update_on_hold(event)
        ###############################################
        if gl_globals.MOUSE_CONTROLLER.right_btn.is_hold:
            delta = gl_globals.MOUSE_CONTROLLER.right_btn.delta_pos
            gl_globals.MAIN_CAMERA.transform.angles += Vector3(delta.y / self.height(), -delta.x / self.width(), 0)
        ###############################################
        if gl_globals.MOUSE_CONTROLLER.middle_btn.is_hold:
            scale = gl_globals.MAIN_CAMERA.transform.origin.magnitude()
            delta = gl_globals.MOUSE_CONTROLLER.middle_btn.delta_pos
            gl_globals.MAIN_CAMERA.transform.origin += \
                (gl_globals.MAIN_CAMERA.transform.up * -delta.y / self.height() * scale +
                 gl_globals.MAIN_CAMERA.transform.right * delta.x / self.width() * scale)
        ###############################################

        # self._mouse.update_position(event.pos().x(), event.pos().y(), self.width(), self.height())
        # if self._mouse.is_left_button:
        #     self.spawn_obj()  #g l_globals.MAIN_CAMERA.transform.angles += Vector3(self._mouse.y_delta, -self._mouse.x_delta, 0)

        # if self._mouse.is_right_button:
        #     gl_globals.MAIN_CAMERA.transform.angles += Vector3(self._mouse.y_delta, -self._mouse.x_delta, 0)

        # bbox = BoundingBox()
        # for m in self._scene_models:
        #     bbox.encapsulate(m.mesh.bounds.max)
        #     bbox.encapsulate(m.mesh.bounds.min)
        # size = bbox.size
        # cntr = bbox.center
        # self._main_camera.look_at(cntr, cntr + size)

    def spawn_obj(self):
        # pm * vm * p = v
        # vm^-1 * pm^-1 * v
        pos = gl_globals.MOUSE_CONTROLLER.middle_btn.hold_pos
        view_ray: Vector3 = gl_globals.MAIN_CAMERA.screen_coord_to_camera_ray(pos.x / self.width(), pos.y / self.height())
        if abs(view_ray.y) < 1e-3:
            return
        view_orig = gl_globals.MAIN_CAMERA.transform.origin
        # (r - r0, n) = (et + r0, {0, 1, 0}) = ey t + y0 = 0
        t = -view_orig.y / view_ray.y
        #
        model_gl = ModelGL()
        model_gl.transform.origin = (-view_orig.y / view_ray.y) * view_ray + view_orig
        model_gl.mesh = gl_globals.BOX_MESH
        self._scene_models.append(model_gl)

    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)
        self._reset_frame_buffer()
        gl_globals.MAIN_CAMERA.aspect = float(height) / width

    def _keyboard_interaction(self):
        keyboard = gl_globals.KEYBOARD_CONTROLLER
        camera  = gl_globals.MAIN_CAMERA
        if keyboard.key_w.is_hold or keyboard.key_up.is_hold:
            camera.transform.origin += camera.transform.front

        if keyboard.key_a.is_hold or keyboard.key_left.is_hold:
            camera.transform.origin += camera.transform.right

        if keyboard.key_s.is_hold or keyboard.key_down.is_hold:
            camera.transform.origin -= camera.transform.front

        if keyboard.key_d.is_hold or keyboard.key_right.is_hold:
            camera.transform.origin -= camera.transform.right

        if keyboard.key_q.is_hold:
            camera.transform.origin += Vector3(0, 1, 0)

        if keyboard.key_e.is_hold:
            camera.transform.origin -= Vector3(0, 1, 0)

        if keyboard.key_plus .is_hold:
            ...
        if keyboard.key_minus.is_hold:
            ...
        if keyboard.key_z.is_hold:
            ...
        if keyboard.key_x.is_hold:
            self._frame_buffer.grab_snap_shot()
            self._frame_buffer.grab_depth_snap_shot()

    def updateGL(self) -> None:
        gl_globals.KEYBOARD_CONTROLLER.update_on_hold()
        for m in self._scene_models:
            self.render_call(gl_globals.MAIN_CAMERA, m)

    @gl_error_catch
    def paintGL(self):
        self._frame_buffer.bind()
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_STENCIL_TEST)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)
        while len(self._render_queue) != 0:
            self._render_queue.pop()()  # (gl_globals.MAP_MATERIAL)
        self._keyboard_interaction()
        self._frame_buffer.blit()
        self.swapBuffers()

