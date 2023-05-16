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
    with open(f"{src_file}\\scene.json", 'rt') as input_file:
        raw_data = json.loads(input_file.read())

    if raw_data is None:
        return None

    scene = SceneGL()

    if "Textures" in raw_data:
        textures = raw_data["Textures"]
        for texture in textures:
            t = TextureGL()
            t.load(f"{src_file}\\{texture['source']}")
            t.name = texture["name"]

    if "Meshes" in raw_data:
        meshes = raw_data["Meshes"]
        for mesh in meshes:
            _m = read_obj_mesh(f"{src_file}\\{mesh['source']}")
            if len(_m) == 0:
                continue
            m = MeshGL(_m[0])
            m.name = mesh["name"]

    if "Shaders" in raw_data:
        shades = raw_data["Shaders"]
        for shader_src in shades:
            shader = ShaderGL()
            shader.vert_shader(f"{src_file}\\{shader_src}.vert")
            shader.frag_shader(f"{src_file}\\{shader_src}.frag")
            shader.load_defaults_settings()

    if "Camera" in raw_data:
        gl_globals.MAIN_CAMERA.setting_from_json(raw_data["Camera"])
    # работает
    if "Materials" in raw_data:
        materials = raw_data["Materials"]
        for m in materials:
            shader = ShaderGL.shaders.get_by_name(m["shader"])
            if shader is None:
                continue
            material = MaterialGL(shader)
            material.setting_from_json(m)

    if "Models" in raw_data:

        for node in raw_data["Models"]:
            if "mesh_src" not in node:
                continue
            if "material" not in node:
                continue
            model = ModelGL()
            model.mesh = MeshGL.meshes.get_by_name(node["mesh_src"])
            model.material = MaterialGL.materials.get_by_name(node["material"])
            if "transform" in node:
                try:
                    model.transform.transform_matrix = Matrix4(*(float(value) for value in node["transform"].values()))
                except ValueError as er:
                    print(f"SceneGL :: load_scene :: incorrect model transform\n : {node['transform']}\n{er.args}")
            scene.add_model(model)

    return scene

    # if "Models" in raw_data:
    #     models = raw_data["Models"]
    #     scene.add_model()

