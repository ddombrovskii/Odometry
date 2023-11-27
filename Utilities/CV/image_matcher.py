from Utilities.Geometry import Matrix3, Vector2
from Utilities.Geometry import set_indent_level
from matplotlib import pyplot as plt
from Utilities import io_utils
from typing import Union
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

    def __repr__(self):
        val =  f"\t{{\n" \
               f"\t\t\"threshold\":          {self.threshold:4f},\n" \
               f"\t\t\"kp1_count\":          {0 if self._kp_1 is None else len(self._kp_1):5},\n" \
               f"\t\t\"kp2_count\":          {0 if self._kp_2 is None else len(self._kp_2):5},\n" \
               f"\t\t\"desc1_count\":        {0 if self._des_1 is None else len(self._des_1):5},\n" \
               f"\t\t\"desc2_count\":        {0 if self._des_2 is None else len(self._des_2):5},\n" \
               f"\t\t\"matches_count\":      {0 if self._matches is None else len(self._matches):5},\n" \
               f"\t\t\"good_matches_count\": {0 if self._good_matches is None else len(self._good_matches):5},\n" \
               f"\t\t\"homography\":\n{self._homography}\n" \
               f"\t}}"
        return val

    def __str__(self):
        def _kp_parce(kp, indent='\t'):
            return f"{indent}{{\"angle\": {kp.angle:4.3f}, " \
                   f"\"class_id\":{kp.class_id:4}, " \
                   f"\"octave\":  {kp.octave:8}, " \
                   f"\"response\":{kp.response:4.8f}, " \
                   f"\"pt\": [{', '.join(f'{v:.3f}'for v in kp.pt)}]}}"

        def _kps_parce(points, indent=''):
            if points is None:
                return "[]"
            sep = ',\n'
            return f"[\n{sep.join(_kp_parce(kp, indent)for kp in points)}\n{indent}]"

        def _desc_parse(desc, indent='\t'):
            val =  f",\n".join(f"{indent}[{', '.join(f'{v:.3f}' for v in row)}]"for row in desc)
            return f"{indent}[\n{val}\n{indent}]"

        def _matches_pair_parce(m, indent='\t'):
            if len(m) == 0:
                return f"{indent}[]"
            if len(m) == 0:
                return f"{indent}[\n" \
                       f"{indent}{{\"distance\": {m[0].distance}, \"imgIdx\":{m[0].imgIdx}, \"queryIdx\":{m[0].queryIdx}, \"trainIdx\":{m[0].trainIdx}}}\n" \
                       f"{indent}\n]"

            return f"{indent}[\n" \
                   f"{indent}{{\"distance\": {m[0].distance}, \"imgIdx\":{m[0].imgIdx}, \"queryIdx\":{m[0].queryIdx}, \"trainIdx\":{m[0].trainIdx}}},\n" \
                   f"{indent}{{\"distance\": {m[1].distance}, \"imgIdx\":{m[1].imgIdx}, \"queryIdx\":{m[1].queryIdx}, \"trainIdx\":{m[1].trainIdx}}}\n" \
                   f"{indent}\n]"

        def _matches_parce(matches, indent='\t'):
            sep = ',\n'
            if matches is None:
                return f"[]"
            return f"[{indent}\n{sep.join(_matches_pair_parce(m) for m in matches)}\n{indent}]"

        set_indent_level(1)
        tab = '\t'
        val =  f"{{" \
               f"\t\"threshold\":          {self.threshold:4f},\n" \
               f"\t\"kp1_count\":          {0 if self._kp_1 is None else len(self._kp_1):5},\n" \
               f"\t\"kp1\":                \n{_kps_parce(self._kp_1, tab)},\n" \
               f"\t\"kp2_count\":          {0 if self._kp_2 is None else len(self._kp_2):5},\n" \
               f"\t\"kp2\":                \n{_kps_parce(self._kp_2, tab)},\n" \
               f"\t\"desc1_count\":        {0 if self._des_1 is None else len(self._des_1):5},\n" \
               f"\t\"desc1\":              \n{_desc_parse(self._des_1, tab)},\n" \
               f"\t\"desc2_count\":        {0 if self._des_2 is None else len(self._des_2):5},\n" \
               f"\t\"desc2\":              \n{_desc_parse(self._des_2, tab)},\n" \
               f"\t\"matches_count\":      {0 if self._matches is None else len(self._matches):5},\n" \
               f"\t\"matches\":            \n{_matches_parce(self._matches)},\n" \
               f"\t\"good_matches_count\": {0 if self._good_matches is None else len(self._good_matches):5},\n" \
               f"\t\"good_matches\":       \n{_matches_parce(self._good_matches)},\n" \
               f"\t\"homography\":\n{self._homography}\n" \
               f"}}"
        set_indent_level(0)
        return val

    def __init__(self, sift_or_orb: bool = True):
        self._threshold = 0.35
        self._img_1 = None
        self._img_2 = None
        self._des_1 = None
        self._des_2 = None
        self._kp_1 = None
        self._kp_2 = None
        self._matches = None
        self._good_matches = None
        self._homography = Matrix3.identity()
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
            points = tuple(tuple(proj_transform_1.perspective_multiply(Vector2(*self._kp_1[m.queryIdx].pt)))
                           for m in self._good_matches)
            pts_1 = np.float32(points).reshape(-1, 1, 2)

        # maintaining list of index of descriptors
        # in train descriptors
        if proj_transform_2 is None:
            pts_2 = np.float32([self._kp_2[m.trainIdx].pt for m in self._good_matches]).reshape(-1, 1, 2)
        else:
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

