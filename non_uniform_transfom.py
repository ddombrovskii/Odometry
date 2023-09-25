import json
import math
import os.path
from typing import Tuple, Callable, List

import cv2

from Utilities.Geometry import Matrix3, Vector2, PerspectiveTransform2d, Camera, Vector4, Vector3, Transform, Plane, \
    Matrix4
from matplotlib import pyplot as plt
import numpy as np
# Система уравнений для определения параметров матрицы искажения:
# пусть у нас есть 4 точки на поверхности земли. Координаты каждой из этих точек соответствуют
# координатам пересечения лучей совпадающих с рёбрами пирамиды видимости камеры
# {p_x, p_y} - координаты мира
# {c_x, c_y} - координаты камеры, которые представляются собой попарный набор из следующих значений:
# {1.0, 1.0} | {1.0, -1.0} | {-1.0, -1.0} | {-1.0, 1.0}
# Система уравнений буде состоять из четырёх пар вида:
# p_x = m00 * c_x + m01 * c_y - p_x * c_x * m20 - p_x * c_y * m21 + m02
# p_y = m10 * c_x + m11 * c_y - p_y * c_x * m20 - p_y * c_y * m21 + m12
# итого система уравнений состоит из блоков вида:
# m00 | m01 | m02 | m10 | m11 | m12 |     m20    |     m21    |
# c_x | c_y |  1  |  0  |  0  |  0  | -p_x * c_x | -p_x * c_y |
#  0  |  0  |  0  | c_x | c_y |  1  | -p_y * c_x | -p_y * c_y |
# окончательно:
#  m00 | m01 | m02 | m10 | m11 | m12 |  m20 |  m21 |

#  1.0 | 1.0 | 1.0 |  0  |  0  |  0  | -p_x | -p_x |
#   0  |  0  |  0  | 1.0 | 1.0 | 1.0 | -p_y | -p_y |

#  1.0 |-1.0 | 1.0 |  0  |  0  |  0  | -p_x |  p_x |
#   0  |  0  |  0  | 1.0 |-1.0 | 1.0 | -p_y |  p_y |

# -1.0 |-1.0 | 1.0 |  0  |  0  |  0  |  p_x |  p_x |
#   0  |  0  |  0  |-1.0 |-1.0 | 1.0 |  p_y |  p_y |

# -1.0 | 1.0 | 1.0 |  0  |  0  |  0  |  p_x | -p_x |
#   0  |  0  |  0  |-1.0 | 1.0 | 1.0 |  p_y | -p_y |
from Utilities.image_matcher import ImageMatcher


def perspective_transform_test():
    transform_m = Matrix3(1.0, 0.4, -0.120,
                          0.1, 1.0, 0.50,
                          -0.25, 0.125, 1.0)

    transform = PerspectiveTransform2d(transform_m)
    x_points = 13
    y_points = 13

    points_1 = (Vector2(1.4629, 1.8286), Vector2(0.768, -0.64),
                Vector2(-1.3511, -0.5333), Vector2(-0.5236, 1.0182))

    points_2 = (Vector2(1.9, 1.2), Vector2(0.28, -0.3),
                Vector2(-1.5, -0.6), Vector2(-0.6, 1.4))

    transform_between = PerspectiveTransform2d.from_eight_points(*points_2, *points_1)
    print('\n'.join(str(v) for v in transform_between.inv_transform_points(points_2)))

    print(transform_between)

    transform_from_points = PerspectiveTransform2d.from_four_points(*points_1)

    positions = [Vector2((row / (y_points - 1) - 0.5) * 2.0, (col / (x_points - 1) - 0.5) * 2.0)
                 for col in range(y_points) for row in range(x_points)]

    positions_transformed = transform.inv_transform_points(positions)
    positions_inv_transformed = transform_from_points.transform_points(positions_transformed)

    x_points = np.array([v.x for v in positions])
    y_points = np.array([v.y for v in positions])

    x_points_transformed = np.array([v.x for v in positions_transformed])
    y_points_transformed = np.array([v.y for v in positions_transformed])

    x_points_inv_transformed = np.array([v.x for v in positions_inv_transformed])
    y_points_inv_transformed = np.array([v.y for v in positions_inv_transformed])

    fig, axs = plt.subplots(1)
    axs.plot(x_points, y_points, '*r')
    axs.plot(x_points_transformed, y_points_transformed, '.b')
    axs.set_aspect('equal', 'box')
    # plt.plot(x_points_inv_transformed, y_points_inv_transformed, 'og')
    plt.show()


def image_sample_points(image, pt1: Vector2, pt2: Vector2, pt3: Vector2, pt4: Vector2, samples=512) -> \
        Tuple[np.ndarray, Matrix3]:
    transform_matrix = Matrix3.perspective_transform_from_eight_points(Vector2(samples, samples), Vector2(samples, 0),
                                                                       Vector2(0, 0), Vector2(0, samples),
                                                                       pt1, pt2, pt3, pt4)
    dst = cv2.warpPerspective(image, transform_matrix.to_np_array(), (samples, samples))
    return dst, transform_matrix


def image_sample(image, sample_transform: Matrix3, samples=256) -> Tuple[np.ndarray, Matrix3]:
    sample_border = (Vector2(samples, samples), Vector2(samples, 0), Vector2(0, 0), Vector2(0, samples))
    source_corners = [sample_transform.multiply_by_point(p - Vector2(samples * 0.5, samples * 0.5))
                      for p in sample_border]
    return image_sample_points(image, source_corners[0], source_corners[1],
                               source_corners[2], source_corners[3], samples)


def build_test_data_for_image_track(image_src: str, target_dir: str):
    image = cv2.imread(image_src, cv2.IMREAD_GRAYSCALE)
    w, h = image.shape
    n_images = 64
    dangle_ = 2 * math.pi / (n_images - 1)
    transforms = [Matrix3.translate(Vector2(h // 2, w // 2)) *
                  (Matrix3.rotate_z(dangle_ * i) * Matrix3.translate(Vector2(h // 4, 0))) for i in range(n_images)]

    # transform = Matrix3.translate(Vector2(h//2, w//2)) * Matrix3.rotate_z(45, angle_in_rad=False)

    with open(f"{target_dir}\\transforms.json", 'wt', encoding='utf-8') as out_file:
        print("{\n\"poses\":[\n", end='', file=out_file)
        for index, transform in enumerate(transforms):
            img, proj = image_sample(image, transform)
            cv2.imwrite(f"{target_dir}\\image_{index}.png", img)
            print(f"\t{{\n\"projection\":\n{proj},\n\"transform\":\n{transform}\n}}", end='', file=out_file)
            if index != len(transform) - 1:
                print(',\n', end='', file=out_file)
        print("]\n}", file=out_file)

    # [cv2.imwrite(f"{target_dir}\\image_{index}.png",
    #             image_sample(image_1, transform)) for index, transform in enumerate(transforms)]


def image_index(img) -> int:
    return int((img.split('_')[-1]).split('.')[0])


def camera_view_frustum_rays():
    camera = Camera()
    camera.aspect = 1.0
    camera.fov = 45
    camera.z_far = 1000
    camera.z_near = 0.1
    # camera.transform.ax = 45
    print(camera.emit_ray(0, 0))
    print(camera.emit_ray(1, 1))
    print(camera.emit_ray(1, -1))
    print(camera.emit_ray(-1, -1))
    print(camera.emit_ray(-1, 1))
    print(2.0 / math.tan(70 / 180 * math.pi))
    directions_start = (Vector3(0, 0, -camera.z_near), Vector3(0, 0, 0.5 * (camera.z_far + camera.z_near)))
    print(camera.projection)
    for ps in directions_start:
        v = camera.to_clip_space(ps)
        print(f"{ps} | -> {v}")
    # print(camera)


def camera_frustum_ground_border(camera: Camera, ground_level: float = 0.0) -> Tuple[Vector3, ...]:
    p = Plane(origin=Vector3(0, ground_level, 0))  # normal=Vector3(0, -1, 0))
    # {1.0, 1.0} | {1.0, -1.0} | {-1.0, -1.0} | {-1.0, 1.0}
    return (p.intersect_by_ray(camera.emit_ray(1.0, 1.0)).end_point,
            p.intersect_by_ray(camera.emit_ray(1.0, -1.0)).end_point,
            p.intersect_by_ray(camera.emit_ray(-1.0, -1.0)).end_point,
            p.intersect_by_ray(camera.emit_ray(-1.0, 1.0)).end_point)


def camera_tilt_movement(flight_height: float = 100.0):
    camera = Camera()
    camera.aspect = 1.0
    # camera.z_near = 0.00001
    # camera.ortho_size = 10
    # camera.perspective_mode = False
    fig, axs = plt.subplots(1)
    axs.set_aspect('equal', 'box')
    for i in range(8):
        camera.transform.origin = Vector3(0, flight_height, 5.0 * i)
        camera.transform.angles = Vector3(90 + 10 * math.cos(4 * i / math.pi), 0.0, 10 * math.sin(4 * i / math.pi))
        border = camera_frustum_ground_border(camera)
        positions_x = [v.x for v in border]
        positions_y = [v.z for v in border]
        positions_x.append(positions_x[0])
        positions_y.append(positions_y[0])
        positions_x = np.array(positions_x)
        positions_y = np.array(positions_y)
        axs.plot(positions_x, positions_y)
    plt.show()


def camera_tilt_simulation(x_ang_amplitude: float = 0.0,
                           y_ang_amplitude: float = 2.50,
                           flight_altitude: float = 100.0,
                           tilt_frequency: float = 5.0,
                           movement_speed: float = 10.0,
                           simulation_steps: int = 32,
                           simulation_duration: float = 10.0):
    camera = Camera()
    camera.aspect = 1.0
    dt = simulation_duration / (simulation_steps - 1)
    borders = []
    for i in range(simulation_steps):
        camera.transform.origin = Vector3(movement_speed * dt * i, flight_altitude, 0.0)
        camera.transform.angles = Vector3(90 + x_ang_amplitude * math.cos(tilt_frequency * dt * i / math.pi), 0.0,
                                          y_ang_amplitude * math.sin(tilt_frequency * dt * i / math.pi))
        borders.append(camera_frustum_ground_border(camera))

    # fig, axs = plt.subplots(1)
    # axs.set_aspect('equal', 'box')
    # for border in borders:
    #     positions_x = [v.x for v in border]
    #     positions_y = [v.z for v in border]
    #     positions_x.append(positions_x[0])
    #     positions_y.append(positions_y[0])
    #     positions_x = np.array(positions_x)
    #     positions_y = np.array(positions_y)
    #     axs.plot(positions_x, positions_y)
    # plt.show()
    return borders


def _load_pose_data(poses_file: str) -> List[Tuple[Matrix3, Matrix4]]:
    with open(poses_file, 'rt', encoding='utf-8') as input_file:
        raw_json = json.load(input_file)
        if 'poses' not in raw_json:
            return []
        poses = []
        for node in raw_json['poses']:
            try:
                proj = Matrix3(*tuple(map(float, node['projection'].values())))
                print(proj)
                trans = Matrix4(*tuple(map(float, node['transform'].values())))
                poses.append((proj, trans))
            except Exception as ex:
                print(ex)
        return poses


def odometry_movement_test(directory):
    img_matcher = ImageMatcher()
    poses = _load_pose_data(f"{directory}\\transforms.json")
    # directory = "path_track\\camera_tilt"
    images = [f"{directory}\\{src}" for src in os.listdir(directory) if src.endswith('png') or src.endswith('JPG')]
    images = sorted(images, key=image_index)
    # [print(t) for t in images]
    positions_x = []
    positions_y = []
    transforms = []
    if len(poses) != len(images):
        transforms = [img_matcher.match_images_from_file(img_1, img_2) for img_1, img_2 in zip(images[:-1], images[1:])]
    else:
        for img_1, img_2, (proj_1, trans_1), (proj_2, trans_2) in zip(images[:-1], images[1:], poses[:-1], poses[1:]):
            transforms.append(img_matcher.match_images_from_file(img_1, img_2, proj_1.invert(), proj_2.invert()))
    # [print(t) for t in transforms]
    curr_t = transforms[0]

    for prev_t, next_t in zip(transforms[:-1], transforms[1:]):
        # print(prev_t)
        # k_matrix =
        curr_t *= prev_t
        positions_x.append(curr_t.m02)
        positions_y.append(curr_t.m12)
    positions_x = np.array(positions_x)
    positions_y = np.array(positions_y)

    fig, axs = plt.subplots(1)
    axs.plot(positions_x, positions_y, 'r')
    axs.set_aspect('equal', 'box')
    plt.show()


def _angles_func(t):
    return Vector3(90 + 0.0 * math.cos(5 * t / math.pi), 0.0, 2.5 * math.sin(5 * t / math.pi))


def _position_func(t):
    return Vector3(0, 100, 5.5 * t)


def generate_trajectory_simulation(image_src: str,
                                   angles_func: Callable[[float], Vector3] = None,
                                   position_func: Callable[[float], Vector3] = None, time_step: float = 0.1,
                                   time_duration: float = 10):
    camera = Camera()
    camera.aspect = 1.0
    camera.fov = 30
    steps = int(time_duration / time_step)
    ground_frustum_borders = []
    angles_func = _angles_func if angles_func is None else angles_func
    position_func = _position_func if position_func is None else position_func
    camera_real_world_transforms = []
    # границы пирамиды видимости в мировых координатах
    for i in range(steps):
        camera.transform.origin = position_func(i * time_step)
        camera.transform.angles = angles_func(i * time_step)
        ground_frustum_borders.append(tuple(Vector2(p.x, p.z) for p in camera_frustum_ground_border(camera)))
        camera_real_world_transforms.append(camera.transform.transform_matrix)
    # минимальные и максимальные координаты границ пирамид видимости
    border_min = Vector2(1e12, 1e12)
    border_max = Vector2(-1e12, -1e12)
    # exact borders limits
    for border in ground_frustum_borders:
        for p in border:
            border_min = Vector2.min(border_min, p)
            border_max = Vector2.max(border_max, p)
    print(f"border_min    : {border_min}\n"
          f"border_max    : {border_max}\n")
    # трансформация с сохранением соотношений сторон в область [-1, 1] x [-1, 1]
    borders_size   = (border_max - border_min)  # + Vector3(0, 1, 0) to handle zero division error...
    borders_scale =  Vector2(borders_size.x / borders_size.y, 1) / borders_size
    to_unit_scale: Matrix3 = Matrix3(borders_scale.x, 0.0,              0.0,
                                     0.0,             borders_scale.y,  0.0,
                                     0.0,             0.0,              1.0)

    to_unit_shift: Matrix3 = Matrix3(1.0, 0.0, -(border_min.x + border_max.x) * 0.5,
                                     0.0, 1.0, -(border_min.y + border_max.y) * 0.5,
                                     0.0, 0.0,              1.0)

    print(f"to_unit_scale:\n{to_unit_scale}")
    print(f"to_unit_shift:\n{to_unit_shift}")
    print(f"to_unit_transform:\n{to_unit_scale * to_unit_shift}")
    image = cv2.imread(image_src, cv2.IMREAD_GRAYSCALE)
    image_w, image_h = image.shape
    image_w, image_h = image_w // 2, image_h // 2
    size = min(image_h, image_w)
    # трансформация для перехода из области [-1, 1] x [-1, 1] в область [0, image_w] x [0, image_h]
    to_image_transform: Matrix3 = Matrix3(size, 0.0,  size * 0.5,
                                          0.0,  size, size * 0.5,
                                          0.0,  0.0,         1.0)

    print(f"to_image_transform:\n{to_image_transform}")
    target_dir = "path_track\\camera_tilt"
    image_space_borders = []
    # перевод границ из пирамид видимости из мировых координат в координаты изображения из которого вырезаем куски,
    # которые могла бы видеть камера при указанных angles_func и position_func
    for border in ground_frustum_borders:
        image_space_borders.append([])
        for p in border:
            p = to_unit_shift.multiply_by_point(p)
            p = to_unit_scale.multiply_by_point(p)
            p = to_image_transform.multiply_by_point(p)
            image_space_borders[-1].append(p)

    with open(f"{target_dir}\\transforms.json", 'wt', encoding='utf-8') as out_file:
        print("{\n\"poses\":[\n", end='', file=out_file)
        for index, (ws_t, gt_b, img_b) in\
                enumerate(zip(camera_real_world_transforms, ground_frustum_borders, image_space_borders)):
            img, proj = image_sample_points(image, *img_b)
            cv2.imwrite(f"{target_dir}\\image_{index}.png", img)
            print(f"\t{{\n\"projection\":\n{Matrix3.perspective_transform_from_four_points(*gt_b)},"
                  f"\n\"transform\":\n{ws_t}\n}}", end='', file=out_file)
            if index != len(camera_real_world_transforms) - 1:
                print(',\n', end='', file=out_file)
        print("]\n}", file=out_file)

    fig, axs = plt.subplots(2)
    axs[0].set_aspect('equal', 'box')
    centers_x = []
    centers_y = []
    for border in ground_frustum_borders:
        positions_x = [v.x for v in border]
        positions_y = [v.y for v in border]
        positions_x.append(positions_x[0])
        positions_y.append(positions_y[0])
        positions_x = np.array(positions_x)
        positions_y = np.array(positions_y)
        # axs[0].plot(positions_x, positions_y)
        centers_x.append(positions_x.sum()/positions_x.size)
        centers_y.append(positions_y.sum() / positions_y.size)
    axs[0].plot(centers_x, centers_y, 'r')

    axs[1].set_aspect('equal', 'box')
    centers_x = []
    centers_y = []
    for border in image_space_borders:
        positions_x = [v.x for v in border]
        positions_y = [v.y for v in border]
        positions_x.append(positions_x[0])
        positions_y.append(positions_y[0])
        positions_x = np.array(positions_x)
        positions_y = np.array(positions_y)
        # axs[1].plot(positions_x, positions_y)
        centers_x.append(positions_x.sum()/positions_x.size)
        centers_y.append(positions_y.sum() / positions_y.size)
    axs[1].plot(centers_x, centers_y, 'r')
    plt.show()


if __name__ == "__main__":
    #
    # generate_trajectory_simulation("salzburg_city_view_by_burtn-d61404o.jpg")

    odometry_movement_test("path_track\\camera_tilt")
    # odometry_movement_test("path_track")
    # odometry_circular_movement_test()
    # exit()
    # image_1 = cv2.imread("salzburg_city_view_by_burtn-d61404o.jpg", cv2.IMREAD_GRAYSCALE)



    # build_test_data_for_image_track("tsukuba_r.png", "path_track")
    # perspective_transform_test()
    # image_math_and_homography("tsukuba_l.png", "tsukuba_r.png")
