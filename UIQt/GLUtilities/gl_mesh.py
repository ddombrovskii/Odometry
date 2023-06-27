from UIQt.GLUtilities.triangle_mesh import TrisMesh, create_plane, create_box
from Utilities.Geometry import Transform, BoundingBox, Vector3
from UIQt.GLUtilities.gl_decorators import gl_error_catch
from UIQt.GLUtilities.objects_pool import ObjectsPool
from UIQt.GLUtilities.gl_buffer import BufferGL
from Utilities import BitSet32
from OpenGL.GL import *
import numpy as np


class MeshGL:
    VerticesAttribute = 0  # 1
    NormalsAttribute = 1  # 2
    TangentsAttribute = 2  # 3
    UVsAttribute = 3  # 8
    TrianglesAttribute = 4  # 16

    meshes = ObjectsPool()

    @classmethod
    def create_box_gl(cls, side: float = 1.0, transform: Transform = None):
        return cls(create_box(Vector3(-side * 0.5, -side * 0.5, -side * 0.5),
                              Vector3(side * 0.5, side * 0.5, side * 0.5), transform))

    @classmethod
    def create_plane_gl(cls, height: float = 1.0, width: float = 1.0, rows: int = 10, cols: int = 10,
                        transform: Transform = None):
        return cls(create_plane(height, width, rows, cols, transform))

    def __repr__(self):
        return f"{{\n" \
               f"\t\"name\"           :\"{self.name}\",\n" \
               f"\t\"vao_id\"         :{self._vao},\n" \
               f"\t\"ibo_id\"         :{self._vbo.bind_id},\n" \
               f"\t\"vbo_id\"         :{self._ibo.bind_id},\n" \
               f"\t\"bytes_per_vert\" :{self._vertex_byte_size},\n" \
               f"\t\"attributes\"     :{self._vertex_attributes.state}\n}}"

    def __str__(self):
        return f"{{\n" \
               f"\t\"name\"   :\"{self.name}\",\n" \
               f"\t\"source\" :\"{self.source}\"" \
               f"\n}}"

    def __init__(self, mesh: TrisMesh = None):
        self._name: str = ""
        self._source: str = ""
        self._bounds: BoundingBox = BoundingBox()
        self._vao: int = 0
        self._vbo: BufferGL | None = None
        self._ibo: BufferGL | None = None
        self._instance_buffer: BufferGL | None = None
        self._vertex_attributes: BitSet32 = BitSet32()
        self._vertex_byte_size = 0
        if not (mesh is None):
            if self._create_gpu_buffers(mesh):
                self.name = f"gl_mesh_{self.bind_id}"
                self.name = f"{mesh.name}_{self.bind_id}"
                self._source = mesh.source
            return
        self.name = f"gl_mesh_{self.bind_id}"

    def __del__(self):
        self.delete()

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def __call__(self, *args, **kwargs):
        with self:
            self.draw()

    @property
    def source(self) -> str:
        return self._source

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not MeshGL.meshes.check_if_name_valid(value):
            return
        MeshGL.meshes.unregister_object(self)
        self._name = value
        MeshGL.meshes.register_object(self)

    @property
    def bounds(self) -> BoundingBox:
        return self._bounds

    @property
    def vbo(self) -> BufferGL:
        return self._vbo

    @property
    def ibo(self) -> BufferGL:
        return self._ibo

    @property
    def bind_id(self) -> int:
        return self._vao

    @property
    def has_vertices(self):
        return self._vertex_attributes.is_bit_set(MeshGL.VerticesAttribute)

    @property
    def has_normals(self):
        return self._vertex_attributes.is_bit_set(MeshGL.NormalsAttribute)

    @property
    def has_uvs(self):
        return self._vertex_attributes.is_bit_set(MeshGL.UVsAttribute)

    @property
    def has_tangents(self):
        return self._vertex_attributes.is_bit_set(MeshGL.TangentsAttribute)

    @property
    def has_triangles(self):
        return self._vertex_attributes.is_bit_set(MeshGL.TrianglesAttribute)

    @gl_error_catch
    def _gen_vao(self):
        if self._vao == 0:
            self._vao = glGenVertexArrays(1)
            MeshGL.meshes.register_object(self)
            self._vertex_byte_size = 0
        self.bind()

    @gl_error_catch
    def _create_gpu_buffers(self, mesh: TrisMesh) -> bool:
        if mesh.vertices_count == 0:
            return False
        if mesh.faces_count == 0:
            return False
        self._vertex_attributes.set_bit(MeshGL.VerticesAttribute )
        self._vertex_attributes.set_bit(MeshGL.NormalsAttribute  )
        self._vertex_attributes.set_bit(MeshGL.UVsAttribute      )
        self._vertex_attributes.set_bit(MeshGL.TrianglesAttribute)
        self._gen_vao()
        self._bounds.reset()
        self._bounds.encapsulate(mesh.bbox.max)
        self._bounds.encapsulate(mesh.bbox.min)
        self.vertices_array = mesh.vertex_array_data
        self.indices_array = mesh.index_array_data
        self.set_attributes(self._vertex_attributes)

        return True

    @gl_error_catch
    def delete(self):
        if self._vao == 0:
            return
        glDeleteVertexArrays(1, np.ndarray([self._vao]))
        self._vbo.delete()
        self._ibo.delete()
        MeshGL.meshes.unregister_object(self)
        self._vao = 0

    @property
    def indices_array(self) -> np.ndarray:
        return self._ibo.read_back_data()

    @indices_array.setter
    def indices_array(self, indices: np.ndarray) -> None:
        self._gen_vao()
        if self._ibo is None:
            self._ibo = BufferGL(len(indices), int(indices.nbytes / len(indices)), GL_ELEMENT_ARRAY_BUFFER)
        self._ibo.load_buffer_data(indices)

    @property
    def vertices_array(self) -> np.ndarray:
        return self._vbo.read_back_data()

    @vertices_array.setter
    def vertices_array(self, vertices: np.ndarray) -> None:
        self._gen_vao()
        if self._vbo is None:
            self._vbo = BufferGL(len(vertices), int(vertices.nbytes / len(vertices)), GL_ARRAY_BUFFER)
        self._vbo.load_buffer_data(vertices)

    @gl_error_catch
    def set_attributes(self, attributes: BitSet32):
        if self._vao == 0:
            return
        if self._vbo is None:
            return
        self._vertex_byte_size = 0
        self._vertex_attributes = attributes
        if attributes.is_bit_set(MeshGL.VerticesAttribute):
            self._vertex_byte_size += 3
        if attributes.is_bit_set(MeshGL.NormalsAttribute):
            self._vertex_byte_size += 3
        if attributes.is_bit_set(MeshGL.TangentsAttribute):
            self._vertex_byte_size += 3
        if attributes.is_bit_set(MeshGL.UVsAttribute):
            self._vertex_byte_size += 2
        ptr = 0
        attr_i = 0
        d_ptr = int(self.vbo.filling / self._vertex_byte_size)
        self.vbo.bind()
        if self.has_vertices:
            glEnableVertexAttribArray(attr_i)
            glVertexAttribPointer(attr_i, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(ptr))
            ptr += d_ptr * 12
            attr_i += 1

        if self.has_normals:
            glEnableVertexAttribArray(attr_i)
            glVertexAttribPointer(attr_i, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(ptr))
            ptr += d_ptr * 12
            attr_i += 1

        if self.has_tangents:
            glEnableVertexAttribArray(attr_i)
            glVertexAttribPointer(attr_i, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(ptr))
            ptr += d_ptr * 12
            attr_i += 1

        if self.has_uvs:
            glEnableVertexAttribArray(attr_i)
            glVertexAttribPointer(attr_i, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(ptr))

    def clean_up(self):
        self.vbo.delete()
        self.ibo.delete()

    def bind(self):
        if not MeshGL.meshes.bounded_update(self.bind_id):
            return
        glBindVertexArray(self._vao)

    def unbind(self):
        glBindVertexArray(0)
        MeshGL.meshes.bounded_update(0)

    def draw(self):
        self.bind()
        glDrawElements(GL_TRIANGLES, self.ibo.filling, GL_UNSIGNED_INT, None)
