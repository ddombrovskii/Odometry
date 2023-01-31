from ctypes import CDLL, Structure, c_int, c_float, POINTER

a_star_lib = CDLL('./AStar/x64/Release/AStar.dll')


class Pt(Structure):
    _fields_ = ("row", c_int), ("col", c_int)


class Path(Structure):
    _fields_ = ("cost", c_float), ("n_points", c_int), ("path_points", POINTER(Pt))


class Map(Structure):
    _fields_ = ("cols", c_int), ("rows", c_int), ("weights", POINTER(c_float))


find_path_func = a_star_lib.find_path
find_path_func.argtypes = [POINTER(Map), POINTER(Pt), POINTER(Pt)]
find_path_func.restype = POINTER(Path)

py_weights = [0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0,
              0.1, 0.9, 0.9, 0.1, 0.0, 1.0, 0.0, 1.0,
              1.1, 0.2, 0.9, 0.2, 0.1, 1.0, 0.0, 1.0,
              1.0, 0.0, 0.3, 0.0, 1.0, 1.0, 0.0, 0.0,
              1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0,
              1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0,
              1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0,
              1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]

c_weights = (c_float * len(py_weights))(*py_weights)
rows, cols = c_int(8), c_int(8)

new_map = Map(rows, cols, c_weights)
start_pt = Pt(0, 0)
end_pt = Pt(7, 7)

path_p = a_star_lib.find_path(new_map, start_pt, end_pt)

print(f"cost: {path_p.contents.cost}")
print(f"n_points: {path_p.contents.n_points}")
for i in range(path_p.contents.n_points):
    print(f"({path_p.contents.path_points[i].row}, {path_p.contents.path_points[i].col})")
