from UIQt.GLUtilities.gl_buffer import BufferGL
from OpenGL.GL import *
import numpy as np

from UIQt.GLUtilities.triangle_mesh import TrisMesh, create_plane, create_box
from Utilities import Transform, BitSet32, BoundingBox


class MeshGL:

    VerticesAttribute = 0  # 1
    NormalsAttribute = 1   # 2
    TangentsAttribute = 2  # 3
    UVsAttribute = 3       # 8
    TrianglesAttribute = 4 # 16

    __mesh_bounded: int = -1

    __vao_instances = {}

    PLANE_MESH = None
    BOX_MESH = None

    @staticmethod
    def init_globals():
        MeshGL.PLANE_MESH = MeshGL.create_plane_gl(2.0, 2.0, 2, 2)
        MeshGL.BOX_MESH = MeshGL.create_box_gl()

    @classmethod
    def create_box_gl(cls, side: float = 1.0, transform: Transform = None):
        return cls(create_box(side, transform))

    @classmethod
    def create_plane_gl(cls, height: float = 1.0, width: float = 1.0, rows: int = 10, cols: int = 10,
                        transform: Transform = None):
        return cls(create_plane(height, width, rows, cols, transform))

    @staticmethod
    def vao_enumerate():
        print(MeshGL.__vao_instances.items())
        for buffer in MeshGL.__vao_instances.items():
            yield buffer[1]

    @staticmethod
    def meshes_write(file, start="", end=""):
        file.write(f"{start}\"meshes\":[\n")
        file.write(',\n'.join(str(m) for m in MeshGL.__vao_instances.values()))
        file.write(f"]\n{end}")

    @staticmethod
    def delete_all_meshes():
        while len(MeshGL.__vao_instances) != 0:
            item = MeshGL.__vao_instances.popitem()
            item[1].delete_mesh()

    def __str__(self):
        return f"{{\n" \
               f"\t\"unique_id\"      :{self.__vao},\n" \
               f"\t\"vao_id\"         :{self.__vao},\n" \
               f"\t\"ibo_id\"         :{self.__vbo.buffer_id},\n" \
               f"\t\"vbo_id\"         :{self.__ibo.buffer_id},\n" \
               f"\t\"bytes_per_vert\" :{self.__vertex_byte_size},\n"\
               f"\t\"attribytes\"     :{self.__vertex_attributes.state}\n}}"

    def __init__(self, mesh: TrisMesh = None):
        self.__unique_id = id(self)
        self.__bounds: BoundingBox = BoundingBox()
        self.__vao: int = 0
        self.__vbo = None
        self.__ibo = None
        self.__instance_buffer = None
        self.__vertex_attributes: BitSet32 = BitSet32()
        self.__vertex_byte_size = 0
        if not(mesh is None):
            self.__create_gpu_buffers(mesh)

    def __del__(self):
        self.delete_mesh()

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def __call__(self, *args, **kwargs):
        with self:
            self.draw()

    @property
    def bounds(self) -> BoundingBox:
        return self.__bounds

    @property
    def vbo(self) -> BufferGL:
        return self.__vbo

    @property
    def ibo(self) -> BufferGL:
        return self.__ibo

    @property
    def unique_id(self) -> int:
        return self.__unique_id

    @property
    def has_vertices(self):
        return self.__vertex_attributes.is_bit_set(MeshGL.VerticesAttribute)

    @property
    def has_normals(self):
        return self.__vertex_attributes.is_bit_set(MeshGL.NormalsAttribute)

    @property
    def has_uvs(self):
        return self.__vertex_attributes.is_bit_set(MeshGL.UVsAttribute)

    @property
    def has_tangents(self):
        return self.__vertex_attributes.is_bit_set(MeshGL.TangentsAttribute)

    @property
    def has_triangles(self):
        return self.__vertex_attributes.is_bit_set(MeshGL.TrianglesAttribute)

    def set_mesh(self, m: TrisMesh) -> None:
        if self.__vao != 0:
            self.delete_mesh()
        self.__create_gpu_buffers(m)

    def __del__(self):
        self.delete_mesh()

    def __gen_vao(self):
        if self.__vao == 0:
            self.__vao = glGenVertexArrays(1)
            MeshGL.__vao_instances[self.__vao] = self
            self.__vertex_byte_size = 0

        self.bind()

    def __create_gpu_buffers(self, mesh: TrisMesh) -> bool:

        if mesh.vertices_count == 0:
            return False
        if mesh.faces_count == 0:
            return False

        self.__vertex_attributes.set_bit(MeshGL.VerticesAttribute)
        self.__vertex_attributes.set_bit(MeshGL.NormalsAttribute)
        self.__vertex_attributes.set_bit(MeshGL.UVsAttribute)
        self.__vertex_attributes.set_bit(MeshGL.TrianglesAttribute)

        self.__gen_vao()

        self.__bounds.reset()

        self.__bounds.encapsulate(mesh.bbox.max)

        self.__bounds.encapsulate(mesh.bbox.min)

        self.vertices_array = mesh.vertex_array_data

        self.indices_array = mesh.index_array_data

        self.set_attributes(self.__vertex_attributes)

        return True

    def delete_mesh(self):
        if self.__vao == 0:
            return
        glDeleteVertexArrays(1, np.ndarray([self.__vao]))
        self.__vbo.delete_buffer()
        self.__ibo.delete_buffer()
        if self.__vao in MeshGL.__vao_instances:
            del MeshGL.__vao_instances[self.__vao]
        self.__vao = 0

    @property
    def indices_array(self) -> np.ndarray:
        return self.__ibo.read_back_data()

    @indices_array.setter
    def indices_array(self, indices: np.ndarray) -> None:
        self.__gen_vao()
        if self.__ibo is None:
            self.__ibo = BufferGL(len(indices), int(indices.nbytes / len(indices)), GL_ELEMENT_ARRAY_BUFFER)
        self.__ibo.load_buffer_data(indices)

    @property
    def vertices_array(self) -> np.ndarray:
        return self.__vbo.read_back_data()

    @vertices_array.setter
    def vertices_array(self, vertices: np.ndarray) -> None:
        self.__gen_vao()
        if self.__vbo is None:
            self.__vbo = BufferGL(len(vertices), int(vertices.nbytes / len(vertices)), GL_ARRAY_BUFFER)
        self.__vbo.load_buffer_data(vertices)

    def set_attributes(self, attributes: BitSet32):

        if self.__vao == 0:
            return

        if self.__vbo is None:
            return

        self.__gen_vao()

        self.__vertex_byte_size = 0

        self.__vertex_attributes = attributes

        if attributes.is_bit_set(MeshGL.VerticesAttribute):
            self.__vertex_byte_size += 3

        if attributes.is_bit_set(MeshGL.NormalsAttribute):
            self.__vertex_byte_size += 3

        if attributes.is_bit_set(MeshGL.TangentsAttribute):
            self.__vertex_byte_size += 3

        if attributes.is_bit_set(MeshGL.UVsAttribute):
            self.__vertex_byte_size += 2

        ptr = 0

        attr_i = 0

        d_ptr = int(self.__vbo.filling / self.__vertex_byte_size)

        self.__vbo.bind()

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
        self.__vbo.delete_buffer()
        self.__ibo.delete_buffer()

    def bind(self):
        #if self.unique_id == MeshGL.__mesh_bounded:
        #    return
        #MeshGL.__mesh_bounded = self.unique_id
        glBindVertexArray(self.__vao)

    def unbind(self):
        glBindVertexArray(0)

    def draw(self):
        self.bind()
        glDrawElements(GL_TRIANGLES, self.__ibo.filling, GL_UNSIGNED_INT, None)
