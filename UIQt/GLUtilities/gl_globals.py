from UIQt.GLUtilities.Materials.grid_material import GridMaterial
from UIQt.GLUtilities.Materials.map_material import MapMaterial
from UIQt.GLUtilities.Materials.obj_material import ObjMaterial
from UIQt.GLUtilities.gl_buffer import BufferGL
from UIQt.GLUtilities.gl_camera import CameraGL
from UIQt.GLUtilities.gl_frame_buffer import FrameBufferGL
from UIQt.GLUtilities.triangle_mesh import read_obj_mesh
from UIQt.GLUtilities.gl_texture import TextureGL
from UIQt.GLUtilities.gl_shader import ShaderGL
from UIQt.GLUtilities.gl_mesh import MeshGL
from UIQt.Input.keyboard_controller import KeyboardController
from UIQt.Input.mouse_controller import MouseController
from Utilities import Color
import numpy as np


####################################
#              SHADERS             #
####################################
SAMPLE_SHADER = None
MAP_SHADER = None
GRID_SHADER = None
FRAME_BUFFER_BLIT_SHADER = None

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
WHITE_TEXTURE = None
RED_TEXTURE = None
GREEN_TEXTURE = None
BLUE_TEXTURE = None
PINK_TEXTURE = None
GRAY_TEXTURE = None


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
PLANE_MESH = None
BOX_MESH = None
SPHERE_MESH = None


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
DEFAULT_MATERIAL: ObjMaterial = None
MAP_MATERIAL: MapMaterial = None
GRID_MATERIAL: GridMaterial = None


def _init_materials():
    global DEFAULT_MATERIAL
    global MAP_MATERIAL
    global GRID_MATERIAL
    DEFAULT_MATERIAL = ObjMaterial(SAMPLE_SHADER)  # ObjMaterial()
    MAP_MATERIAL = MapMaterial(MAP_SHADER)
    GRID_MATERIAL = GridMaterial(GRID_SHADER)


####################################
#             CAMERAS              #
####################################
MAIN_CAMERA: CameraGL = None

####################################
#              MOUSE               #
####################################
MOUSE_CONTROLLER: MouseController = None

####################################
#             KEYBOARD             #
####################################
KEYBOARD_CONTROLLER: KeyboardController = None


def init():
    global MAIN_CAMERA
    global MOUSE_CONTROLLER
    global KEYBOARD_CONTROLLER
    MOUSE_CONTROLLER = MouseController()
    KEYBOARD_CONTROLLER = KeyboardController()
    MAIN_CAMERA = CameraGL()
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



