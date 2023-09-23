import math
import os.path
from typing import Tuple

import cv2

from Utilities.Geometry import Matrix3, Vector2, PerspectiveTransform2d, Camera, Vector4, Vector3, Transform, Plane
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
    transform_m = Matrix3( 1.0,   0.4, -0.120,
                           0.1,   1.0,   0.50,
                         -0.25, 0.125,    1.0)

    transform = PerspectiveTransform2d(transform_m)
    x_points = 13
    y_points = 13

    points_1 = (Vector2(1.4629, 1.8286), Vector2(0.768, -0.64),
                Vector2(-1.3511, -0.5333), Vector2(-0.5236, 1.0182))

    points_2 = (Vector2(1.9, 1.2), Vector2(0.28, -0.3),
                Vector2(-1.5, -0.6), Vector2(-0.6, 1.4))

    transform_between =  PerspectiveTransform2d.from_eight_points(*points_2, *points_1)
    print('\n'.join(str(v)for v in transform_between.inv_transform_points(points_2)))

    print(transform_between)

    transform_from_points = PerspectiveTransform2d.from_four_points(*points_1)

    positions = [Vector2((row / (y_points - 1)  - 0.5) * 2.0, (col /  (x_points - 1) - 0.5) * 2.0)
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


def image_sample(image, sample_transform: Matrix3, samples=256):
    samples_half = samples // 2
    sample_border = (Vector2(samples, samples), Vector2(samples, 0), Vector2(0, 0), Vector2(0, samples))
    sample_border_center = sum(v for v in sample_border) / len(sample_border)
    source_corners = [sample_transform.multiply_by_point(p - sample_border_center) for p in sample_border]
    # for p1, p2 in zip(samples_points, sample_corners):
    #     print(f"{p1} |=> {p2}")
    source_corners = np.float32(source_corners)
    sample_border = np.float32(sample_border)
    matrix = cv2.getPerspectiveTransform(source_corners, sample_border)
    # print(Matrix3.from_np_array(matrix))
    dst = cv2.warpPerspective(image, matrix, (samples, samples))
    return dst
    # plt.subplot(121), plt.imshow(image), plt.title('Input')
    # plt.subplot(122), plt.imshow(dst), plt.title('Output')
    # plt.show()


def build_test_data_for_image_track(image_src: str, target_dir: str):
    image_1 = cv2.imread(image_src, cv2.IMREAD_GRAYSCALE)
    w, h = image_1.shape
    n_images = 64
    dangle_ = 2 * math.pi / (n_images - 1)
    transforms = [Matrix3.translate(Vector2(h//2, w//2)) *
                  (Matrix3.rotate_z(dangle_ * i) * Matrix3.translate(Vector2(h//4, 0))) for i in range(n_images)]

    transform = Matrix3.translate(Vector2(h//2, w//2)) * Matrix3.rotate_z(45, angle_in_rad=False)

    [cv2.imwrite(f"{target_dir}\\image_{index}.png",
                 image_sample(image_1, transform)) for index, transform in enumerate(transforms)]


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
    p = Plane(origin=Vector3(0, ground_level, 0))
    # {1.0, 1.0} | {1.0, -1.0} | {-1.0, -1.0} | {-1.0, 1.0}
    return (p.intersect_by_ray(camera.emit_ray( 1.0,  1.0)).end_point,
            p.intersect_by_ray(camera.emit_ray( 1.0, -1.0)).end_point,
            p.intersect_by_ray(camera.emit_ray(-1.0, -1.0)).end_point,
            p.intersect_by_ray(camera.emit_ray(-1.0,  1.0)).end_point)


def camera_tilt_movement():
    camera = Camera()
    camera.aspect = 1.0
    # camera.z_near = 0.00001
    # camera.ortho_size = 10
    # camera.perspective_mode = False
    fig, axs = plt.subplots(1)
    axs.set_aspect('equal', 'box')
    for i in range(8):
        camera.transform.origin = Vector3(0, 100, 5.0 * i)
        camera.transform.angles = Vector3(90 + 10 * math.cos(4 * i / math.pi), 0.0, 10 * math.sin(4 * i / math.pi))
        # print(camera.transform.transform_matrix)
        # [print(v) for v in ]
        border = camera_frustum_ground_border(camera)
        positions_x = [v.x for v in border]
        positions_y = [v.z for v in border]
        positions_x.append(positions_x[0])
        positions_y.append(positions_y[0])
        positions_x = np.array(positions_x)
        positions_y = np.array(positions_y)
        axs.plot(positions_x, positions_y)
    plt.show()


if __name__ == "__main__":
    camera_tilt_movement()
    exit()
    img_matcher = ImageMatcher()
    directory = "path_track"
    images = [f"{directory}\\{src}" for src in os.listdir(directory) if src.endswith('png') or src.endswith('JPG')]
    images = sorted(images, key=image_index)
    [print(t) for t in images]
    positions_x = []
    positions_y = []

    transforms = [img_matcher.match_images_from_file(img_1, img_2) for img_1, img_2 in zip(images[:-1], images[1:])]
    # [print(t) for t in transforms]
    curr_t = transforms[0]
    for next_t in transforms[1:]:
        curr_t *= next_t
        positions_x.append(curr_t.m02)
        positions_y.append(curr_t.m12)
    positions_x = np.array(positions_x)
    positions_y = np.array(positions_y)

    fig, axs = plt.subplots(1)
    axs.plot(positions_x, positions_y, 'r')
    axs.set_aspect('equal', 'box')
    plt.show()

    # build_test_data_for_image_track("tsukuba_r.png", "path_track")
    # perspective_transform_test()
    # image_math_and_homography("tsukuba_l.png", "tsukuba_r.png")