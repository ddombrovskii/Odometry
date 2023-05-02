from UIQt.GLUtilities import gl_globals
from UIQt.GLUtilities.gl_material import MaterialGL
from UIQt.GLUtilities.gl_mesh import MeshGL
from Utilities.Geometry import Transform


class ModelGL:
    def __init__(self):
        self._mesh: MeshGL         = gl_globals.BOX_MESH
        self._material: MaterialGL = gl_globals.DEFAULT_MATERIAL
        self._transform: Transform = Transform()

    @property
    def mesh(self) -> MeshGL:
        return self._mesh

    @mesh.setter
    def mesh(self, m: MeshGL) -> None:
        self._mesh = gl_globals.BOX_MESH if m is None else m

    @property
    def material(self) -> MaterialGL:
        return self._material

    @material.setter
    def material(self, m: MeshGL) -> None:
        self._material = MaterialGL.DEFAULT_MATERIAL if m is None else m

    @property
    def transform(self) -> Transform:
        return self._transform
