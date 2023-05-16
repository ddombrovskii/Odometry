from UIQt.GLUtilities.gl_shader import ShaderGL
from UIQt.GLUtilities.triangle_mesh import read_obj_mesh, poly_strip
from Utilities.Geometry import Matrix4, Vector3, Vector2
from UIQt.GLUtilities.gl_material import MaterialGL
from UIQt.GLUtilities.gl_texture import TextureGL
from UIQt.GLUtilities.gl_model import ModelGL
from UIQt.GLUtilities.gl_mesh import MeshGL
from UIQt.GLUtilities import gl_globals
from OpenGL.GL.shaders import GL_TRUE
from Utilities import BitSet32
from typing import List
import json


class SceneGL:
    DRAW_GIZMOS = 0
    DRAW_ENTITIES = 1

    def __init__(self):
        self._entities = {}
        self._gizmos = {}
        self._cam_view_matrix = Matrix4.identity()
        self._cam_projection  = Matrix4.identity()
        self._cam_position    = Vector3(0, 0, 0)
        self._draw_state: BitSet32 = BitSet32()
        self.draw_gizmos = True
        self.draw_entities = True

    @property
    def draw_entities(self) -> bool:
        return self._draw_state.is_bit_set(SceneGL.DRAW_ENTITIES)

    @draw_entities.setter
    def draw_entities(self, value: bool) -> None:
        if value:
            self._draw_state.set_bit(SceneGL.DRAW_ENTITIES)
        else:
            self._draw_state.clear_bit(SceneGL.DRAW_ENTITIES)

    @property
    def draw_gizmos(self) -> bool:
        return self._draw_state.is_bit_set(SceneGL.DRAW_GIZMOS)

    @draw_gizmos.setter
    def draw_gizmos(self, value: bool) -> None:
        if value:
            self._draw_state.set_bit(SceneGL.DRAW_GIZMOS)
        else:
            self._draw_state.clear_bit(SceneGL.DRAW_GIZMOS)

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
        self._gizmos.update({model_gl.bind_id: model_gl})
        return model_gl

    def create_line(self, points: List[Vector2]) -> ModelGL:
        model_gl = ModelGL()
        model_gl.material = gl_globals.DEFAULT_MATERIAL
        model_gl.mesh = MeshGL(poly_strip(points))
        self._gizmos.update({model_gl.bind_id: model_gl})
        return model_gl

    def load_model(self, file_path: str = None, transform: Matrix4 = None):
        if file_path is None:
            model_gl = ModelGL()
            model_gl.mesh = gl_globals.BOX_MESH
            self._entities.update({model_gl.bind_id: model_gl})
            if transform is not None:
                model_gl.transform.transform_matrix *= transform
            return
        try:
            for m in read_obj_mesh(file_path):
                model_gl = ModelGL()
                model_gl.mesh = MeshGL(m)
                if transform is not None:
                    model_gl.transform.transform_matrix *= transform
                self._entities.update({model_gl.bind_id: model_gl})
        except RuntimeError as err:
            pass

    def add_model(self, model: ModelGL):
        self._entities.update({model.bind_id: model})

    def add_gizmo(self, model: ModelGL):
        self._gizmos.update({model.bind_id: model})

    def draw_scene(self):
        self.update_camera_state()
        if self.draw_gizmos:
            self._on_draw_gizmos()
        if self.draw_entities:
            self._on_draw_entities()

    def _on_draw_gizmos(self):
        for e in self._gizmos.values():
            self._draw_any(e)

    def _on_draw_entities(self):
        for e in self._entities.values():
            self._draw_any(e)

    def _draw_any(self, model: ModelGL, material: MaterialGL = None):
        material = material if material is not None else model.material
        material.bind()
        material.shader.send_mat_4("view", self._cam_view_matrix)
        material.shader.send_mat_4("projection", self._cam_projection)
        material.shader.send_vec_3("cam_position", self._cam_position)
        material.shader.send_mat_4("model", model.transform.transform_matrix, GL_TRUE)
        model.mesh.draw()


def load_scene(src_file: str) -> SceneGL:
    with open(src_file, 'rt') as input_file:
        raw_data = json.loads(input_file.read())

    if raw_data is None:
        return None

    if "Textures" in raw_data:
        textures = raw_data["Textures"]
        for texture in textures:
            t = TextureGL()
            t.load(texture["source"])
            t.name = texture["name"]

    if "Meshes" in raw_data:
        meshes = raw_data["Meshes"]
        for mesh in meshes:
            _m = read_obj_mesh(mesh["source"])
            if len(_m) == 0:
                continue
            m = MeshGL(_m[0])
            m.name = mesh["name"]

    if "Shades" in raw_data:
        shades = raw_data["Shades"]
        for shader_src in shades:
            shader = ShaderGL()
            shader.vert_shader(f"{shader_src}.vert")
            shader.frag_shader(f"{shader_src}.frag")
            shader.load_defaults_settings()

    if "Camera" in raw_data:
        camera = raw_data["Camera"]
        if "z_far" in camera:
            try:
                gl_globals.MAIN_CAMERA.z_far = float(camera["z_far"] )
            except ValueError as er:
                print(f"load_scene :: incorrect z_far : {camera['z_far']}\n{er.args}")
        if "z_near" in camera:
            try:
                gl_globals.MAIN_CAMERA.z_near = float(camera["z_near"] )
            except ValueError as er:
                print(f"load_scene :: incorrect z_near : {camera['z_near']}\n{er.args}")
        if "aspect" in camera:
            try:
                gl_globals.MAIN_CAMERA.aspect = float(camera["aspect"] )
            except ValueError as er:
                print(f"load_scene :: incorrect aspect : {camera['aspect']}\n{er.args}")
        if "fov" in camera:
            try:
                gl_globals.MAIN_CAMERA.fov = float(camera["fov"] )
            except ValueError as er:
                print(f"load_scene :: incorrect aspect : {camera['fov']}\n{er.args}")
        if "orthographic_size" in camera:
            try:
                gl_globals.MAIN_CAMERA.ortho_size = float(camera["orthographic_size"] )
            except ValueError as er:
                print(f"load_scene :: incorrect orthographic_size : {camera['orthographic_size']}\n{er.args}")
        if "is_orthographic" in camera:
            try:
                gl_globals.MAIN_CAMERA.perspective_mode = bool(camera["is_orthographic"] )
            except ValueError as er:
                print(f"load_scene :: incorrect is_orthographic : {camera['is_orthographic']}\n{er.args}")
        if "transform" in camera:
            try:
                t = Matrix4(*(float(value) for value in camera["transform"].values()))
                gl_globals.MAIN_CAMERA.transform.transform_matrix = t
            except ValueError as er:
                print(f"load_scene :: incorrect camera transform\n : {camera['transform']}\n{er.args}")

    if "Materials" in raw_data:
        materials = raw_data["Materials"]
        for m in materials:
            shader = ShaderGL.shaders.get_by_name(m["shader"])
            if shader is None:
                continue


    scene = SceneGL()

    # if "Models" in raw_data:
    #     models = raw_data["Models"]
    #     scene.add_model()

