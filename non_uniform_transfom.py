from Utilities.Geometry import Matrix3, Vector2, PerspectiveTransform2d, Camera, Vector4
from matplotlib import pyplot as plt
import numpy as np
import os.path
import math
import cv2
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


def _flann_orb():
    FLANN_INDEX_LSH = 6
    index_params = {"algorithm": FLANN_INDEX_LSH, "table_number": 6, "key_size": 12, "multi_probe_level": 2}
    search_params = {"checks": 50}
    return cv2.FlannBasedMatcher(indexParams=index_params, searchParams=search_params)


def _flann_sift():
    FLANN_INDEX_KDTREE = 1
    index_params = {"algorithm": FLANN_INDEX_KDTREE, "trees": 5}
    search_params = {"checks": 10}  # or pass empty dictionary
    return cv2.FlannBasedMatcher(index_params, search_params)


def _filter_matches(matches, threshold=0.5):
    good_matches = []
    for pair in matches:
        if len(pair) != 2:
            continue
        if pair[0].distance > threshold * pair[1].distance:
            continue
        good_matches.append(pair[0])

    return good_matches  # [pair[0] for pair in matches if pair[0].distance < threshold * pair[1].distance]


def _matches_mask(matches, threshold=0.5):
    return [[1, 0] if m.distance < threshold * n.distance else [0, 0] for m, n in matches]


def _draw_matches(image_1, kp_1, image_2, kp_2, matches, threshold=0.5, homography=None):
    matches_mask = _matches_mask(matches, threshold=threshold)
    draw_params = {"matchColor": (0, 255, 0), "singlePointColor": (255, 0, 0),
                   "matchesMask": matches_mask, "flags": cv2.DrawMatchesFlags_DEFAULT}
    img3 = cv2.drawMatchesKnn(image_1, kp_1, image_2, kp_2, matches, None, **draw_params)
    if homography is not None:
        h, w = image_1.shape
        # saving all points in pts
        pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape((-1, 1, 2))
        for layer in pts:
            layer[0][0] += w
        dst = cv2.perspectiveTransform(pts, homography)
        img3 = cv2.polylines(img3, [np.int32(dst)], True, (255, 0, 0), 3)
    plt.imshow(img3, )
    plt.show()


def image_math_and_homography(image_1_src: str, image_2_src: str, sift_or_orb: bool = True):
    assert isinstance(image_1_src, str)
    assert isinstance(image_2_src, str)
    assert os.path.exists(image_1_src)
    assert os.path.exists(image_2_src)

    image_1 = cv2.imread(image_1_src, cv2.IMREAD_GRAYSCALE)
    image_2 = cv2.imread(image_2_src, cv2.IMREAD_GRAYSCALE)

    if sift_or_orb:
        _detector = cv2.SIFT_create()
        _matcher = _flann_sift()
    else:
        _detector = cv2.ORB_create(1000)
        _matcher = _flann_orb()

    kp_1, des_1 = _detector.detectAndCompute(image_1, None)
    kp_2, des_2 = _detector.detectAndCompute(image_2, None)

    matches = _matcher.knnMatch(des_1, des_2, k=2)
    # print(len(matches))
    good_matches = _filter_matches(matches, 0.5)
    # maintaining list of index of descriptors
    # in query descriptors
    pts_1 = np.float32([kp_1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # maintaining list of index of descriptors
    # in train descriptors
    pts_2 = np.float32([kp_2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # finding  perspective transformation
    # between two planes
    # print(f"len(pts_1) : {len(pts_1)} | len(pts_2) : {len(pts_2)}")
    matrix, mask = cv2.findHomography(pts_1, pts_2, cv2.RANSAC, 5.0)

    return Matrix3.from_np_array(matrix)
    # print(np.array(m).reshape(9))

    # _draw_matches(image_1, kp_1, image_2, kp_2, matches, threshold=0.5, homography=matrix)


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


if __name__ == "__main__":
    # self._z_far: float = 1000
    # self._z_near: float = 0.01
    # self._fov: float = 70.0
    # self._aspect: float = 10.0
    # self._ortho_size: float = 10.0
    # camera = Camera()
    # camera.aspect = 2.0
    # camera.fov = 90
    # print(camera.emit_ray(0, 0))
    # print(camera.emit_ray(1, 1))
    # print(camera.emit_ray(1, -1))
    # print(camera.emit_ray(-1, -1))
    # print(camera.emit_ray(-1, 1))
    # print(2.0 / math.tan(70 / 180 * math.pi))
    # directions_start = (Vector4(0, 1, 0.01, 1), Vector4(0, 1, 1000, 1))
    # directions_end   = (Vector4(1, 1, 1, 1), Vector4(1, 1, 1, 1))
    # print(camera.inv_projection)
    # print(camera.projection)
    # for ps in directions_start:
    #     print(f"{ps} | -> {camera.projection * ps}")
    # print(camera)
    # print()
    # perspective_transform_test()
    # exit()
    # build_test_data_for_image_track("salzburg_city_view_by_burtn-d61404o.jpg", "path_track")
    # exit()
    # directory  = "phantom_flight_1"
    directory = "path_track"
    images = [f"{directory}\\{src}" for src in os.listdir(directory) if src.endswith('png') or src.endswith('JPG')]
    images = sorted(images, key=image_index)
    [print(t) for t in images]
    positions_x = []
    positions_y = []

    transforms = [image_math_and_homography(img_1, img_2) for img_1, img_2 in zip(images[:-1], images[1:])]
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
