from matplotlib import pyplot as plt
from os.path import isfile, join
from Utilities import Vector2
from typing import List, Tuple
from os import listdir
import numpy as np
import cv2 as cv


# https://github.com/niconielsen32/ComputerVision/blob/master/VisualOdometry/visual_odometry.py
# https://github.com/niconielsen32/ComputerVision/blob/master/LiveCameraTrajectory/liveCameraPoseEstimation.py
# KITTI Camera
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


def decompose_essential_mat(essential_matrix: np.ndarray, q_1: np.ndarray, q_2: np.ndarray) -> np.ndarray:
    rot_1, rot_2, trans = cv.decomposeEssentialMat(essential_matrix)

    trans = np.squeeze(trans)

    transformations = (build_transform(rot_1, trans), build_transform(rot_2, trans),
                       build_transform(rot_1, -trans), build_transform(rot_2, -trans))
    # camera = np.concatenate((camera_k, np.zeros((3, 1))), axis=1) equal to camera_p
    projections = (camera_p @ transformations[0], camera_p @ transformations[1],
                   camera_p @ transformations[2], camera_p @ transformations[3])

    positives = []

    for P, T in zip(projections, transformations):
        # hom_q1 = cv.triangulatePoints(camera, p, 1.T, q2.T)  # visual odometry
        hom_q1 = cv.triangulatePoints(P, P, q_1.T, q_2.T)  # Camera Tracking System
        hom_q2 = T @ hom_q1
        uhom_q1 = hom_q1[:3, :] / hom_q1[3, :]
        uhom_q2 = hom_q2[:3, :] / hom_q2[3, :]
        # Find the number of points there has positive z coordinate in both cameras
        # sum_of_pos_z = sum(uhom_q2[2, :] > 0) + sum(uhom_q1[2, :] > 0)
        # relative_scale = np.mean(np.linalg.norm(uhom_q1.T[:-1] - uhom_q1.T[1:], axis=-1) /
        #                          np.linalg.norm(uhom_q2.T[:-1] - uhom_q2.T[1:], axis=-1))
        #                          may cause zero division error
        sum_of_pos_z = sum(uhom_q1[2, :] > 0) + sum(uhom_q2[2, :] > 0)
        n_1 = np.linalg.norm(uhom_q1.T[:-1] - uhom_q1.T[1:], axis=-1)
        n_2 = np.linalg.norm(uhom_q2.T[:-1] - uhom_q2.T[1:], axis=-1)
        relative_scale = sum(Vector2(ai / bi, 1.0) for ai, bi in zip(n_1.flat, n_2.flat) if bi != 0.0)
        positives.append(sum_of_pos_z + relative_scale.x / relative_scale.y)

    return transformations[np.argmax(positives)]


def get_pose(q_1: np.ndarray, q_2: np.ndarray):
    e_m, e_m_mask = cv.findEssentialMat(q_1, q_2, camera_k, threshold=1)
    return decompose_essential_mat(e_m, q_1, q_2)


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
        for fpath, image in self._images:
            self._img_curr = image
            if self._img_prev is None:
                self._img_prev = self._img_curr
                continue

            kp1, des1 = self._orb.detectAndCompute(self._img_prev, None)
            kp2, des2 = self._orb.detectAndCompute(self._img_curr, None)

            if des1 is None:
                continue
            if des2 is None:
                continue
            if len(kp1) < 10:
                continue
            if len(kp2) < 10:
                continue

            matches = self._flann.knnMatch(des1, des2, k=2)
            matches_mask = [(0, 0) for i in range(len(matches))]
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
                img3 = cv.drawMatchesKnn(self._img_prev, kp1, self._img_curr, kp2, matches, None, **draw_params)
                cv.imshow('SIFT-odometry', img3)
                cv.waitKey(100)
            self._img_prev = self._img_curr
            q1 = np.float32([kp1[m.queryIdx].pt for m in matches_good])
            q2 = np.float32([kp2[m.trainIdx].pt for m in matches_good])
            self._transforms.append(self._transforms[-1] @ get_pose(q1, q2))

    def draw_path(self):
        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        draw_transforms(self._transforms, axis=ax)
        draw_transforms(self._transforms_gt, 'b', axis=ax)
        plt.show()


if __name__ == "__main__":
    # 'E:/GitHub/Odometry/Odometry/Cameras/saved_frames/2_4_2023')
    #
    ct = CameraTrack(images_src="E:/GitHub/Odometry/Odometry/Cameras/image_l",
                     gt_poses_src='E:/GitHub/Odometry/Odometry/Cameras/image_l/poses.txt')
    ct.compute()
    ct.draw_path()

