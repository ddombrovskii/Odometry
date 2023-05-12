from UIQt.GLUtilities.triangle_mesh import read_obj_mesh, poly_strip
from Utilities.Geometry import Matrix4, Vector3, Vector2
from UIQt.GLUtilities.gl_material import MaterialGL
from UIQt.GLUtilities.gl_model import ModelGL
from UIQt.GLUtilities.gl_mesh import MeshGL
from UIQt.GLUtilities import gl_globals
from OpenGL.GL.shaders import GL_TRUE
from typing import List


class SceneGL:
    def __init__(self):
        self._entities = []
        self._gizmos = []
        self._cam_view_matrix = Matrix4.identity()
        self._cam_projection  = Matrix4.identity()
        self._cam_position    = Vector3(0, 0, 0)

    def update_camera_state(self):
        self._cam_view_matrix = gl_globals.MAIN_CAMERA.look_at_matrix
        self._cam_projection  = gl_globals.MAIN_CAMERA.projection
        self._cam_position    = gl_globals.MAIN_CAMERA.transform.origin

    def create_grid(self, transform: Matrix4 = None) -> ModelGL:
        model_gl = ModelGL()
        if transform is not None:
            model_gl.transform.transform_matrix = transform
        model_gl.transform.scale *= Vector3(10, 10, 10)
        model_gl.material = gl_globals.GRID_MATERIAL
        model_gl.mesh = gl_globals.PLANE_MESH
        self._gizmos.append(model_gl)
        return model_gl

    def create_line(self, points: List[Vector2]) -> ModelGL:
        model_gl = ModelGL()
        model_gl.material = gl_globals.DEFAULT_MATERIAL
        model_gl.mesh = MeshGL(poly_strip(points))
        self._gizmos.append(model_gl)
        return model_gl

    def load_model(self, file_path: str = None, transform: Matrix4 = None):
        if file_path is None:
            model_gl = ModelGL()
            model_gl.mesh = gl_globals.BOX_MESH
            self._entities.append(model_gl)
            if transform is not None:
                model_gl.transform.transform_matrix *= transform
            return
        try:
            for m in read_obj_mesh(file_path):
                model_gl = ModelGL()
                model_gl.mesh = MeshGL(m)
                if transform is not None:
                    model_gl.transform.transform_matrix *= transform
                self._entities.append(model_gl)
        except RuntimeError as err:
            pass

    def add_model(self, model: ModelGL):
        ...

    def draw_scene(self):
        self.update_camera_state()
        self._on_draw_gizmos()
        self._on_draw_entities()

    def _on_draw_gizmos(self):
        for e in self._gizmos:
            self._draw_any(e)

    def _on_draw_entities(self):
        for e in self._entities:
            self._draw_any(e)

    def _draw_any(self, model: ModelGL, material: MaterialGL = None):
        material = material if material is not None else model.material
        material.bind()
        material.shader.send_mat_4("view", self._cam_view_matrix)
        material.shader.send_mat_4("projection", self._cam_projection)
        material.shader.send_vec_3("cam_position", self._cam_position)
        material.shader.send_mat_4("model", model.transform.transform_matrix, GL_TRUE)
        model.mesh.draw()
