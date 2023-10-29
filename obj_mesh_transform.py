from typing import Tuple
import numpy as np
import os.path
import math


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


def build_identity_transform():
    return np.identity(4, dtype=float)


def transform_scale(transform: np.ndarray) -> Tuple[float, float, float]:
    sx = math.sqrt(transform[0, 0] ** 2 + transform[1, 0] ** 2 + transform[2, 0] ** 2)
    sy = math.sqrt(transform[0, 1] ** 2 + transform[1, 1] ** 2 + transform[2, 1] ** 2)
    sz = math.sqrt(transform[0, 2] ** 2 + transform[1, 2] ** 2 + transform[2, 2] ** 2)
    return sx, sy, sz


def rotate_transform(ax: float, ay: float, az: float, transform: np.ndarray) -> np.ndarray:
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
    return np.array((rm[0, 0] * sx, rm[0, 1] * sy, rm[0, 2] * sz, transform[0, 3],
                     rm[1, 0] * sx, rm[1, 1] * sy, rm[1, 2] * sz, transform[1, 3],
                     rm[2, 0] * sx, rm[2, 1] * sy, rm[2, 2] * sz, transform[2, 3],
                     0.0,           0.0,           0.0,           1.0)).reshape((4, 4))


def scale_transform(sx: float, sy: float, sz: float, transform: np.ndarray) -> np.ndarray:
    _sx, _sy, _sz = transform_scale(transform)
    _sx = sx / _sx
    _sy = sy / _sy
    _sz = sz / _sz
    return np.array((transform[0, 0] * _sx, transform[0, 1] * _sy, transform[0, 2] * _sz, transform[0, 3],
                     transform[1, 0] * _sx, transform[1, 1] * _sy, transform[1, 2] * _sz, transform[1, 3],
                     transform[2, 0] * _sx, transform[2, 1] * _sy, transform[2, 2] * _sz, transform[2, 3],
                     0.0,                   0.0,                   0.0,                   1.0)).reshape((4, 4))


def _transform_mesh(load_mesh_path: str, save_mesh_path: str,  transform: np.ndarray):
    if not os.path.exists(load_mesh_path):
        print(f"Unable to found mesh at path \"{load_mesh_path}\"")
        return
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
                    x, y, z = _parse_line(line)
                    x, y, z = _transform_position(x, y, z, transform)
                    print(f"v  {x:.4f} {y:.4f} {z:.4f}", file=mesh_output)
                    continue
                print(line, file=mesh_output)


def transform_mesh(load_mesh_path: str, transform: np.ndarray):
    temp_path = f"{'.'.join(v for v in load_mesh_path.split('.')[:-1])}_temp.obj"
    _transform_mesh(load_mesh_path, temp_path, transform)
    os.remove(load_mesh_path)
    os.rename(temp_path, load_mesh_path)


if __name__ == "__main__":
    transform_m = build_identity_transform()
    transform_m = rotate_transform(math.pi * 0.5, 0, 0, transform_m)
    # transform_m = scale_transform (-1.0 * size_x, 1.0 * size_y, 1.0 * size_z, transform_m)
    # если нужно отразить по Х или указать размер
    #  _transform_mesh('teapot.obj', 'teapot_transformed.obj', transform_m) # запишет новый файл
    transform_mesh('teapot.obj', transform_m)  # ПЕРЕЗАПИШЕТ ФАЙЛ!
