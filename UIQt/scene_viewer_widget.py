from PyQt5.QtGui import QOpenGLVersionProfile, QSurfaceFormat, QMouseEvent, QWheelEvent, QKeyEvent
from UIQt.Scripts.Functionality.mouse_view_contoller import MouseViewController
from UIQt.GLUtilities import SceneGL, load_scene
from UIQt.Scripts.viewer_behaviour import ViewerBehaviour
from UIQt.GLUtilities import FrameBufferGL
from UIQt.GLUtilities import gl_error_catch
from UIQt.GLUtilities import gl_globals
from Utilities.Geometry import Vector3
from PyQt5 import QtOpenGL, QtCore
from typing import List
import OpenGL.GL as GL


class SceneViewerWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.makeCurrent()
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.parent = parent
        self._scene: SceneGL = SceneGL()
        self._components: List[ViewerBehaviour] = []
        self._mouse_controller = MouseViewController(self.scene_gl)
        self._frame_buffer: FrameBufferGL | None = None
        self._fmt: QOpenGLVersionProfile | None = None

    def register_behaviour(self, behaviour: ViewerBehaviour):
        self._components.append(behaviour)

    @property
    def scene_gl(self) -> SceneGL:
        return self._scene

    @staticmethod
    def _get_opengl_info():
        def formatter(v):
            v = f"\"{v}\""
            return f"{v:>50}"

        return f"{{\n" \
               f"\t\"Vendor\"         : {formatter(GL.glGetString(GL.GL_VENDOR).  decode('utf-8'))},\n" \
               f"\t\"Renderer\"       : {formatter(GL.glGetString(GL.GL_RENDERER).decode('utf-8'))},\n" \
               f"\t\"OpenGL Version\" : {formatter(GL.glGetString(GL.GL_VERSION). decode('utf-8'))},\n" \
               f"\t\"Shader Version\" : {formatter(GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode('utf-8'))}\n" \
               f"}}"

    def _reset_frame_buffer(self):
        if self._frame_buffer is not None:
            self._frame_buffer.delete()
        self._frame_buffer = FrameBufferGL(self.width(), self.height())
        self._frame_buffer.name = "main-screen-frame-buffer"
        self._frame_buffer.create_color_attachment_rgba_8("attachment_0")
        self._frame_buffer.create_depth()
        self._frame_buffer.validate()
        self._frame_buffer.clear_buffer()
        self._frame_buffer.unbind()

    def initializeGL(self):
        self._fmt = QOpenGLVersionProfile()
        self._fmt.setVersion(3, 3)
        self._fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        print(SceneViewerWidget._get_opengl_info())
        gl_globals.init()
        self._reset_frame_buffer()
        self._scene = load_scene(r".\GLUtilities\StartScene")
        gl_globals.MAIN_CAMERA.look_at(Vector3(0, 0, 0), self._scene.bounds.max * 0.6)

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
        self._mouse_controller.wheel_update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        gl_globals.MOUSE_CONTROLLER.update_on_release(event)
        self._mouse_controller.mouse_update()
        ###############################################

    def mousePressEvent(self, event: QMouseEvent) -> None:
        gl_globals.MOUSE_CONTROLLER.update_on_press(event)
        self._mouse_controller.mouse_update()
        ###############################################

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        gl_globals.MOUSE_CONTROLLER.update_on_hold(event)
        self._mouse_controller.mouse_update()

    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)
        self._reset_frame_buffer()
        gl_globals.MAIN_CAMERA.aspect = float(height) / width

    def _keyboard_interaction(self):
        keyboard = gl_globals.KEYBOARD_CONTROLLER
        camera = gl_globals.MAIN_CAMERA
        if camera.perspective_mode:
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
        else:
            if keyboard.key_w.is_hold or keyboard.key_up.is_hold:
                camera.transform.origin -= camera.transform.up

            if keyboard.key_a.is_hold or keyboard.key_left.is_hold:
                camera.transform.origin += camera.transform.right

            if keyboard.key_s.is_hold or keyboard.key_down.is_hold:
                camera.transform.origin += camera.transform.up

            if keyboard.key_d.is_hold or keyboard.key_right.is_hold:
                camera.transform.origin -= camera.transform.right

            if keyboard.key_q.is_hold:
                size = gl_globals.MAIN_CAMERA.ortho_size - 1.0
                max_size = self._scene.bounds.size.magnitude()
                gl_globals.MAIN_CAMERA.ortho_size = min(max(0.1, size), max_size * 0.5)

            if keyboard.key_e.is_hold:
                size = gl_globals.MAIN_CAMERA.ortho_size + 1.0
                max_size = self._scene.bounds.size.magnitude()
                gl_globals.MAIN_CAMERA.ortho_size = min(max(0.1, size), max_size * 0.5)

        if keyboard.key_plus .is_hold:
            ...
        if keyboard.key_minus.is_hold:
            ...

        if keyboard.key_x.is_hold:
            self._frame_buffer.grab_snap_shot().save("snap-shoot.png")

    @gl_error_catch
    def updateGL(self) -> None:
        gl_globals.KEYBOARD_CONTROLLER.update_on_hold()
        for c in self._components:
            c.update()
        self._scene.update_camera_state()

    @gl_error_catch
    def paintGL(self):
        self._scene.draw_scene(self._frame_buffer)
        self._frame_buffer.blit()
        self._keyboard_interaction()
        self.swapBuffers()


