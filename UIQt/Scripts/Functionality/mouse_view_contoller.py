from UIQt.GLUtilities.gl_frame_buffer import FrameBufferGL
from UIQt.Scripts.viewer_behaviour import ViewerBehaviour
from UIQt.GLUtilities.gl_scene import SceneGL
from UIQt.GLUtilities import gl_globals
from Utilities.Geometry import Vector3


class MouseViewController(ViewerBehaviour):
    def __init__(self, scene_gl: SceneGL):
        super().__init__(scene_gl)

    def wheel_update(self):
        if gl_globals.MAIN_CAMERA.perspective_mode:
            MouseViewController._wheel_perspective(self.scene_gl)
            return
        MouseViewController._wheel_ortho(self.scene_gl)

    def mouse_update(self):
        if gl_globals.MAIN_CAMERA.perspective_mode:
            MouseViewController._mouse_perspective(self.scene_gl)
            return
        MouseViewController._mouse_ortho(self.scene_gl)

    @staticmethod
    def _wheel_perspective(scene_gl: SceneGL):
        gl_globals.MAIN_CAMERA.transform.origin += \
            gl_globals.MAIN_CAMERA.transform.front * gl_globals.MOUSE_CONTROLLER.wheel_delta / 120.0

    @staticmethod
    def _wheel_ortho(scene_gl: SceneGL):
        size = gl_globals.MAIN_CAMERA.ortho_size - gl_globals.MOUSE_CONTROLLER.wheel_delta / 120.0
        max_size = scene_gl.bounds.size.magnitude()
        gl_globals.MAIN_CAMERA.ortho_size = min(max(0.1, size), max_size)

    @staticmethod
    def _mouse_perspective(scene_gl: SceneGL):
        if gl_globals.MOUSE_CONTROLLER.right_btn.is_hold:
            delta = gl_globals.MOUSE_CONTROLLER.right_btn.delta_pos
            w, h = FrameBufferGL.get_main_frame_buffer().shape
            gl_globals.MAIN_CAMERA.transform.angles += Vector3(delta.y / h, -delta.x / w, 0)
            return

        if gl_globals.MOUSE_CONTROLLER.middle_btn.is_hold:
            scale = gl_globals.MAIN_CAMERA.transform.origin.magnitude()
            delta = gl_globals.MOUSE_CONTROLLER.middle_btn.delta_pos
            w, h = FrameBufferGL.get_main_frame_buffer().shape
            gl_globals.MAIN_CAMERA.transform.origin += \
                (gl_globals.MAIN_CAMERA.transform.up * -delta.y / h * scale +
                 gl_globals.MAIN_CAMERA.transform.right * delta.x / w * scale)
            return

    @staticmethod
    def _mouse_ortho(scene_gl: SceneGL):
        if gl_globals.MOUSE_CONTROLLER.middle_btn.is_hold:
            scale = gl_globals.MAIN_CAMERA.ortho_size
            delta = gl_globals.MOUSE_CONTROLLER.middle_btn.delta_pos
            w, h = FrameBufferGL.get_main_frame_buffer().shape
            gl_globals.MAIN_CAMERA.transform.origin += \
                (gl_globals.MAIN_CAMERA.transform.up * -delta.y / h * scale +
                 gl_globals.MAIN_CAMERA.transform.right * delta.x / w * scale)

