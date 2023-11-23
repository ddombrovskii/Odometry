from typing import Tuple, List, Union
from numpy.linalg import LinAlgError
from collections import namedtuple
import matplotlib.pyplot as plt
import numpy as np
import os.path
import json
import math
import sys


def get_full_path(directory: str, file: str) -> str:
    return os.path.join(os.path.dirname(directory), file)


def build_identity_transform():
    return np.array(((1.0, 0.0, 0.0, 0.0),
                     (0.0, 1.0, 0.0, 0.0),
                     (0.0, 0.0, 1.0, 0.0)))


def _parse_line(line: str) -> Tuple[float, float, float]:
    s_line = line.split(' ')
    s_line = tuple(s for s in s_line if len(s) != 0)
    return float(s_line[-3]), float(s_line[-2]), float(s_line[-1])


def _transform_position(x: float, y: float, z: float, transform: np.ndarray) -> Tuple[float, float, float]:
    return transform[0, 0] * x + transform[0, 1] * y + transform[0, 2] * z + transform[0, 3],\
           transform[1, 0] * x + transform[1, 1] * y + transform[1, 2] * z + transform[1, 3],\
           transform[2, 0] * x + transform[2, 1] * y + transform[2, 2] * z + transform[2, 3]


def _transform_direction(x: float, y: float, z: float, transform: np.ndarray) -> Tuple[float, ...]:
    normal = (transform[0, 0] * x + transform[0, 1] * y + transform[0, 2] * z,
              transform[1, 0] * x + transform[1, 1] * y + transform[1, 2] * z,
              transform[2, 0] * x + transform[2, 1] * y + transform[2, 2] * z)
    length = 1.0 / sum(v * v for v in normal)
    return tuple(v * length for v in normal)


def transform_scale(transform: np.ndarray) -> Tuple[float, float, float]:
    sx = np.linalg.norm(transform[:, 0])
    sy = np.linalg.norm(transform[:, 1])
    sz = np.linalg.norm(transform[:, 2])
    return sx, sy, sz


def transform_translation(transform: np.ndarray) -> Tuple[float, float, float]:
    return transform[0, 3], transform[1, 3], transform[2, 3]


def rotate_transform(ax: float, ay: float, az: float, transform: np.ndarray = None) -> np.ndarray:
    if transform is None:
       sx, sy, sz = 1.0, 1.0, 1.0
       transform = build_identity_transform()
    else:
        sx, sy, sz = transform_scale(transform)

    cos_a = math.cos(ax)
    sin_a = math.sin(ax)
    rx = np.array((1.0, 0.0, 0.0, 0.0, cos_a, -sin_a, 0.0, sin_a, cos_a)).reshape((3, 3))
    cos_a = math.cos(ay)
    sin_a = math.sin(ay)
    ry = np.array((cos_a, 0.0, sin_a, 0.0, 1.0, 0.0, -sin_a, 0.0, cos_a)).reshape((3, 3))
    cos_a = math.cos(az)
    sin_a = math.sin(az)
    rz = np.array((cos_a, -sin_a, 0.0, sin_a, cos_a, 0.0, 0.0, 0.0, 1.0)).reshape((3, 3))
    rm = rx @ ry @ rz
    transform[0, 0] = rm[0, 0] * sx
    transform[1, 0] = rm[1, 0] * sx
    transform[2, 0] = rm[2, 0] * sx
    transform[0, 1] = rm[0, 1] * sy
    transform[1, 1] = rm[1, 1] * sy
    transform[2, 1] = rm[2, 1] * sy
    transform[0, 2] = rm[0, 2] * sz
    transform[1, 2] = rm[1, 2] * sz
    transform[2, 2] = rm[2, 2] * sz
    return transform


def scale_transform(sx: float, sy: float, sz: float, transform: np.ndarray = None) -> np.ndarray:
    if transform is None:
       _sx, _sy, _sz = 1.0, 1.0, 1.0
       transform = build_identity_transform()
    else:
        _sx, _sy, _sz = transform_scale(transform)
    _sx = sx / _sx
    _sy = sy / _sy
    _sz = sz / _sz
    transform[0, 0] *= _sx
    transform[1, 0] *= _sx
    transform[2, 0] *= _sx
    transform[0, 1] *= _sy
    transform[1, 1] *= _sy
    transform[2, 1] *= _sy
    transform[0, 2] *= _sz
    transform[1, 2] *= _sz
    transform[2, 2] *= _sz
    return transform


def translate_transform(px: float, py: float, pz: float, transform: np.ndarray = None) -> np.ndarray:
    if transform is None:
       transform = build_identity_transform()
    transform[0, 3] = px
    transform[1, 3] = py
    transform[2, 3] = pz
    return transform


def bi_linear_regression(x: np.ndarray, y: np.ndarray, z: np.ndarray) ->\
        Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    """
    Билинейная регрессия.\n
    Hesse matrix:\n
                   | Σ xi^2;  Σ xi*yi; Σ xi |\n
    H(kx, ky, b) = | Σ xi*yi; Σ yi^2;  Σ yi |\n
                   | Σ xi;    Σ yi;    n    |\n

                      | Σ-zi*xi + ky*xi*yi + kx*xi^2 + xi*b |\n
    grad(kx, ky, b) = | Σ-zi*yi + ky*yi^2 + kx*xi*yi + b*yi |\n
                      | Σ-zi + yi*ky + xi*kx                |\n

    Окончательно решение:\n
    |kx|   |1|\n
    |ky| = |1| -  H(1, 1, 0)^-1 * grad(1, 1, 0)\n
    | b|   |0|\n

    :param x: массив значений по x
    :param y: массив значений по y
    :param z: массив значений по z
    :returns: возвращает тройку (kx, ky, b), которая является решением задачи (Σ(zi - (yi * ky + xi * kx + b))^2)->min
    и тройку координат центра
    """
    assert x.size == y.size, "bi_linear_regression :: x.size == y.size"
    assert x.size == z.size, "bi_linear_regression :: x.size == z.size"

    sum_x = x.sum()
    sum_y = y.sum()
    sum_z = z.sum()
    i_n = 1.0 / x.size
    sum_xy = (x * y).sum()
    sum_xx = (x * x).sum()
    sum_yy = (y * y).sum()
    sum_zy = (z * y).sum()
    sum_zx = (x * z).sum()

    hess = np.array([[sum_xx, sum_xy, sum_x],
                     [sum_xy, sum_yy, sum_y],
                     [sum_x, sum_y, x.size]])
    grad = np.array([sum_xx + sum_xy - sum_zx,
                     sum_xy + sum_yy - sum_zy,
                     sum_x  + sum_y - sum_z])
    try:
        return tuple(np.array([1.0, 1.0, 0.0]) - np.linalg.inv(hess) @ grad), (sum_x * i_n, sum_y * i_n, sum_z * i_n)
    except LinAlgError as err:
        print(err.args)
        return (0.0, 0.0, 0.0), (sum_x * i_n, sum_y * i_n, sum_z * i_n)


def load_poses(poses_file: str) -> Union[List[np.ndarray], None]:
    assert isinstance(poses_file, str)
    assert os.path.exists(poses_file)
    with open(poses_file, 'rt', encoding='utf-8') as input_poses:
        poses_json = json.load(input_poses)
    if "extrinsics" not in poses_json:
        return None
    transforms = []
    for p_json in poses_json["extrinsics"]:
        try:
            rot = np.array(tuple(tuple(tuple(float(v) for v in row)) for row in p_json["value"]["rotation"]))
            for i in range(3):
                rot[:, i] /= np.linalg.norm(rot[:, i])
            pos = np.array(tuple(float(v) for v in p_json["value"]["center"])).reshape((3, 1))
            transforms.append(np.hstack((rot, pos)))
        except ZeroDivisionError as er:
            print(er)
        except KeyError as er:
            print(er)
        except ValueError as er:
            print(er)

    points = [transforms.pop()]
    while len(transforms) != 0:
        dist = 1e32
        pt_index = -1
        p_target = points[-1]
        for index, pt in enumerate(transforms):
            curr_dist = np.linalg.norm(p_target[:, 3] - pt[:, 3])
            if curr_dist < dist:
                dist = curr_dist
                pt_index = index
        points.append(transforms[pt_index])
        del transforms[pt_index]
    return points


def _build_transform_from_points_cloud(xs: np.ndarray,
                                       ys: np.ndarray,
                                       zs: np.ndarray,
                                       ez: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]:

    (kx, ky, b), (cx, cy, cz) = bi_linear_regression(xs, ys, zs)
    ey = np.array((-kx, -ky, 1.0))
    ey /= np.linalg.norm(ey)
    ez = np.array((0.0, 0.0, 0.1))  # if ez is None else ez
    ex  = np.cross(ey, ez)
    ex /= np.linalg.norm(ex)
    ez  = np.cross(ex, ey)
    ez /= np.linalg.norm(ez)
    # Костыльный способ развернуть по доминирующему направлению вдоль оси z
    # должно предотвратить переворачивание карты?
    # if abs(ex[0]) < 0.3:
    #     ex, ez = ez, ex * (1.0 if ex[0] > 0 else -1.0)
    pc = np.array((cx, cy, cz), dtype=float)
    direct_transform         = np.hstack((ex.reshape((3, 1)), ey.reshape((3, 1)),
                                          ez.reshape((3, 1)), pc.reshape((3, 1))))
    invert_transform         = np.zeros((3, 4), dtype=float)
    invert_transform[:3, :3] = direct_transform[:3, :3].T
    invert_transform[:, 3]   = np.array((-np.dot(pc, ex), -np.dot(pc, ey), -np.dot(pc, ez)), dtype=float)
    return direct_transform, invert_transform


def transform_mesh(load_mesh_path: str, save_mesh_path: str,  transform: np.ndarray):
    if not os.path.exists(load_mesh_path):
        print(f"Unable to found mesh at path \"{load_mesh_path}\"")
        return
    override_file = False
    if load_mesh_path == save_mesh_path:
        override_file = True
        save_mesh_path =  get_full_path(save_mesh_path, "temp.obj")

    x_points = []
    y_points = []
    z_points = []
    p_min = ( 1e32,  1e32,  1e32)
    p_max = (-1e32, -1e32, -1e32)

    with open(load_mesh_path, 'rt') as mesh_input:
        with open(save_mesh_path, 'wt') as mesh_output:
            for line in mesh_input:
                line = line.strip()
                if line.startswith('vt'):
                    print(line, file=mesh_output)
                    continue
                if line.startswith('vn'):
                    x, y, z = _parse_line(line)
                    x, y, z = _transform_direction(x, y, z, transform)
                    print(f"vn {x:.4f} {y:.4f} {z:.4f}", file=mesh_output)
                    continue
                if line.startswith('v'):
                    pt = _parse_line(line)
                    pt = _transform_position(*pt, transform)
                    x_points.append(pt[0])
                    y_points.append(pt[1])
                    z_points.append(pt[2])
                    p_min = tuple(min(pi, pti) for pi, pti in zip(p_min, pt))
                    p_max = tuple(max(pi, pti) for pi, pti in zip(p_max, pt))
                    print(f"v  {pt[0]:.4f} {pt[1]:.4f} {pt[2]:.4f}", file=mesh_output)
                    continue
                print(line, file=mesh_output)

    x_points = np.array(x_points)
    y_points = np.array(y_points)
    z_points = np.array(z_points)

    if override_file:
        os.remove(load_mesh_path)
        os.rename(save_mesh_path, load_mesh_path)

    return _build_transform_from_points_cloud(x_points, y_points, z_points)


def get_transform_from_poses(poses: List[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    dist_max = 0.0
    p_max_1 = np.zeros((3,), dtype=float)
    p_max_2 = np.zeros((3,), dtype=float)
    for p_1 in poses:
        for p_2 in poses:
            curr_dist = np.linalg.norm(p_1[:, 3] - p_2[:, 3])
            if curr_dist < dist_max:
                continue
            dist_max = curr_dist
            p_max_1 = p_1[:, 3]
            p_max_2 = p_2[:, 3]
    ez = p_max_2 - p_max_1

    xs = np.array([p_i[0, 3] for p_i in poses])
    ys = np.array([p_i[1, 3] for p_i in poses])
    zs = np.array([p_i[2, 3] for p_i in poses])

    return _build_transform_from_points_cloud(xs, ys, zs, ez)


class MeshTransformSettings(namedtuple("MeshTransformSettings", "original_mesh, transformed_mesh,"
                                                                " poses_file, position, rotation, scale")):
    def __new__(cls, *args):
        assert len(args) == 6
        assert all(isinstance(arg, t_type)for arg, t_type in zip(args, (str, str, str, tuple, tuple, tuple)))
        return super().__new__(cls, *args)

    def __str__(self):
        return (f"{{\n"
                f"\t\"original_mesh\":    \"{self.original_mesh}\",\n"
                f"\t\"transformed_mesh\": \"{self.transformed_mesh}\",\n"
                f"\t\"poses_file\":       \"{self.poses_file}\",\n"
                f"\t\"position\":         [{','.join(str(v) for v in self.position)}],\n"
                f"\t\"rotation\":         [{','.join(str(v) for v in self.rotation)}],\n"
                f"\t\"scale\":            [{','.join(str(v) for v in self.scale)}]\n"
                f"}}")


def load_mesh_transform_settings(src_file: str, as_string: bool = False) -> Union[str, MeshTransformSettings]:
    raw_json = None
    if as_string:
        raw_json = json.loads(src_file)
    else:
        with open(src_file, 'rt', encoding='utf-8') as input_f:
            raw_json = json.load(input_f)
    if raw_json is None:
        return f"{{\"error\": \"unable to read or parce json file: \'{src_file}\'...\"}}"

    original_mesh    = raw_json["original_mesh"] if "original_mesh" in raw_json else ""
    transformed_mesh = raw_json["transformed_mesh"] if "transformed_mesh" in raw_json else original_mesh
    poses_file       = raw_json["poses_file"] if "poses_file" in raw_json else ""
    angle_units = 1.0
    if "angle_units" in raw_json:
        angle_units = math.pi / 180.0 if raw_json["angle_units"] == "deg" else 1.0 if "angle_units" in raw_json else 1.0
    try:
        position = tuple(float(v) for v in raw_json["position"]) if "position" in raw_json else (0.0, 0.0, 0.0)
    except ValueError as ex:
        return f"{{\"error\": \"position read error: {ex}\"}}"
    try:
        rotation = tuple(float(v) * angle_units for v in raw_json["rotation"]) \
                         if "rotation" in raw_json else (0.0, 0.0, 0.0)
    except ValueError as ex:
        return f"{{\"error\": \"rotation read error: {ex}\"}}"
    try:
        scale    = tuple(float(v) for v in raw_json["scale"]) if "scale" in raw_json else (1.0, 1.0, 1.0)
    except ValueError as ex:
        return f"{{\"error\": \"scale read error: {ex}\"}}"

    return MeshTransformSettings(original_mesh, transformed_mesh, poses_file, position, rotation, scale)


def make_mesh_transform(args: Tuple[str, ...] = None):
    """
    command example:
    {
        "original_mesh":    "my_mesh.obj",
        "transformed_mesh": "my_mesh.obj",
        "poses_file":       "",
        "angle_units":      "deg",
        "position":         [1.0, 2.0, 3.0],
        "rotation":         [90.0, 0.0, 0.0],
        "scale":            [1.0, 1.0, 1.0]
    }
    """
    if args is None:
        args = sys.argv[1:]

    if len(args) == 0:
        return f"{{\"error\": \"empty command\"}}"

    dir_name  = args[0]
    transform_settings = load_mesh_transform_settings(dir_name, False)
    print(transform_settings)
    transform_m = build_identity_transform()
    transform_m = rotate_transform   (*transform_settings.rotation, transform_m)
    transform_m = scale_transform    (*transform_settings.scale,    transform_m)
    transform_m = translate_transform(*transform_settings.position, transform_m)
    model_orig_path = get_full_path(dir_name, transform_settings.original_mesh)
    model_curr_path = model_orig_path
    if transform_settings.poses_file != "":
        poses = load_poses(get_full_path(dir_name, transform_settings.poses_file))
        transform, inv_transform = get_transform_from_poses(poses)
        model_curr_path = get_full_path(dir_name, '_temp.obj')
        tf, ti = transform_mesh(model_orig_path, model_curr_path, inv_transform)
        transform_mesh(model_curr_path, model_curr_path, ti)
    transform_mesh(model_curr_path, get_full_path(dir_name, transform_settings.transformed_mesh), transform_m)
    if model_curr_path.endswith("_temp.obj"):
        os.remove(model_curr_path)


def test_transform_from_poses(poses_file):
    poses = load_poses(poses_file)
    [print(f"pose {i}\n{p}") for i, p in enumerate(poses)]
    transform, inv_transform = get_transform_from_poses(poses)
    print(f"transform:\n{transform}")
    print(f"inv_transform:\n{inv_transform}")
    x = np.array([p[0, 3] for p in poses])
    y = np.array([p[1, 3] for p in poses])
    z = np.array([p[2, 3] for p in poses])
    ax = plt.axes(projection='3d')
    plt.xlabel('x')
    plt.ylabel('y')
    pc = transform[:, 3]
    ax.plot3D(x, y, z, 'k')

    for i, c in zip((0, 1, 2), ('r', 'g', 'b')):
        ex = transform[:, i]
        ax.plot3D([pc[0], pc[0] + ex[0] * 0.5],
                  [pc[1], pc[1] + ex[1] * 0.5],
                  [pc[2], pc[2] + ex[2] * 0.5],  c)
    pc = _transform_position(*transform[:, 3], inv_transform)
    transform_ = transform[:3, :3] @ inv_transform[:3, :3]
    for i, c in zip((0, 1, 2), ('r', 'g', 'b')):
        ex = transform_[:, i]
        ax.plot3D([pc[0], pc[0] + ex[0] * 0.5],
                  [pc[1], pc[1] + ex[1] * 0.5],
                  [pc[2], pc[2] + ex[2] * 0.5],  c)

    inv_transform_poses = []
    for p in poses:
        p = p[:, 3]
        inv_transform_poses.append(_transform_position(p[0], p[1], p[2], inv_transform))

    x = np.array([p[0] for p in inv_transform_poses])
    y = np.array([p[1] for p in inv_transform_poses])
    z = np.array([p[2] for p in inv_transform_poses])
    ax.plot3D(x, y, z, 'gray')
    ax.set_aspect('equal', 'box')

    plt.show()


if __name__ == "__main__":
    # test_transform_from_poses("meshes/mesh_1/sfm_data_poses.json")
    # test_transform_from_poses("meshes/mesh_2/sfm_data_poses.json")
    # test_transform_from_poses("meshes/mesh_3/sfm_data_poses.json")
    # test_transform_from_poses("meshes/mesh_4/sfm_data_poses.json")
    # exit()
    """
    Структура директории : meshes/mesh_1/
     |- meshes/mesh_1/transform_info.json
     |- meshes/mesh_1/sfm_data_poses.json
     |- meshes/mesh_1/map.obj
    """
    """
      Пример файла настроек трансформации:
      "{
          "original_mesh":    "map.obj",
          "transformed_mesh": "transformed_map.obj",
          "poses_file":       "sfm_data_poses.json",
          "angle_units":      "deg",
          "position":         [ 0.0, 0.0, 0.0],
          "rotation":         [90.0, 0.0, 0.0], // x= 90.0 потому плоскость карты выравнивается по оси Z, а должна быть по Y 
          "scale":            [ 1.0, 1.0, 1.0]
      }"
      Пример "scale": [-1.0, 1.0, 1.0] - карта отражённая по оси х
    """
    # E:\GitHub\PathFinder\NewMap\Model
    make_mesh_transform(("E:/GitHub/PathFinder/NewMap/Model/transform_info.json",))

    # make_mesh_transform(("meshes/mesh_1/transform_info.json", ))
    # make_mesh_transform(("meshes/mesh_2/transform_info.json", ))
    # make_mesh_transform(("meshes/mesh_3/transform_info.json", ))
