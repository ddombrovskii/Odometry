from PyQt5.QtGui import QOpenGLVersionProfile, QSurfaceFormat, QMouseEvent, QWheelEvent, QKeyEvent
from UIQt.GLUtilities.gl_decorators import gl_error_catch
from UIQt.GLUtilities.gl_frame_buffer import FrameBufferGL
from UIQt.GLUtilities.gl_scene import SceneGL, load_scene, save_scene
from Utilities.Geometry import Vector3, Vector2, Vector4
from UIQt.GLUtilities.gl_model import ModelGL
from UIQt.GLUtilities import gl_globals
from PyQt5 import QtOpenGL, QtCore
from typing import List
import OpenGL.GL as GL
import math


class SceneViewerWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.fmt: QOpenGLVersionProfile = None
        self.parent = parent
        self._scene = SceneGL()
        self._frame_buffer = None
        self.setFocusPolicy(QtCore.Qt.ClickFocus)

    @staticmethod
    def _get_opengl_info():
        return f"{{\n" \
               f"\t\"Vendor\":         \"{GL.glGetString(GL.GL_VENDOR).decode('utf-8')}\",\n" \
               f"\t\"Renderer\":       \"{GL.glGetString(GL.GL_RENDERER).decode('utf-8')}\",\n" \
               f"\t\"OpenGL Version\": \"{GL.glGetString(GL.GL_VERSION).decode('utf-8')}\",\n" \
               f"\t\"Shader Version\": \"{GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode('utf-8')}\"\n}}"

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
        print(SceneViewerWidget._get_opengl_info())
        gl_globals.init()
        self._reset_frame_buffer()
        self._scene = load_scene(r"E:\GitHub\Odometry\Odometry\UIQt\GLUtilities\Scenes")
        gl_globals.MAIN_CAMERA.look_at(self._scene.bounds.min, self._scene.bounds.max)

        for i in range(64):
            gl_globals.MAIN_CAMERA.transform.origin += gl_globals.MAIN_CAMERA.transform.right *  (i / 100.0)
            image = self._scene.draw_scene_preview(gl_globals.MAIN_CAMERA, 1024, 1024)
            image.save(f"previews/preview_{i + 1}.bmp")

    def clean_up(self) -> None:
        self.makeCurrent()
        save_scene("test_scene.json", self._scene)
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
        self.on_mouse_pick()
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
        # print(self._frame_buffer.read_depth_pixel( event.x(), event.y()))

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

    def on_mouse_pick(self):
        if not gl_globals.MOUSE_CONTROLLER.left_btn.is_pressed:
            return
        x_pix = gl_globals.MOUSE_CONTROLLER.left_btn.pressed_pos.x
        y_pix = gl_globals.MOUSE_CONTROLLER.left_btn.pressed_pos.y
        depth = self._frame_buffer.read_depth_pixel(x_pix, y_pix)
        print(*depth)
        x = -2.0 * x_pix / self.width() + 1
        y = -2.0 * y_pix / self.height() + 1
        clip_coord = Vector4(x, y, -1, 1)
        inv_projection = gl_globals.MAIN_CAMERA.projection.invert()
        eye_coord = inv_projection * clip_coord
        eye_coord = Vector4(eye_coord.x, eye_coord.y, 1, 0)
        inv_view_mat = gl_globals.MAIN_CAMERA.look_at_matrix.invert()
        eye_coord = inv_view_mat * eye_coord
        world_ray = Vector3(eye_coord.x, eye_coord.y, eye_coord.z).normalized()
        print(world_ray)

        # model = ModelGL()
        # model.mesh = gl_globals.BOX_MESH
        # view_orig = gl_globals.MAIN_CAMERA.transform.origin
        # model.transform.origin = (-view_orig.y / world_ray.y) * world_ray + view_orig
        # print(f"model.transform.origin {model.transform.origin}")
        # self._scene.add_model(model)



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
        # self._scene_models.append(model_gl)

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
            # self._frame_buffer.grab_depth_snap_shot()

    def updateGL(self) -> None:
        gl_globals.KEYBOARD_CONTROLLER.update_on_hold()

    @gl_error_catch
    def paintGL(self):
        self._scene.update_camera_state()
        self._scene.draw_scene(self._frame_buffer)
        self._frame_buffer.blit()
        self.swapBuffers()
        self._keyboard_interaction()


