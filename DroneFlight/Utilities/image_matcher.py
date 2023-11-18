from typing import Union

from Utilities import io_utils
from Utilities.Geometry import Matrix3, Vector2, PerspectiveTransform2d
from matplotlib import pyplot as plt
import numpy as np
import os
import cv2


_FLANN_INDEX_LSH = 6
_FLANN_INDEX_KDTREE = 1


def _flann_orb():
    index_params = {"algorithm": _FLANN_INDEX_LSH, "table_number": 6, "key_size": 12, "multi_probe_level": 2}
    search_params = {"checks": 50}
    return cv2.FlannBasedMatcher(indexParams=index_params, searchParams=search_params)


def _flann_sift():
    index_params = {"algorithm": _FLANN_INDEX_KDTREE, "trees": 5}
    search_params = {"checks": 10}  # or pass empty dictionary
    return cv2.FlannBasedMatcher(index_params, search_params)


def _filter_matches(matches, threshold=0.5):
    good_matches = []
    for pair in matches:
        if len(pair) != 2:
            continue
        # if abs(pair[0].distance - pair[1].distance) / (pair[0].distance + pair[1].distance) < 0.55:
        if pair[0].distance >= threshold * pair[1].distance:
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


class ImageMatcher:
    __slots__ = ("_matcher", "_detector", "_threshold", "_img_1", "_img_2", "_kp_1",
                 "_kp_2", "_des_1", "_des_2", "_matches", "_good_matches", "_homography")

    def __init__(self, sift_or_orb: bool = True):
        self._threshold = 0.35
        self._img_1 = None
        self._img_2 = None
        self._des_1 = None
        self._des_2 = None
        self._kp_1 = None
        self._kp_2 = None
        self._matches = None
        self._homography = Matrix3.identity()
        self._good_matches = None
        if sift_or_orb:
            self._detector = cv2.SIFT_create()
            self._matcher = _flann_sift()
        else:
            self._detector = cv2.ORB_create(1000)
            self._matcher = _flann_orb()

    def match_images(self, image_1: np.ndarray, image_2: np.ndarray,
                     proj_transform_1: Matrix3 = None,
                     proj_transform_2: Matrix3 = None) -> bool:

        self._img_1 = image_1
        self._img_2 = image_2

        self._kp_1, self._des_1 = self._detector.detectAndCompute(self._img_1, None)
        self._kp_2, self._des_2 = self._detector.detectAndCompute(self._img_2, None)

        self._matches = self._matcher.knnMatch(self._des_1, self._des_2, k=2)
        self._good_matches = _filter_matches(self._matches, self._threshold)

        # maintaining list of index of descriptors
        # in query descriptors
        if proj_transform_1 is None:
            pts_1 = np.float32([self._kp_1[m.queryIdx].pt for m in self._good_matches]).reshape(-1, 1, 2)
        else:
            # proj_transform_1 = proj_transform_1.invert()
            points = tuple(tuple(proj_transform_1.perspective_multiply(Vector2(*self._kp_1[m.queryIdx].pt)))
                           for m in self._good_matches)
            pts_1 = np.float32(points).reshape(-1, 1, 2)

        # maintaining list of index of descriptors
        # in train descriptors
        if proj_transform_2 is None:
            pts_2 = np.float32([self._kp_2[m.trainIdx].pt for m in self._good_matches]).reshape(-1, 1, 2)
        else:
            # proj_transform_2 = proj_transform_2.invert()
            points = tuple(tuple(proj_transform_2.perspective_multiply(Vector2(*self._kp_2[m.trainIdx].pt)))
                           for m in self._good_matches)
            pts_2 = np.float32(points).reshape(-1, 1, 2)

        # finding  perspective transformation
        # between two planes
        try:
            matrix, mask = cv2.findHomography(pts_1, pts_2, cv2.RANSAC, 10.0)
            # print(matrix)
            self._homography = Matrix3.from_np_array(matrix)
            return True
        except:
            return False
        # return self.homography_matrix

    def match_images_from_file(self, image_1_src: str, image_2_src: str,
                               proj_transform_1: Matrix3 = None,
                               proj_transform_2: Matrix3 = None) -> bool:
        assert isinstance(image_1_src, str)
        assert isinstance(image_2_src, str)
        assert os.path.exists(image_1_src)
        assert os.path.exists(image_2_src)
        try:
            return self.match_images(io_utils.read_image(image_1_src, cv2.IMREAD_GRAYSCALE),
                                     io_utils.read_image(image_2_src, cv2.IMREAD_GRAYSCALE),
                                     proj_transform_1, proj_transform_2)
        except Exception as ex:
            print(f"Error occurs while image {image_1_src} and image {image_2_src} matching...\n Error:\n{ex}")
            return False

    def draw_matches(self):
        if not all(v is not None for v in (self._img_1, self._kp_1, self._img_2, self._kp_2, self._matches,
                                           self._threshold, self._homography)):
            print("nothing to draw...")
            return
        _draw_matches(self._img_1, self._kp_1, self._img_2, self._kp_2,
                      self._matches, self._threshold, self._homography)

    @property
    def threshold(self) -> float:
        return self._threshold

    @threshold.setter
    def threshold(self, value: float) -> None:
        assert isinstance(value, float)
        self._threshold = min(max(0.0, value), 1.0)

    @property
    def image_1(self) -> Union[np.ndarray, None]:
        return self._img_1

    @property
    def image_2(self) -> Union[np.ndarray, None]:
        return self._img_2

    @property
    def descriptors_1(self) -> Union[np.ndarray, None]:
        return self._des_1

    @property
    def descriptors_2(self) -> Union[np.ndarray, None]:
        return self._des_2

    @property
    def key_points_1(self) -> Union[np.ndarray, None]:
        return self._kp_1

    @property
    def key_points_2(self) -> Union[np.ndarray, None]:
        return self._kp_2

    @property
    def matches(self) -> Union[np.ndarray, None]:
        return self._matches

    @property
    def good_matches(self) -> Union[np.ndarray, None]:
        return self._good_matches

    @property
    def homography_matrix(self) -> Matrix3:
        return self._homography

