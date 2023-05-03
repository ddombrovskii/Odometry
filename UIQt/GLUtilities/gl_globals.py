from UIQt.GLUtilities.Materials.grid_material import GridMaterial
from UIQt.GLUtilities.Materials.map_material import MapMaterial
from UIQt.GLUtilities.Materials.obj_material import ObjMaterial
from UIQt.GLUtilities.triangle_mesh import read_obj_mesh
from UIQt.GLUtilities.gl_material import MaterialGL
from UIQt.GLUtilities.gl_texture import TextureGL
from UIQt.GLUtilities.gl_shader import Shader
from UIQt.GLUtilities.gl_mesh import MeshGL
from Utilities import Color
import numpy as np


####################################
#              SHADERS             #
####################################
SAMPLE_SHADER = None
MAP_SHADER = None
# UI_TEXT_SHADER = None
# UI_CLEAR_FB_SHADER = None
# FRAME_BUFFER_BLIT_SHADER = None


def _init_shaders():
    global SAMPLE_SHADER
    global MAP_SHADER

    SAMPLE_SHADER = Shader()
    SAMPLE_SHADER.vert_shader("./GLUtilities/Shaders/sample_shader.vert")
    SAMPLE_SHADER.frag_shader("./GLUtilities/Shaders/sample_shader.frag")
    SAMPLE_SHADER.load_defaults_settings()

    MAP_SHADER = Shader()
    MAP_SHADER.vert_shader("./GLUtilities/Shaders/map_shader.vert")
    MAP_SHADER.frag_shader("./GLUtilities/Shaders/map_shader.frag")
    MAP_SHADER.load_defaults_settings()

    #  Shader.FRAME_BUFFER_BLIT_SHADER = Shader()
    #  Shader.FRAME_BUFFER_BLIT_SHADER.vert_shader("E:/GitHub/VisualOdometry/UI/gl/shaders/ui_render_shader.vert")
    #  Shader.FRAME_BUFFER_BLIT_SHADER.frag_shader("E:/GitHub/VisualOdometry/UI/gl/shaders/ui_render_shader.frag")
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
CARBON_TEXTURE = None


def _init_textures():
    global WHITE_TEXTURE
    global RED_TEXTURE
    global GREEN_TEXTURE
    global BLUE_TEXTURE
    global PINK_TEXTURE
    global GRAY_TEXTURE
    global CARBON_TEXTURE
    global CARBON_TEXTURE

    WHITE_TEXTURE = TextureGL(100, 100, Color(np.uint8(255), np.uint8(255), np.uint8(255)))
    RED_TEXTURE = TextureGL(100, 100, Color(np.uint8(255), np.uint8(0), np.uint8(0)))
    GREEN_TEXTURE = TextureGL(100, 100, Color(np.uint8(0), np.uint8(255), np.uint8(0)))
    BLUE_TEXTURE = TextureGL(100, 100, Color(np.uint8(0), np.uint8(0), np.uint8(255)))
    PINK_TEXTURE = TextureGL(100, 100, Color(np.uint8(255), np.uint8(0), np.uint8(255)))
    GRAY_TEXTURE = TextureGL(100, 100, Color(np.uint8(125), np.uint8(125), np.uint8(125)))
    CARBON_TEXTURE = TextureGL()
    CARBON_TEXTURE.load(r'./GLUtilities/Resources/carbon.jpg')


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
DEFAULT_MATERIAL = None
MAP_MATERIAL = None


def _init_materials():
    global DEFAULT_MATERIAL
    global MAP_MATERIAL
    DEFAULT_MATERIAL = MapMaterial(MAP_SHADER)  # ObjMaterial()
    MAP_MATERIAL = MapMaterial(MAP_SHADER)


def init():
    _init_textures()
    _init_shaders()
    _init_meshes()
    _init_materials()


def free():
    TextureGL.delete_all()
    Shader.delete_all()
    MeshGL.delete_all()


