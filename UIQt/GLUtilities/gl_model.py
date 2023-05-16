from UIQt.GLUtilities.gl_material import MaterialGL
from UIQt.GLUtilities.gl_mesh import MeshGL
from UIQt.GLUtilities.objects_pool import ObjectsPool
from Utilities.Geometry import Transform
from UIQt.GLUtilities import gl_globals


class ModelGL:

    models = ObjectsPool()

    def __init__(self):
        self._id = id(self)
        self._mesh: MeshGL = gl_globals.BOX_MESH
        self._name = self._mesh.name
        self._material: MaterialGL = gl_globals.DEFAULT_MATERIAL
        self._transform: Transform = Transform()
        ModelGL.models.register_object(self)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not ModelGL.models.check_if_name_valid(value):
            return
        ModelGL.models.unregister_object(self)
        self._name = value
        ModelGL.models.register_object(self)

    @property
    def bind_id(self) -> int:
        return self._id

    @property
    def mesh(self) -> MeshGL:
        return self._mesh

    @mesh.setter
    def mesh(self, m: MeshGL) -> None:
        self._mesh = gl_globals.BOX_MESH if m is None else m
        self.name = self._mesh.name

    @property
    def material(self) -> MaterialGL:
        return self._material

    @material.setter
    def material(self, m: MeshGL) -> None:
        self._material = gl_globals.DEFAULT_MATERIAL if m is None else m

    @property
    def transform(self) -> Transform:
        return self._transform
