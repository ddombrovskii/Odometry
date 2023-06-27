from UIQt.Scripts.viewer_behaviour import ViewerBehaviour
from UIQt.GLUtilities.gl_material import MaterialGL
from Utilities.Geometry import Vector3, Matrix4
from UIQt.GLUtilities.gl_scene import SceneGL
from UIQt.GLUtilities import gl_globals


class SwitchViewBehaviour(ViewerBehaviour):
    def __init__(self, scene_gl: SceneGL):
        super().__init__(scene_gl)
        self._last_transform: Matrix4 | None = None

    def switch_view(self):
        gl_globals.MAIN_CAMERA.perspective_mode = not gl_globals.MAIN_CAMERA.perspective_mode
        if not gl_globals.MAIN_CAMERA.perspective_mode:
            self._last_transform = gl_globals.MAIN_CAMERA.transform.transform_matrix
            gl_globals.MAIN_CAMERA.look_at(Vector3(0, 0, 0), Vector3(0, 100, 0), Vector3(-1, 0, 0))
            self.scene_gl.override_material = MaterialGL.materials.get_by_name("map_material")
        else:
            gl_globals.MAIN_CAMERA.transform.transform_matrix = self._last_transform
            gl_globals.MAIN_CAMERA.look_at(gl_globals.MAIN_CAMERA.transform.origin +
                                           gl_globals.MAIN_CAMERA.transform.front,
                                           gl_globals.MAIN_CAMERA.transform.origin, Vector3(0, 1, 0))
            self.scene_gl.override_material = None

