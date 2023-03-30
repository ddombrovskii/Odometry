import numpy as np
import cv2


class SLAM:
    def __init__(self, init_transform: np.ndarray, size=3000):
        self.orb = cv2.ORB_create(size)
        self._km = init_transform
        self._pm = np.zeros((3, 4), dtype=np.float32)
        self._pm[0:3, 0:3] = init_transform
        FLANN_INDEX_LSH = 6
        index_params = {"algorithm": FLANN_INDEX_LSH, "table_number": 6, "key_size": 12, "multi_probe_level": 1}
        search_params = {"checks": 50}
        self.flann = cv2.FlannBasedMatcher(indexParams=index_params, searchParams=search_params)
        self._curr_frame = None
        self._prev_frame = None
        self._transform_m = np.eye(4, dtype=np.float32)

    def _match_frames(self, frame: np.ndarray):
        if self._curr_frame is None:
            self._curr_frame = frame
            return None

        if self._prev_frame is None:
            self._prev_frame = self._curr_frame
            self._curr_frame = frame
            return None
        # Find the keypoints and descriptors with ORB
        kp1, des1 = self.orb.detectAndCompute(self._prev_frame, None)
        kp2, des2 = self.orb.detectAndCompute(self._curr_frame, None)
        if len(kp1) < 5:
            return None
        if len(kp2) < 5:
            return None

        self._prev_frame = self._curr_frame
        self._curr_frame = frame
        # Find matches
        matches = self.flann.knnMatch(des1, des2, k=2)

        # Find the matches there do not have a to high distance
        good = []
        try:
            for m, n in matches:
                if m.distance < 0.8 * n.distance:
                    good.append(m)
        except ValueError:
            pass
        # Get the image points form the good matches
        q1 = np.float32([kp1[m.queryIdx].pt for m in good])
        q2 = np.float32([kp2[m.trainIdx].pt for m in good])
        return q1, q2

    def _decompose_essential_mat(self, e_mat, q1, q2):
        def sum_z_cal_relative_scale(r_m, t_m):
            # Get the transformation matrix
            transform = np.eye(4, dtype=np.float32)
            transform[:3, :3] = r_m
            transform[:3, 3] = t_m
            # Make the projection matrix
            projection = np.matmul(np.concatenate((self._km, np.zeros((3, 1))), axis=1), transform)

            # Triangulate the 3D points
            hom_Q1 = cv2.triangulatePoints(self._pm, projection, q1.T, q2.T)
            # Also seen from cam 2
            hom_Q2 = np.matmul(transform, hom_Q1)

            # Un-homogenize
            uhom_Q1 = hom_Q1[:3, :] / hom_Q1[3, :]
            uhom_Q2 = hom_Q2[:3, :] / hom_Q2[3, :]

            # Find the number of points there has positive z coordinate in both cameras
            sum_of_pos_z_Q1 = sum(uhom_Q1[2, :] > 0)
            sum_of_pos_z_Q2 = sum(uhom_Q2[2, :] > 0)

            # Form point pairs and calculate the relative scale
            relative_scale = np.mean(np.linalg.norm(uhom_Q1.T[:-1] - uhom_Q1.T[1:], axis=-1)/
                                     np.linalg.norm(uhom_Q2.T[:-1] - uhom_Q2.T[1:], axis=-1))
            return sum_of_pos_z_Q1 + sum_of_pos_z_Q2, relative_scale

        # Decompose the essential matrix
        try:
            # print(f"e_mat {e_mat.shape}")
            rot_1, rot_2, t = cv2.decomposeEssentialMat(e_mat)
        except RuntimeError as err:
            return None, None
        t = np.squeeze(t)

        # Make a list of the different possible pairs
        pairs = [[rot_1, t], [rot_1, -t], [rot_2, t], [rot_2, -t]]

        # Check which solution there is the right one
        z_sums = []
        relative_scales = []
        for rot, t in pairs:
            z_sum, scale = sum_z_cal_relative_scale(rot, t)
            z_sums.append(z_sum)
            relative_scales.append(scale)

        # Select the pair there has the most points with positive z coordinate
        right_pair_idx = np.argmax(z_sums)
        right_pair = pairs[right_pair_idx]
        relative_scale = relative_scales[right_pair_idx]
        rot_1, t = right_pair
        t = t * relative_scale
        return rot_1, t

    def _get_pose(self, q1: np.ndarray, q2: np.ndarray):
        # Essential matrix
        if len(q1) <= 2:
            return self.transform

        if len(q2) <= 2:
            return self.transform

        e_m, _ = cv2.findEssentialMat(q1, q2, self._km, threshold=1)

        if e_m is None:
            return self.transform

        # Decompose the Essential matrix into R and t
        rot_m, t = self._decompose_essential_mat(e_m[:3][:3], q1, q2)
        if rot_m is None:
            return self._transform_m

        # Get transformation matrix
        self._transform_m = np.eye(4, dtype=np.float32)
        self._transform_m[:3, :3] = rot_m
        self._transform_m[:3, 3] = t
        return self._transform_m

    @property
    def transform(self) -> np.ndarray:
        return self._transform_m

    def __call__(self, frame: np.ndarray):
        q1q2 = self._match_frames(frame)
        if q1q2 is None:
            return None
        return self._get_pose(*q1q2)

