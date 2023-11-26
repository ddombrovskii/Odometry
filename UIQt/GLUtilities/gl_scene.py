from Utilities.Geometry import Matrix4, Vector3, Vector2, BoundingBox, Camera
from Utilities.Common import BitSet32
from .gl_tris_mesh import read_obj_mesh, poly_strip
from .gl_frame_buffer import FrameBufferGL
from .gl_material import MaterialGL
from .gl_texture import TextureGL
from .gl_shader import ShaderGL
from .gl_model import ModelGL
from .gl_mesh import MeshGL
from UIQt.GLUtilities import gl_globals
from typing import List, Dict
import OpenGL.GL as GL
import json


class SceneGL:
    DRAW_GIZMOS = 0
    DRAW_ENTITIES = 1

    def __init__(self):
        self._entities: Dict[int, ModelGL] = {}
        self._gizmos:   Dict[int, ModelGL] = {}
        self._cam_view_matrix = Matrix4.identity()
        self._cam_projection = Matrix4.identity()
        self._cam_position   = Vector3(0, 0, 0)
        self._bounds         = BoundingBox()
        self._gizmo_bounds   = BoundingBox()
        self._draw_state: BitSet32 = BitSet32()
        self._models_bounds  = BoundingBox()
        self.draw_gizmos   = True
        self.draw_entities = True
        self._perspective  = True
        self.override_material: MaterialGL | None = None

    @property
    def models_count(self) -> int:
        return len(self._entities)

    @property
    def gizmos_count(self) -> int:
        return len(self._gizmos)

    def remove_model(self, model: ModelGL):
        if model is None:
            return
        if model.bind_id in self._entities:
            del self._entities[model.bind_id]
            return
        if model.bind_id in self._gizmos:
            del self._gizmos[model.bind_id]
            return

    @property
    def scene_materials(self) -> List[MaterialGL]:
        materials = {}
        for m in self._entities.values():
            materials.update({m.material.bind_id: m.material})
        for m in self._gizmos.values():
            materials.update({m.material.bind_id: m.material})
        return list(materials.values())

    @property
    def scene_textures(self) -> List[TextureGL]:
        materials = self.scene_materials
        textures = {}
        for m in materials:
            for t in m.textures.values():
                textures.update({t.bind_id: t})
        for m in self._gizmos.values():
            for t in m.material.textures.values():
                textures.update({t.bind_id: t})
        return list(textures.values())

    @property
    def scene_meshes(self) -> List[MeshGL]:
        meshes = {}
        for m in self._entities.values():
            meshes.update({m.bind_id: m.mesh})
        for m in self._gizmos.values():
            meshes.update({m.bind_id: m.mesh})
        return list(meshes.values())

    @property
    def scene_shaders(self) -> List[ShaderGL]:
        shaders = {}
        materials = self.scene_materials
        for m in materials:
            shaders.update({m.shader.bind_id: m.shader})
        return list(shaders.values())

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

    @property
    def bounds(self) -> BoundingBox:
        return self._bounds

    @property
    def gizmos_bounds(self) -> BoundingBox:
        return self._gizmo_bounds

    @property
    def models_bounds(self) -> BoundingBox:
        return self._models_bounds

    def update_camera_state(self, camera: Camera = None):
        if camera is None:
            self._cam_view_matrix = gl_globals.MAIN_CAMERA.look_at_matrix
            self._cam_projection  = gl_globals.MAIN_CAMERA.projection
            self._cam_position    = gl_globals.MAIN_CAMERA.transform.origin
            self._perspective     = gl_globals.MAIN_CAMERA.perspective_mode
            return
        self._cam_view_matrix = camera.look_at_matrix
        self._cam_projection  = camera.projection
        self._cam_position    = camera.transform.origin
        self._perspective     = camera.perspective_mode

    def create_grid(self, transform: Matrix4 = None) -> ModelGL:
        model_gl = ModelGL()
        if transform is not None:
            model_gl.transform.transform_matrix *= transform
        model_gl.material = gl_globals.GRID_MATERIAL
        model_gl.mesh = gl_globals.PLANE_MESH
        model_gl.name = "grid"
        self.add_gizmo(model_gl)
        return model_gl

    def create_box(self, transform: Matrix4 = None, mat_name: str = None) -> ModelGL:
        model_gl = ModelGL()
        if transform is not None:
            model_gl.transform.transform_matrix *= transform
        model_gl.material = MaterialGL.materials.get_by_name("red_material") if mat_name is None else\
            MaterialGL.materials.get_by_name(mat_name)
        model_gl.mesh = gl_globals.BOX_MESH
        self.add_gizmo(model_gl)
        return model_gl

    def create_sky(self, transform: Matrix4 = None) -> ModelGL:
        model_gl = ModelGL()
        if transform is not None:
            model_gl.transform.transform_matrix *= transform
        model_gl.mesh = gl_globals.SPHERE_MESH
        self.add_gizmo(model_gl)
        return model_gl

    def create_line(self, points: List[Vector2], transform: Matrix4 = None, line_width: float = 0.04) -> ModelGL:
        model_gl = ModelGL()
        if transform is not None:
            model_gl.transform.transform_matrix *= transform
        model_gl.material = MaterialGL.materials.get_by_name("blue_material")
        model_gl.mesh = MeshGL(poly_strip(points, strip_width=line_width))
        self.add_gizmo(model_gl)
        return model_gl

    def load_model(self, file_path: str = None, transform: Matrix4 = None):
        if file_path is None:
            model_gl = ModelGL()
            if transform is not None:
                model_gl.transform.transform_matrix *= transform
            self.add_model(model_gl)
            return
        try:
            for m in read_obj_mesh(file_path):
                model_gl = ModelGL()
                model_gl.mesh = MeshGL(m)
                if transform is not None:
                    model_gl.transform.transform_matrix *= transform
                self.add_model(model_gl)
        except RuntimeError as err:
            pass

    def add_model(self, model: ModelGL):
        self._entities.update({model.bind_id: model})
        bbox = model.bounds_world
        self.bounds.encapsulate(bbox.min)
        self.bounds.encapsulate(bbox.max)
        self.models_bounds.encapsulate(bbox.min)
        self.models_bounds.encapsulate(bbox.max)

    def add_gizmo(self, model: ModelGL):
        self._gizmos.update({model.bind_id: model})
        bbox = model.bounds_world
        self.bounds.encapsulate(bbox.min)
        self.bounds.encapsulate(bbox.max)
        self.gizmos_bounds.encapsulate(bbox.min)
        self.gizmos_bounds.encapsulate(bbox.max)

    def draw_scene(self, frame_buffer: FrameBufferGL = None, camera: Camera = None):
        self.update_camera_state(camera)
        if frame_buffer is None:
            if self.draw_gizmos:
                self._on_draw_gizmos()
            if self.draw_entities:
                self._on_draw_entities(self.override_material)
            return
        frame_buffer.bind()
        GL.glClearColor(1, 1, 1, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)
        if self.draw_gizmos:
            self._on_draw_gizmos()
        if self.draw_entities:
            self._on_draw_entities(self.override_material)

    def _on_draw_gizmos(self):
        for e in self._gizmos.values():
            self._draw_any(e)

    def _on_draw_entities(self, override_material=None):
        for e in self._entities.values():
            self._draw_any(e, override_material)

    def _draw_any(self, model: ModelGL, override_material=None):
        if not model.enable:
            return
        material = override_material if override_material is not None else model.material
        if material.bind():
            material.set_property_val("view",         self._cam_view_matrix)
            material.set_property_val("projection",   self._cam_projection)
            material.set_property_val("cam_position", self._cam_position)
            # material.set_property_val("model", model.transform.transform_matrix.transpose())
        material.shader.send_mat_4("model", model.transform.transform_matrix)  # .transpose())
        model.mesh.draw()


GL_SCENE_TEXTURES = "Textures"
GL_SCENE_MESHES = "Meshes"
GL_SCENE_SHADERS = "Shaders"
GL_SCENE_CAMERA = "Camera"
GL_SCENE_MATERIALS = "Materials"
GL_SCENE_MODELS = "Models"
GL_SCENE_GIZMOS = "Gizmos"


def merge_scene(scene: SceneGL, src_file: str) -> SceneGL:
    with open(f"{src_file}\\scene.json", 'rt') as input_file:
        raw_data = json.loads(input_file.read())

    if raw_data is None:
        return scene

    if GL_SCENE_TEXTURES in raw_data:
        textures = raw_data[GL_SCENE_TEXTURES]
        for texture in textures:
            t = TextureGL()
            t.load(f"{src_file}\\{texture['source']}")
            t.name = texture["name"]

    if GL_SCENE_MESHES in raw_data:
        meshes = raw_data[GL_SCENE_MESHES]
        for mesh in meshes:
            _m = read_obj_mesh(f"{src_file}\\{mesh['source']}")
            if len(_m) == 0:
                continue
            m = MeshGL(_m[0])
            m.name = mesh["name"]

    if GL_SCENE_SHADERS in raw_data:
        shades = raw_data[GL_SCENE_SHADERS]
        for shader_src in shades:
            shader = ShaderGL()
            shader.vert_shader(f"{src_file}\\{shader_src}.vert")
            shader.frag_shader(f"{src_file}\\{shader_src}.frag")
            shader.load_defaults_settings()

    if GL_SCENE_CAMERA in raw_data:
        gl_globals.MAIN_CAMERA.setting_from_json(raw_data[GL_SCENE_CAMERA])

    if GL_SCENE_MATERIALS in raw_data:
        materials = raw_data[GL_SCENE_MATERIALS]
        for m in materials:
            # if not MaterialGL.materials.check_if_name_valid(m["name"]):
            #     continue
            shader = ShaderGL.shaders.get_by_name(m["shader"])
            if shader is None:
                continue
            material = MaterialGL(shader)
            material.setting_from_json(m)

    if GL_SCENE_MODELS in raw_data:
        for node in raw_data[GL_SCENE_MODELS]:
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

    if GL_SCENE_GIZMOS in raw_data:
        gizmos = raw_data[GL_SCENE_GIZMOS]
        for g in gizmos:
            if "type" not in g:
                continue
            g_type = g["type"]
            if g_type == "grid":
                grid = scene.create_grid()
                if "material" in g:
                    grid.material = MaterialGL.materials.get_by_name(g["material"])
                if "transform" in g:
                    try:
                        t = Matrix4(*(float(value) for value in g["transform"].values()))
                        grid.transform.transform_matrix = t
                    except ValueError as er:
                        print(f"SceneGL :: load_scene :: incorrect gizmo transform\n : {g['transform']}\n{er.args}")
                continue
            if g_type == "sky":
                sky = scene.create_sky()
                if "material" in g:
                    sky.material = MaterialGL.materials.get_by_name(g["material"])
                if "transform" in g:
                    try:
                        t = Matrix4(*(float(value) for value in g["transform"].values()))
                        sky.transform.transform_matrix = t
                    except ValueError as er:
                        print(f"SceneGL :: load_scene :: incorrect gizmo transform\n : {g['transform']}\n{er.args}")
                continue
            if g_type == "line-2d":
                if "points" not in g:
                    continue
                try:
                    points = [Vector2(*(float(value) for value in v.values())) for v in g["points"]]
                except ValueError as err:
                    print(f"SceneGL :: load_scene :: incorrect line-2d points\n{err.args}")
                    continue
                line = scene.create_line(points)
                if "material" in g:
                    line.material = MaterialGL.materials.get_by_name(g["material"])
                if "transform" in g:
                    try:
                        t = Matrix4(*(float(value) for value in g["transform"].values()))
                        line.transform.transform_matrix = t
                    except ValueError as er:
                        print(f"SceneGL :: load_scene :: incorrect gizmo transform\n : {g['transform']}\n{er.args}")

    grid: ModelGL | None = ModelGL.models.get_by_name("grid")

    if grid is None:
        return scene

    grid_sx, _, grid_sz = grid.mesh.bounds.size
    if scene.models_count != 0:
        sx, sy, sz = scene.models_bounds.size
        sx_ = round(sx / grid_sx)
        sz_ = round(sz / grid_sz)
        sx_ = sx_ if sx_ > sx else sx_ + 1
        sz_ = sz_ if sz_ > sz else sz_ + 1
        grid.transform.scale = Vector3(sx_, 1.0, sz_)
        gl_globals.MAIN_CAMERA.look_at(scene.models_bounds.center, Vector3(1, 1, 1) * 1.0 * max(sx, sy, sz))
        return scene

    if scene.gizmos_count != 0:
        sx, sy, sz = scene.gizmos_bounds.size
        sx_ = round(sx / grid_sx)
        sz_ = round(sz / grid_sz)
        sx_ = sx_ if sx_ > sx else sx_ + 1
        sz_ = sz_ if sz_ > sz else sz_ + 1
        grid.transform.scale = Vector3(sx_, 1.0, sz_)
        return scene

    grid.transform.scale = Vector3(32, 1.0, 32)
    return scene


def load_scene(src_file: str) -> SceneGL:
    scene: SceneGL = SceneGL()
    merge_scene(scene, src_file)
    return scene


def save_scene(file_path: str, scene: SceneGL):
    def comas(v):
        return f"\"{str(v)}\""

    def str_clean(v):
        return v.replace('\\', '/')

    with open(file_path, "wt") as output:
        sep = ',\n'
        print(f"{{\n\"Textures\":[\n{sep.join(str(t) for t in scene.scene_textures)}\n],", file=output)
        print(f"\n\"Meshes\":[\n{sep.join(str(t) for t in scene.scene_meshes)}\n],", file=output)
        print(f"\n\"Shaders\":[\n{sep.join(comas(str_clean(t.vert_src)) for t in scene.scene_shaders)}\n],", file=output)
        print(f"\n\"Materials\":[\n{sep.join(str(t) for t in scene.scene_materials)}\n]\n}}", file=output)
