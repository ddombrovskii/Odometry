import time

from matplotlib import pyplot as plt
from os.path import isfile, join
from typing import List, Tuple
from os import listdir
import numpy as np
import cv2 as cv


# https://github.com/niconielsen32/ComputerVision/blob/master/VisualOdometry/visual_odometry.py
# https://github.com/niconielsen32/ComputerVision/blob/master/LiveCameraTrajectory/liveCameraPoseEstimation.py
# KITTI Camera
from Utilities.Geometry import Matrix4

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
    imgs  = [cv.imread(f, cv.IMREAD_GRAYSCALE) for f in files]
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
    z_sums  = []
    z_scale = []
    for T, P in zip(transformations, projections):
        hom_q1 = cv.triangulatePoints(camera_p, P, q_1.T, q_2.T)  # Camera Tracking System
        hom_q2 = np.matmul(T, hom_q1)
        uhom_q1 = hom_q1[:3, :] / hom_q1[3, :]  # Пространственные координаты особых точек, которые видит камера
        uhom_q2 = hom_q2[:3, :] / hom_q2[3, :]  # Пространственные координаты особых точек, которые видит камера
        # Find the number of points there has positive z coordinate in both cameras
        z_sums.append(sum(uhom_q2[2, :] > 0) + sum(uhom_q1[2, :] > 0))
        z_scale.append(np.mean(np.linalg.norm(uhom_q1.T[:-1] - uhom_q1.T[1:], axis=-1) /
                               np.linalg.norm(uhom_q2.T[:-1] - uhom_q2.T[1:], axis=-1)))

    right_pair_idx = np.argmax(z_sums)
    transform = transformations[right_pair_idx]
    transform[:3, 3] *= z_scale[right_pair_idx]
    return transform


def get_pose(q_1: np.ndarray, q_2: np.ndarray, camera_k: np.ndarray, camera_p: np.ndarray):
    e_m, e_m_mask = cv.findEssentialMat(q_1, q_2, camera_k)  #, threshold=1)
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
        self._transforms.append(np.eye(4, dtype=np.float32) if len(self._transforms_gt) == 0 else self._transforms_gt[0])
        self._orb = cv.ORB_create(3000)
        self._img_curr = None
        self._img_prev = None
        FLANN_INDEX_LSH = 6
        index_params = {"algorithm": FLANN_INDEX_LSH, "table_number": 6, "key_size": 12, "multi_probe_level": 1}
        search_params = {"checks": 50}
        self._flann = cv.FlannBasedMatcher(indexParams=index_params, searchParams=search_params)
        self.display: bool = True

    def compute(self):
        with open('log.txt', 'wt') as output:  # открываем файл для записи триангуляционных данных
            for index in range(len(self._images) - 1):

                kp1, des1 = self._orb.detectAndCompute(self._images[index][1], None)
                kp2, des2 = self._orb.detectAndCompute(self._images[index + 1][1], None)

                if des1 is None:
                    self._img_prev = self._img_curr
                    continue
                if des2 is None:
                    self._img_prev = self._img_curr
                    continue
                if len(kp1) < 10:
                    self._img_prev = self._img_curr
                    continue
                if len(kp2) < 10:
                    self._img_prev = self._img_curr
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
                    img3 = cv.drawMatchesKnn(self._images[index][1], kp1, self._images[index+1][1], kp2, matches, None, **draw_params)
                    cv.imshow('SIFT-odometry', img3)
                    cv.waitKey(100)
                self._img_prev = self._img_curr
                q1 = np.float32([kp1[m.queryIdx].pt for m in matches_good])
                q2 = np.float32([kp2[m.trainIdx].pt for m in matches_good])
                # по результатам q1 и q2 получаем цвета из _img_prev и _img_curr соответсвенно
                t = get_pose(q1, q2, self._camera_k, self._camera_p) # дополнительно рассчитывает пространственное полежние  q1, q2
                self._transforms.append(np.matmul(self._transforms[-1], np.linalg.inv(t)))
                # тут перевод в мировую систему координтат q1, q2
                # запись в файл output
                self._img_prev = self._img_curr

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
    n = 1000000
    for _ in range(n):
        t_start = time.perf_counter()
        a = np.eye(4, dtype=float)
        t_total +=  time.perf_counter() - t_start
    print(f"np 4x4 matrix identity create time: {t_total}")
    t_total = 0.0
    for _ in range(n):
        t_start = time.perf_counter()
        a = Matrix4.identity()
        t_total +=  time.perf_counter() - t_start
    print(f"my 4x4 matrix identity create time: {t_total}")
    np_m = np.array([[1, 2, 0, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 0, 15, 16]], dtype=float)
    my_m = Matrix4(1, 2, 0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0, 15, 16)
    for _ in range(n):
        t_start = time.perf_counter()
        a = np.linalg.inv(np_m)
        t_total +=  time.perf_counter() - t_start
    print(f"np 4x4 matrix inversion time: {t_total}")
    t_total = 0.0
    for _ in range(n):
        t_start = time.perf_counter()
        a = my_m.invert()
        t_total +=  time.perf_counter() - t_start
    print(f"my 4x4 matrix inversion time: {t_total}")
    t_total = 0.0
    for _ in range(n):
        t_start = time.perf_counter()
        a = np_m @ np_m
        t_total +=  time.perf_counter() - t_start
    print(f"np 4x4 matrix multiplication time: {t_total}")
    t_total = 0.0
    for _ in range(n):
        t_start = time.perf_counter()
        a = my_m * my_m
        t_total +=  time.perf_counter() - t_start
    print(f"my 4x4 matrix multiplication time: {t_total}")



if __name__ == "__main__":
    # 'E:/GitHub/Odometry/Odometry/Cameras/saved_frames/2_4_2023')
    #
    # speed_test()
    # exit()
    ct = CameraTrack(images_src="E:/GitHub/Odometry/Odometry/Cameras/image_l",
                     gt_poses_src='E:/GitHub/Odometry/Odometry/Cameras/image_l/poses.txt')
    ct.compute()
    ct.draw_path()

