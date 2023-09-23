from Utilities.Geometry import Camera
from .Materials import GridMaterial
from .Materials import MapMaterial
from .Materials import ObjMaterial
from UIQt.GLUtilities.Input.keyboard_controller import KeyboardController
from .gl_frame_buffer import FrameBufferGL
from .gl_tris_mesh import read_obj_mesh
from UIQt.GLUtilities.Input.mouse_controller import MouseController
from .gl_texture import TextureGL
from .gl_shader import ShaderGL
from .gl_mesh import MeshGL
from Utilities import Color
import numpy as np


####################################
#              SHADERS             #
####################################
SAMPLE_SHADER: ShaderGL | None = None
MAP_SHADER: ShaderGL | None = None
GRID_SHADER: ShaderGL | None = None
FRAME_BUFFER_BLIT_SHADER: ShaderGL | None = None

# UI_TEXT_SHADER = None
# UI_CLEAR_FB_SHADER = None
# FRAME_BUFFER_BLIT_SHADER = None


def _init_shaders():
    global SAMPLE_SHADER
    global MAP_SHADER
    global GRID_SHADER
    global FRAME_BUFFER_BLIT_SHADER

    SAMPLE_SHADER = ShaderGL()
    SAMPLE_SHADER.vert_shader("./GLUtilities/Shaders/sample_shader.vert")
    SAMPLE_SHADER.frag_shader("./GLUtilities/Shaders/sample_shader.frag")
    SAMPLE_SHADER.load_defaults_settings()

    MAP_SHADER = ShaderGL()
    MAP_SHADER.vert_shader("./GLUtilities/Shaders/map_shader.vert")
    MAP_SHADER.frag_shader("./GLUtilities/Shaders/map_shader.frag")
    MAP_SHADER.load_defaults_settings()

    GRID_SHADER = ShaderGL()
    GRID_SHADER.vert_shader("./GLUtilities/Shaders/grid_shader.vert")
    GRID_SHADER.frag_shader("./GLUtilities/Shaders/grid_shader.frag")
    GRID_SHADER.load_defaults_settings()

    FRAME_BUFFER_BLIT_SHADER = ShaderGL()
    FRAME_BUFFER_BLIT_SHADER.vert_shader("./GLUtilities/Shaders/frame_buffer_blit_shader.vert")
    FRAME_BUFFER_BLIT_SHADER.frag_shader("./GLUtilities/Shaders/frame_buffer_blit_shader.frag")
    FRAME_BUFFER_BLIT_SHADER.load_defaults_settings()
    #  Shader.FRAME_BUFFER_BLIT_SHADER = Shader()
    #  Shader.FRAME_BUFFER_BLIT_SHADER.vert_shader("E:/GitHub/VisualOdometry/UI/gl/shaders/frame_buffer_blit_shader.vert")
    #  Shader.FRAME_BUFFER_BLIT_SHADER.frag_shader("E:/GitHub/VisualOdometry/UI/gl/shaders/frame_buffer_blit_shader.frag")
    #  Shader.FRAME_BUFFER_BLIT_SHADER.load_defaults_settings()

    #  Shader.UI_TEXT_SHADER = Shader()
    #  Shader.UI_TEXT_SHADER.vert_shader("E:/GitHub/VisualOdometry/UI/gl/shaders/ui_text_shaders/ui_text_shader.vert")
    #  Shader.UI_TEXT_SHADER.frag_shader("E:/GitHub/VisualOdometry/UI/gl/shaders/ui_text_shaders/ui_text_shader.frag")
    #  Shader.UI_TEXT_SHADER.load_defaults_settings()

    #  Shader.UI_CLEAR_FB_SHADER = Shader()
    #  Shader.UI_CLEAR_FB_SHADER.vert_shader\
    #      ("E:/GitHub/VisualOdometry/UI/gl/shaders/ui_renderer_region_clean_up_shader.vert")
    #  Shader.UI_CLEAR_FB_SHADER.frag_shader\
    #      ("E:/GitHub/VisualOdometry/UI/gl/shaders/ui_renderer_region_clean_up_shader.frag")
    #  Shader.UI_CLEAR_FB_SHADER.load_defaults_settings()


####################################
#              SHADERS             #
####################################
WHITE_TEXTURE: TextureGL | None = None
RED_TEXTURE: TextureGL | None = None
GREEN_TEXTURE: TextureGL | None = None
BLUE_TEXTURE: TextureGL | None = None
PINK_TEXTURE: TextureGL | None = None
GRAY_TEXTURE: TextureGL | None = None


def _init_textures():
    global WHITE_TEXTURE
    global RED_TEXTURE
    global GREEN_TEXTURE
    global BLUE_TEXTURE
    global PINK_TEXTURE
    global GRAY_TEXTURE

    WHITE_TEXTURE = TextureGL(100, 100, Color(np.uint8(255), np.uint8(255), np.uint8(255)))
    WHITE_TEXTURE.name = "white"
    RED_TEXTURE = TextureGL(100, 100, Color(np.uint8(255), np.uint8(0), np.uint8(0)))
    RED_TEXTURE.name = "red"
    GREEN_TEXTURE = TextureGL(100, 100, Color(np.uint8(0), np.uint8(255), np.uint8(0)))
    GREEN_TEXTURE.name = "green"
    BLUE_TEXTURE = TextureGL(100, 100, Color(np.uint8(0), np.uint8(0), np.uint8(255)))
    BLUE_TEXTURE.name = "blue"
    PINK_TEXTURE = TextureGL(100, 100, Color(np.uint8(255), np.uint8(0), np.uint8(255)))
    PINK_TEXTURE.name = "pink"
    GRAY_TEXTURE = TextureGL(100, 100, Color(np.uint8(125), np.uint8(125), np.uint8(125)))
    GRAY_TEXTURE.name = "gray"


####################################
#              MESHES              #
####################################
PLANE_MESH: MeshGL | None = None
BOX_MESH: MeshGL | None = None
SPHERE_MESH: MeshGL | None = None


def _init_meshes():
    global PLANE_MESH
    global BOX_MESH
    global SPHERE_MESH
    PLANE_MESH = MeshGL.create_plane_gl(2.0, 2.0, 2, 2)
    BOX_MESH = MeshGL(read_obj_mesh("./GLUtilities/Resources/box.obj")[0])
    SPHERE_MESH = MeshGL(read_obj_mesh("./GLUtilities/Resources/sphere.obj")[0])


####################################
#              MESHES              #
####################################
DEFAULT_MATERIAL: ObjMaterial | None = None
MAP_MATERIAL: MapMaterial | None = None
GRID_MATERIAL: GridMaterial | None = None


def _init_materials():
    global DEFAULT_MATERIAL
    global MAP_MATERIAL
    global GRID_MATERIAL
    if DEFAULT_MATERIAL is None:
        DEFAULT_MATERIAL = ObjMaterial(SAMPLE_SHADER)  # ObjMaterial()
    if MAP_MATERIAL is None:
        MAP_MATERIAL = MapMaterial(MAP_SHADER)
    if GRID_MATERIAL is None:
        GRID_MATERIAL = GridMaterial(GRID_SHADER)


####################################
#             CAMERAS              #
####################################
MAIN_CAMERA: Camera | None = None

####################################
#              MOUSE               #
####################################
MOUSE_CONTROLLER: MouseController | None = None

####################################
#             KEYBOARD             #
####################################
KEYBOARD_CONTROLLER: KeyboardController | None = None


def init():
    global MAIN_CAMERA
    global MOUSE_CONTROLLER
    global KEYBOARD_CONTROLLER
    if MOUSE_CONTROLLER is None:
        MOUSE_CONTROLLER = MouseController()
    if KEYBOARD_CONTROLLER is None:
        KEYBOARD_CONTROLLER = KeyboardController()
    if MAIN_CAMERA is None:
        MAIN_CAMERA = Camera()
    _init_textures()
    _init_shaders()
    _init_meshes()
    _init_materials()


def free():
    # BufferGL.buffers.write_all_instances()
    # ShaderGL.shaders.write_all_instances()
    TextureGL.textures.delete_all()
    ShaderGL.shaders.delete_all()
    MeshGL.meshes.delete_all()
    FrameBufferGL.frame_buffers.delete_all()



