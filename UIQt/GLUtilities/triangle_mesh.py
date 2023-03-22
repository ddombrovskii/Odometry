from Utilities import Vector3, BoundingBox, Transform
from Utilities import Vector2
from typing import Tuple, List, Union
import numpy as np
import re


class Face:
    __slots__ = "__p_1", "__p_2", "__p_3", "__uv1", "__uv2", "__uv3", "__n_1", "__n_2", "__n_3"

    def __init__(self, p1=None, uv1=None, n1=None, p2=None, uv2=None, n2=None, p3=None, uv3=None, n3=None):
        self.__p_1: int = -1 if p1 is None else p1
        self.__uv1: int = -1 if uv1 is None else uv1
        self.__n_1: int = -1 if n1 is None else n1

        self.__p_2: int = -1 if p2 is None else p2
        self.__uv2: int = -1 if uv2 is None else uv2
        self.__n_2: int = -1 if n2 is None else n2

        self.__p_3: int = -1 if p3 is None else p3
        self.__uv3: int = -1 if uv3 is None else uv3
        self.__n_3: int = -1 if n3 is None else n3

    def __str__(self):
        return f"{{" \
               f"\t\"p_1\": {self.p_1:4}, \"uv1\": {self.uv1:4}, \"n_1\": {self.n_1:4}," \
               f"\t\"p_2\": {self.p_2:4}, \"uv2\": {self.uv2:4}, \"n_2\": {self.n_2:4}," \
               f"\t\"p_3\": {self.p_3:4}, \"uv3\": {self.uv3:4}, \"n_3\": {self.n_3:4}" \
               f"}}"

    @property
    def points(self):
        yield self.pt_1
        yield self.pt_2
        yield self.pt_3

    @property
    def pt_1(self) -> Tuple[int, int, int]:
        return self.__p_1, self.__n_1, self.__uv1

    @property
    def pt_2(self) -> Tuple[int, int, int]:
        return self.__p_2, self.__n_2, self.__uv2

    @property
    def pt_3(self) -> Tuple[int, int, int]:
        return self.__p_3, self.__n_3, self.__uv3

    @property
    def p_1(self) -> int:
        return self.__p_1

    @p_1.setter
    def p_1(self, val: int) -> None:
        self.__p_1 = max(0, val)

    @property
    def n_1(self) -> int:
        return self.__n_1

    @n_1.setter
    def n_1(self, val: int) -> None:
        self.__n_1 = max(0, val)

    @property
    def uv1(self) -> int:
        return self.__uv1

    @uv1.setter
    def uv1(self, val: int) -> None:
        self.__uv1 = max(0, val)

    @property
    def p_2(self) -> int:
        return self.__p_2

    @p_2.setter
    def p_2(self, val: int) -> None:
        self.__p_2 = max(0, val)

    @property
    def n_2(self) -> int:
        return self.__n_2

    @n_2.setter
    def n_2(self, val: int) -> None:
        self.__n_2 = max(0, val)

    @property
    def uv2(self) -> int:
        return self.__uv2

    @uv2.setter
    def uv2(self, val: int) -> None:
        self.__uv2 = max(0, val)

    @property
    def p_3(self) -> int:
        return self.__p_3

    @p_3.setter
    def p_3(self, val: int) -> None:
        self.__p_3 = max(0, val)

    @property
    def n_3(self) -> int:
        return self.__n_3

    @n_3.setter
    def n_3(self, val: int) -> None:
        self.__n_3 = max(0, val)

    @property
    def uv3(self) -> int:
        return self.__uv3

    @uv3.setter
    def uv3(self, val: int) -> None:
        self.__uv3 = max(0, val)

    def index1(self, index) -> None:
        self.__p_1 = index
        self.__uv1 = index
        self.__n_1 = index

    def index2(self, index) -> None:
        self.__p_2 = index
        self.__uv2 = index
        self.__n_2 = index

    def index3(self, index) -> None:
        self.__p_3 = index
        self.__uv3 = index
        self.__n_3 = index


class TrisMesh:

    __slots__ = "name", "_vertices", "_normals", "_uvs", "_faces", "_bbox"

    def __init__(self):
        self.name: str = "no name"
        self._vertices: List[Vector3] = []
        self._normals: List[Vector3] = []
        self._uvs: List[Vector2] = []
        self._faces: List[Face] = []
        self._bbox: BoundingBox = BoundingBox()

    def __str__(self):
        new_l = ",\n\t\t"
        return f"{{\n" \
               f"\t\"name\"     :\"{self.name}\",\n" \
               f"\t\"unique_id\":{self.unique_id},\n" \
               f"\t\"bounds\"   :\n{self._bbox},\n" \
               f"\t\"vertices\" :\n\t[\n\t\t{new_l.join(str(v) for v in self._vertices)}\n\t],\n" \
               f"\t\"normals\"  :\n\t[\n\t\t{new_l.join(str(v) for v in self._normals)}\n\t],\n" \
               f"\t\"uvs\"      :\n\t[\n\t\t{new_l.join(str(v) for v in self._uvs)}\n\t],\n" \
               f"\t\"faces\"    :\n\t[\n\t\t{new_l.join(str(v) for v in self._faces)}\n\t]\n" \
               f"}}"

    @property
    def unique_id(self) -> int:
        return id(self)

    @property
    def vertex_array_data(self) -> np.ndarray:
        size_ = self.vertices_count * 8
        v_data = np.zeros(size_, dtype=np.float32)
        unique_vert_id = {}
        for f in self.faces:
            for pt in f.points:
                if not(pt[0] in unique_vert_id):
                    if pt[0] != -1:
                        v = self.vertices[pt[0]]
                        idx = pt[0] * 3
                        v_data[idx + 0] = v.x
                        v_data[idx + 1] = v.y
                        v_data[idx + 2] = v.z

                    if pt[1] != -1:
                        n = self.normals[pt[1]]
                        idx = self.vertices_count * 3 + pt[0] * 3
                        v_data[idx + 0] = n.x
                        v_data[idx + 1] = n.y
                        v_data[idx + 2] = n.z

                    if pt[2] != -1:
                        uv = self.uvs[pt[2]]
                        idx = self.vertices_count * 6 + pt[0] * 2
                        v_data[idx + 0] = uv.x
                        v_data[idx + 1] = uv.y
                    unique_vert_id[pt[0]] = pt[0]

        return v_data

    @property
    def index_array_data(self) -> np.ndarray:
        i_data = np.zeros(self.faces_count * 3, dtype=np.uint32)
        idx: int = 0
        for f in self.faces:
            i_data[idx + 0] = f.p_1
            i_data[idx + 1] = f.p_2
            i_data[idx + 2] = f.p_3
            idx += 3
        return i_data

    @property
    def vertices(self) -> List[Vector3]:
        return self._vertices

    @property
    def normals(self) -> List[Vector3]:
        return self._normals

    @property
    def uvs(self) -> List[Vector2]:
        return self._uvs

    @property
    def faces(self) -> List[Face]:
        return self._faces

    @property
    def faces_count(self) -> int:
        return len(self._faces)

    @property
    def vertices_count(self) -> int:
        return len(self._vertices)

    @property
    def uvs_count(self) -> int:
        return len(self._uvs)

    @property
    def normals_count(self) -> int:
        return len(self._normals)

    @property
    def bbox(self) -> BoundingBox:
        return self._bbox

    def set_vertex(self, i_id: int, v: Union[Vector3, Tuple[float, float, float]]) -> None:
        if i_id < 0:
            return

        if i_id >= self.vertices_count:
            return

        if isinstance(v, tuple):
            _v = Vector3(v[0], v[1], v[2])
            self._bbox.encapsulate(_v)
            self._vertices[i_id] = _v
            return

        self._bbox.encapsulate(v)
        self._vertices[i_id] = v

    def set_normal(self, i_id: int, v: Union[Vector3, Tuple[float, float, float]]) -> None:
        if i_id < 0:
            return

        if i_id >= self.normals_count:
            return

        if isinstance(v, tuple):
            self._normals[i_id] = Vector3(v[0], v[1], v[2])
            return

        self._normals[i_id] = v

    def set_uv(self, i_id: int, v: Union[Vector3, Tuple[float, float]]) -> None:
        if i_id < 0:
            return

        if i_id >= self.uvs_count:
            return

        if isinstance(v, tuple):
            self._uvs[i_id] = Vector3(v[0], v[1])
            return

        self._uvs[i_id] = v

    def append_vertex(self, v: Union[Vector3, Tuple[float, float, float]]) -> None:
        if isinstance(v, tuple):
            v_ = Vector3(v[0], v[1], v[2])
            self._bbox.encapsulate(v_)
            self._vertices.append(v_)
            return
        self._bbox.encapsulate(v)
        self._vertices.append(v)

    def append_normal(self, v: Union[Vector3, Tuple[float, float, float]]) -> None:
        if isinstance(v, tuple):
            self._normals.append(Vector3(v[0], v[1], v[2]))
            return
        self._normals.append(v)

    def append_uv(self, v: Union[Vector2, Tuple[float, float]]) -> None:
        if isinstance(v, tuple):
            self._uvs.append(Vector2(v[0], v[1]))
            return
        self._uvs.append(v)

    def append_face(self, f: Union[Face, Tuple[int, int, int]]) -> None:
        if isinstance(f, tuple):
            _f = Face()
            _f.index1(f[0])
            _f.index2(f[1])
            _f.index3(f[2])
            self._faces.append(_f)
            return

        self._faces.append(f)

    def clean_up(self) -> None:
        if len(self._vertices) == 0:
            return
        del self._uvs
        del self._vertices
        del self._normals
        del self._faces

        self._uvs: List[Vector2] = []
        self._vertices: List[Vector3] = []
        self._normals: List[Vector3] = []
        self._faces: List[Face] = []

    def transform_mesh(self, transform: Transform = None) -> None:
        for i in range(len(self._vertices)):
            self._vertices[i] = transform.transform_vect(self._vertices[i], 1.0)

        for i in range(len(self._normals)):
            self._normals[i] = transform.transform_vect(self._normals[i], 0.0)

    def merge(self, other):
        v_offset = self.vertices_count
        uv_offset = self.uvs_count
        n_offset = self.normals_count

        for p in other.vertices:
            self.append_vertex(p)

        for n in other.normals:
            self.append_normal(n)

        for uv in other.uvs:
            self.append_uv(uv)

        for face in other.faces:
            _face = Face()
            _face.p_1 = face.p_1 + v_offset
            _face.p_2 = face.p_2 + v_offset
            _face.p_3 = face.p_3 + v_offset

            _face.n_1 = face.n_1 + n_offset
            _face.n_2 = face.n_2 + n_offset
            _face.n_3 = face.n_3 + n_offset

            _face.uv1 = face.uv1 + uv_offset
            _face.uv2 = face.uv2 + uv_offset
            _face.uv3 = face.uv3 + uv_offset
            self.append_face(_face)

        return self


def read_obj_mesh(path: str) -> List[TrisMesh]:
    try:
        with open(path, mode='r') as file:

            tmp: List[str]
            tmp2: List[str]
            id_: int

            meshes: List[TrisMesh] = []
            uv_shift: int = 0
            v__shift: int = 0
            n__shift: int = 0

            for str_ in file:

                line = (re.sub(r"[\n\t]*", "", str_))

                if len(line) == 0:
                    continue

                tmp = line.strip().split()

                id_ = len(tmp) - 1

                if id_ == -1:
                    continue

                if tmp[0] == "#":
                    if id_ == 0:
                        continue

                    if not (tmp[1] == "object"):
                        continue

                    mesh: TrisMesh = TrisMesh()
                    mesh.name = tmp[2]
                    meshes.append(mesh)
                    if len(meshes) == 1:
                        continue
                    uv_shift += meshes[len(meshes) - 2].uvs_count
                    v__shift += meshes[len(meshes) - 2].vertices_count
                    n__shift += meshes[len(meshes) - 2].normals_count
                    continue

                if tmp[0] == "o":
                    mesh: TrisMesh = TrisMesh()
                    mesh.name = tmp[1]
                    meshes.append(mesh)
                    if len(meshes) == 1:
                        continue
                    uv_shift += meshes[len(meshes) - 2].uvs_count
                    v__shift += meshes[len(meshes) - 2].vertices_count
                    n__shift += meshes[len(meshes) - 2].normals_count
                    continue

                if tmp[0] == "vn":
                    meshes[len(meshes) - 1].append_normal(
                        Vector3(float(tmp[id_ - 2]), float(tmp[id_ - 1]), float(tmp[id_])))
                    continue

                if tmp[0] == "v":
                    meshes[len(meshes) - 1].append_vertex(
                        Vector3(float(tmp[id_ - 2]), float(tmp[id_ - 1]), float(tmp[id_])))
                    continue

                if tmp[0] == "vt":
                    meshes[len(meshes) - 1].append_uv(Vector2(float(tmp[id_ - 1]), float(tmp[id_])))
                    continue

                if tmp[0] == "f":
                    tmp2 = tmp[1].strip().split("/")
                    face_ = Face()
                    face_.p_1 = int(tmp2[0]) - 1 - v__shift
                    face_.uv1 = int(tmp2[1]) - 1 - uv_shift
                    face_.n_1 = int(tmp2[2]) - 1 - n__shift

                    tmp2 = tmp[2].split("/")
                    face_.p_2 = int(tmp2[0]) - 1 - v__shift
                    face_.uv2 = int(tmp2[1]) - 1 - uv_shift
                    face_.n_2 = int(tmp2[2]) - 1 - n__shift

                    tmp2 = tmp[3].split("/")
                    face_.p_3 = int(tmp2[0]) - 1 - v__shift
                    face_.uv3 = int(tmp2[1]) - 1 - uv_shift
                    face_.n_3 = int(tmp2[2]) - 1 - n__shift
                    meshes[len(meshes) - 1].append_face(face_)
                    continue
            return meshes
    except IOError:
        print(f"file: \"{path}\" not found")
        return []


def write_obj_mesh(mesh: TrisMesh, path: str) -> None:
    with open(path, "wt") as obj_file:
        print('\n'.join("v {:.5f} {:.5f} {:.5f}".format(v.x, v.y, v.z) for v in mesh.vertices), file=obj_file)
        print('\n'.join("vt {:.5f} {:.5f}".format(v.x, v.y) for v in mesh.uvs), file=obj_file)
        print('\n'.join("vn {:.5f} {:.5f} {:.5f}".format(v.x, v.y, v.z) for v in mesh.normals), file=obj_file)
        print('\n'.join("f {}/{}/{} {}/{}/{} {}/{}/{}".format(v.p_1 + 1, v.uv1 + 1, v.n_1 + 1,
                                                              v.p_2 + 1, v.uv2 + 1, v.n_2 + 1,
                                                              v.p_3 + 1, v.uv3 + 1, v.n_3 + 1) for v in mesh.faces), file=obj_file)


def create_plane(height: float = 1.0, width: float = 1.0, rows: int = 10,
                 cols: int = 10, transform: Transform = None) -> TrisMesh:
    if rows < 2:
        rows = 2
    if cols < 2:
        cols = 2
    points_n: int = cols * rows
    x: float
    z: float
    mesh: TrisMesh = TrisMesh()
    normal: Vector3 = Vector3(0, 1, 0)
    for index in range(0, points_n):
        row, col = divmod(index, cols)
        x = width * ((cols - 1) * 0.5 - col) / (cols - 1.0)
        z = height * ((cols - 1) * 0.5 - row) / (cols - 1.0)
        mesh.append_vertex(Vector3(x, 0, z))
        mesh.append_uv(Vector3(1.0 - col * 1.0 / (cols - 1), row * 1.0 / (cols - 1)))
        mesh.append_normal(normal)
        if (index + 1) % cols == 0:
            continue  # пропускаем последю
        if rows - 1 == row:
            continue
        f = Face()
        f.index1(index)
        f.index2(index + 1)
        f.index3(index + cols)
        mesh.append_face(f)
        f = Face()
        f.index1(index + cols)
        f.index2(index + 1)
        f.index3(index + cols + 1)
        mesh.append_face(f)
    if transform is not None:
        mesh.transform_mesh(transform)
    return mesh


def create_box(side: float = 1.0, transform: Transform = None) -> TrisMesh:
    mesh: TrisMesh = TrisMesh()

    mesh.append_vertex(side * Vector3(-0.5000, 0.5000, -0.5000))
    mesh.append_vertex(side * Vector3(-0.5000, 0.5000, 0.5000))
    mesh.append_vertex(side * Vector3(0.5000, 0.5000, 0.5000))
    mesh.append_vertex(side * Vector3(0.5000, 0.5000, -0.5000))
    mesh.append_vertex(side * Vector3(-0.5000, -0.5000, -0.5000))
    mesh.append_vertex(side * Vector3(0.5000, -0.5000, -0.5000))
    mesh.append_vertex(side * Vector3(0.5000, -0.5000, 0.5000))
    mesh.append_vertex(side * Vector3(-0.5000, -0.5000, 0.5000))

    mesh.append_normal(Vector3(0.0000, 1.0000, 0.0000))
    mesh.append_normal(Vector3(0.0000, -1.0000, -0.0000))
    mesh.append_normal(Vector3(0.0000, 0.0000, -1.0000))
    mesh.append_normal(Vector3(1.0000, 0.0000, 0.0000))
    mesh.append_normal(Vector3(0.0000, -0.0000, 1.0000))
    mesh.append_normal(Vector3(-1.0000, 0.0000, 0.0000))

    mesh.append_uv(Vector2(1.0000, 0.0000))
    mesh.append_uv(Vector2(1.0000, 1.0000))
    mesh.append_uv(Vector2(0.0000, 1.0000))
    mesh.append_uv(Vector2(0.0000, 0.0000))

    mesh.append_face(Face(0, 0, 0, 1, 1, 0, 2, 2, 0))
    mesh.append_face(Face(2, 2, 0, 3, 3, 0, 0, 0, 0))
    mesh.append_face(Face(4, 3, 1, 5, 0, 1, 6, 1, 1))
    mesh.append_face(Face(6, 1, 1, 7, 2, 1, 4, 3, 1))
    mesh.append_face(Face(0, 3, 2, 3, 0, 2, 5, 1, 2))
    mesh.append_face(Face(5, 1, 2, 4, 2, 2, 0, 3, 2))
    mesh.append_face(Face(3, 3, 3, 2, 0, 3, 6, 1, 3))
    mesh.append_face(Face(6, 1, 3, 5, 2, 3, 3, 3, 3))
    mesh.append_face(Face(2, 3, 4, 1, 0, 4, 7, 1, 4))
    mesh.append_face(Face(7, 1, 4, 6, 2, 4, 2, 3, 4))
    mesh.append_face(Face(1, 3, 5, 0, 0, 5, 4, 1, 5))
    mesh.append_face(Face(4, 1, 5, 7, 2, 5, 1, 3, 5))

    if transform is not None:
        mesh.transform_mesh(transform)
    return mesh
