import time

from matplotlib import pyplot as plt
from os.path import isfile, join
from typing import List, Tuple, Dict
from os import listdir
import numpy as np
import cv2 as cv

# https://github.com/niconielsen32/ComputerVision/blob/master/VisualOdometry/visual_odometry.py
# https://github.com/niconielsen32/ComputerVision/blob/master/LiveCameraTrajectory/liveCameraPoseEstimation.py
# KITTI Camera
from UIQt.GLUtilities.gl_tris_mesh import create_box, write_obj_mesh, TrisMesh
from Utilities.Geometry import Matrix4, Vector3
from Utilities.Geometry.voxel import Voxel

camera_k = np.array([[7.070912000000e+02, 0.000000000000e+00, 6.018873000000e+02],
                     [0.000000000000e+00, 7.070912000000e+02, 1.831104000000e+02],
                     [0.000000000000e+00, 0.000000000000e+00, 1.000000000000e+00]])

camera_p = camera_k @ np.array(((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0)), dtype=np.float32)


# Microsoft Camera
# camera_k = np.array([[890.9132532946423, 0.0, 304.91274981959896],
#                      [0.0, 921.2595350054454, 265.2413569408279],
#                      [0.0, 0.0, 1.0]])

# camera_p = camera_k @ np.array(((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0)), dtype=np.float32)


def build_transform(r: np.ndarray, t: np.ndarray) -> np.ndarray:
    """
    Build transform matrix
    :param r: rotation 3x3 matrix
    :param t: translation 3x1 vector
    :return:
    """
    tr = np.eye(4, dtype=np.float32)
    tr[:3, :3] = r
    tr[:3, 3] = t
    return tr


def load_images(path: str):
    files = [f"{path}/{p}" for p in listdir(path) if isfile(join(path, p))]
    imgs = [cv.imread(f, cv.IMREAD_GRAYSCALE) for f in files]
    return [(f, i) for f, i in zip(files, imgs)]


def load_calib(path: str):
    """
    Loads the calibration of the camera
    Parameters
    ----------
    filepath (str): The file path to the camera file
    Returns
    -------
    K (ndarray): Intrinsic parameters
    P (ndarray): Projection matrix
    """
    with open(path, 'r') as f:
        params = np.fromstring(f.readline(), dtype=np.float32, sep=' ')
        P = np.reshape(params, (3, 4))
        K = P[0:3, 0:3]
    return K, P


def load_poses(filepath):
    """
     Loads the GT poses
     Parameters
     ----------
     filepath (str): The file path to the poses file
     Returns
     -------
     poses (ndarray): The GT poses
     """
    poses = []
    with open(filepath, 'r') as f:
        for line in f.readlines():
            t = np.fromstring(line, dtype=np.float32, sep=' ')
            t = t.reshape(3, 4)
            t = np.vstack((t, (0.0, 0.0, 0.0, 1.0)))
            poses.append(t)
    return poses


def draw_transforms(t_list: List[np.ndarray], color='k', axis=None):
    x = [tr[0][3] for tr in t_list]
    y = [tr[1][3] for tr in t_list]
    z = [tr[2][3] for tr in t_list]
    ex = [tr[:][0] for tr in t_list]
    ey = [tr[:][1] for tr in t_list]
    ez = [tr[:][2] for tr in t_list]
    if axis is None:
        figure, axis = plt.subplots(subplot_kw={"projection": "3d"})
    axis.plot(x, y, z, color)
    for i in range(min(128, len(x))):
        axis.plot([x[i], x[i] + ex[i][0]],
                  [y[i], y[i] + ex[i][1]],
                  [z[i], z[i] + ex[i][2]], 'r')
        axis.plot([x[i], x[i] + ey[i][0]],
                  [y[i], y[i] + ey[i][1]],
                  [z[i], z[i] + ey[i][2]], 'g')
        axis.plot([x[i], x[i] + ez[i][0]],
                  [y[i], y[i] + ez[i][1]],
                  [z[i], z[i] + ez[i][2]], 'b')


def draw_transforms_xz(t_list: List[np.ndarray], color='k', axis=None):
    x = [tr[0][3] for tr in t_list]
    z = [tr[2][3] for tr in t_list]
    ex = [tr[:][0] for tr in t_list]
    ez = [tr[:][2] for tr in t_list]
    if axis is None:
        figure, axis = plt.subplots()
    axis.plot(x, z, color)
    for i in range(min(128, len(x))):
        axis.plot([x[i], x[i] + ex[i][0]],
                  [z[i], z[i] + ex[i][2]], 'r')
        axis.plot([x[i], x[i] + ez[i][0]],
                  [z[i], z[i] + ez[i][2]], 'b')


def decompose_essential_mat(essential_matrix: np.ndarray, q_1: np.ndarray, q_2: np.ndarray, camera_p) -> np.ndarray:
    rot_1, rot_2, trans = cv.decomposeEssentialMat(essential_matrix)

    trans = np.squeeze(trans)

    transformations = (build_transform(rot_1, trans), build_transform(rot_2, trans),
                       build_transform(rot_1, -trans), build_transform(rot_2, -trans))

    # camera = np.concatenate((camera_k, np.zeros((3, 1))), axis=1) equal to camera_p
    projections = (camera_p @ transformations[0], camera_p @ transformations[1],
                   camera_p @ transformations[2], camera_p @ transformations[3])
    z_sums = -1e32  # []
    z_scale = -1.0  # []
    z_sums_curr = 0
    transformation = None
    target_points = None
    for T, P in zip(transformations, projections):
        hom_q1 = cv.triangulatePoints(camera_p, P, q_1.T, q_2.T)  # Camera Tracking System
        hom_q2 = np.matmul(T, hom_q1)
        hom_q1[:3, :] /= hom_q1[3, :]  # Пространственные координаты особых точек, которые видит камера 1
        hom_q2[:3, :] /= hom_q2[3, :]  # Пространственные координаты особых точек, которые видит камера 2

        hom_q1[3, :] = 1.0
        hom_q2[3, :] = 1.0

        z_sums_curr = sum(hom_q2[2, :] > 0) + sum(hom_q1[2, :] > 0)
        if z_sums_curr < z_sums:
            continue
        # Find the number of points there has positive z coordinate in both cameras
        z_sums = z_sums_curr
        z_scale = np.mean(np.linalg.norm(hom_q1.T[:-1] - hom_q1.T[1:], axis=-1) /
                          np.linalg.norm(hom_q2.T[:-1] - hom_q2.T[1:], axis=-1))
        transformation = T
        transformation[:3, 3] *= z_scale

    return transformation, hom_q2


def get_pose(q_1: np.ndarray, q_2: np.ndarray, camera_k: np.ndarray, camera_p: np.ndarray):
    e_m, e_m_mask = cv.findEssentialMat(q_1, q_2, camera_k)  # , threshold=2.)
    return decompose_essential_mat(e_m, q_1, q_2, camera_p)


class CameraTrack:
    def __init__(self, images_src, calib_info_src: str = None, gt_poses_src: str = None):
        self._images: List[Tuple[str, np.ndarray]] = load_images(images_src)
        if gt_poses_src is not None:
            self._transforms_gt: List[np.ndarray] = load_poses(gt_poses_src)
        else:
            self._transforms_gt = []
        if calib_info_src is None:
            # KITTI Camera
            self._camera_k, self._camera_p = camera_k, camera_p
        else:
            self._camera_k, self._camera_p = load_calib(calib_info_src)
        self._transforms: List[np.ndarray] = []
        self._transforms.append(
            np.eye(4, dtype=np.float32) if len(self._transforms_gt) == 0 else self._transforms_gt[0])
        self._orb = cv.ORB_create(3000)
        self._img_curr = None
        self._img_prev = None
        FLANN_INDEX_LSH = 6
        index_params = {"algorithm": FLANN_INDEX_LSH, "table_number": 6, "key_size": 12, "multi_probe_level": 2}
        search_params = {"checks": 10}
        self._flann = cv.FlannBasedMatcher(indexParams=index_params, searchParams=search_params)
        self.display: bool = True
        self._voxel_size = 0.5
        self._voxels = set()

    def compute(self):
        mesh = TrisMesh()
        with open('voxels_info.json', 'wt') as output:  # открываем файл для записи триангуляционных данных
            print(f"{{\n\t\"voxel_size\": {self._voxel_size},\n\t\"voxels\": [", file=output)
            for index in range(len(self._images) - 1):

                kp1, des1 = self._orb.detectAndCompute(self._images[index][1], None)
                kp2, des2 = self._orb.detectAndCompute(self._images[index + 1][1], None)

                if des1 is None:
                    continue
                if des2 is None:
                    continue
                if len(kp1) < 10:
                    continue
                if len(kp2) < 10:
                    continue

                matches = self._flann.knnMatch(des1, des2, k=2)
                matches_mask = [(0, 0) for _ in range(len(matches))]
                matches_good = []

                for i, match in enumerate(matches):
                    if len(match) != 2:
                        continue
                    m, n = match
                    if m.distance < 0.5 * n.distance:
                        matches_mask[i] = (1, 0)
                        matches_good.append(m)
                # Sort them in the order of their distance.
                if self.display:
                    draw_params = dict(matchColor=(0, 255, 0), singlePointColor=(255, 0, 0),
                                       matchesMask=matches_mask, flags=2)
                    img3 = cv.drawMatchesKnn(self._images[index][1], kp1, self._images[index + 1][1], kp2, matches,
                                             None, **draw_params)
                    cv.imshow('SIFT-odometry', img3)
                    cv.waitKey(10)
                self._img_prev = self._img_curr
                q1 = np.float32([kp1[m.queryIdx].pt for m in matches_good])
                q2 = np.float32([kp2[m.trainIdx].pt for m in matches_good])
                # по результатам q1 и q2 получаем цвета из _img_prev и _img_curr соответсвенно
                t, u_hom_pnts = get_pose(q1, q2, self._camera_k,
                                         self._camera_p)  # дополнительно рассчитывает пространственное полежние  q1, q2
                if t is None:
                    continue

                self._transforms.append(np.matmul(self._transforms[-1], np.linalg.inv(t)))

                points = self._transforms[-1] @ u_hom_pnts
                # points = u_hom_pnts
                for x, y, z, _ in points.T:
                    # x, y, z = t[:3, :3] @ u_hom_pnts[:, i] + t[:3, 3]
                    ijk = (int(x / self._voxel_size), int(y / self._voxel_size), int(z / self._voxel_size))
                    if ijk not in self._voxels:
                        center = Vector3((ijk[0] + 0.5) * self._voxel_size,
                                         (ijk[1] + 0.5) * self._voxel_size,
                                         (ijk[2] + 0.5) * self._voxel_size)
                        voxel = Voxel(center, self._voxel_size)
                        mesh.merge(create_box(Vector3(center.x - self._voxel_size * 0.5,
                                                      center.y - self._voxel_size * 0.5,
                                                      center.z - self._voxel_size * 0.5),
                                              Vector3(center.x + self._voxel_size * 0.5,
                                                      center.y + self._voxel_size * 0.5,
                                                      center.z + self._voxel_size * 0.5)))
                        print(Voxel(center, self._voxel_size), file=output, end=',\n')
                        self._voxels.update(ijk)

                # тут перевод в мировую систему координтат q1, q2
                # запись в файл output
                # self._img_prev = self._img_curr
            output.seek(output.tell() - 3, 0)
            print('\n\t]\n}', file=output)
            write_obj_mesh(mesh, 'voxels.obj')

    def draw_path(self):
        fig, ax = plt.subplots()  # (subplot_kw={"projection": "3d"})
        draw_transforms_xz(self._transforms, axis=ax)
        draw_transforms_xz(self._transforms_gt, 'b', axis=ax)
        plt.show()


def speed_test():
    # np 4x4 matrix identity create time: 1.149396504915785  sec for 1000000 iterations
    # my 4x4 matrix identity create time: 1.229776706022676  sec for 1000000 iterations
    # np 4x4 matrix inversion time:       130.61569990747375 sec for 1000000 iterations
    # my 4x4 matrix inversion time:       6.819007195997983  sec for 1000000 iterations
    # np 4x4 matrix multiplication time:  1.2466165156802163 sec for 1000000 iterations
    # my 4x4 matrix multiplication time:  5.52913630718831   sec for 1000000 iterations
    t_start = 0.0
    t_total = 0.0
    n = 100000

    for _ in range(n):
        t_start = time.perf_counter()
        a = np.eye(4, dtype=float)
        t_total += time.perf_counter() - t_start
    print(f"np 4x4 matrix identity create time: {t_total}")
    t_total = 0.0
    for _ in range(n):
        t_start = time.perf_counter()
        a = Matrix4.identity()
        t_total += time.perf_counter() - t_start
    print(f"my 4x4 matrix identity create time: {t_total}")
    np_m = np.array([[1, 2, 0, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 0, 15, 16]], dtype=float)
    my_m = Matrix4(1, 2, 0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0, 15, 16)
    for _ in range(n):
        t_start = time.perf_counter()
        a = np.linalg.inv(np_m)
        t_total += time.perf_counter() - t_start
    print(f"np 4x4 matrix inversion time: {t_total}")
    t_total = 0.0
    for _ in range(n):
        t_start = time.perf_counter()
        a = my_m.invert()
        t_total += time.perf_counter() - t_start
    print(f"my 4x4 matrix inversion time: {t_total}")
    t_total = 0.0
    for _ in range(n):
        t_start = time.perf_counter()
        a = np_m @ np_m
        t_total += time.perf_counter() - t_start
    print(f"np 4x4 matrix multiplication time: {t_total}")
    t_total = 0.0
    for _ in range(n):
        t_start = time.perf_counter()
        a = my_m * my_m
        t_total += time.perf_counter() - t_start
    print(f"my 4x4 matrix multiplication time: {t_total}")


if __name__ == "__main__":
    # box = create_box()
    # write_obj_mesh(box, 'box.obj')
    # 'E:/GitHub/Odometry/Odometry/Cameras/saved_frames/2_4_2023')
    #
    speed_test()
    exit()
    ct = CameraTrack(images_src="E:/GitHub/Odometry/Odometry/Cameras/image_l",
                     gt_poses_src='E:/GitHub/Odometry/Odometry/Cameras/image_l/poses.txt')
    ct.compute()
    ct.draw_path()

# if __name__ == "__main__":
#     code = \
#         """
#                    Matrix3(self[0] * other[0] + self[1] * other[3] + self[2] * other[6],
#                            self[0] * other[1] + self[1] * other[4] + self[2] * other[7],
#                            self[0] * other[2] + self[1] * other[5] + self[2] * other[8],
#                            self[3] * other[0] + self[4] * other[3] + self[5] * other[6],
#                            self[3] * other[1] + self[4] * other[4] + self[5] * other[7],
#                            self[3] * other[2] + self[4] * other[5] + self[5] * other[8],
#                            self[6] * other[0] + self[7] * other[3] + self[8] * other[6],
#                            self[6] * other[1] + self[7] * other[4] + self[8] * other[7],
#                            self[6] * other[2] + self[7] * other[5] + self[8] * other[8])
#     """
#     open_brackets =  [i for i, ch in enumerate(code) if ch == '[']
#     close_brackets = [i for i, ch in enumerate(code) if ch == ']']
#     # print(open_brackets)
#     # print(close_brackets)
#     new_code = ''
#     prev_start, prev_end = 0, 0
#     for start, end in zip(open_brackets, close_brackets):
#         value = int(code[start + 1: end])
#         # print(value)
#         new_code += code[prev_end: start]
#         new_code += f".m{value // 3}{value % 3}"
#         prev_start, prev_end = end, end + 1
#     print(new_code)
