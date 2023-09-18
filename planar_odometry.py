from collections import namedtuple

import cv2

MAX_SIZE = 1000

FLANN_INDEX_KDTREE = 1

FLANN_INDEX_LSH = 6


class DetectorSettings(namedtuple('DetectorSettings',
                                  'detector, norm, algorithm, table_number, key_size, multi_probe_level')):
    def __new__(cls, json_node: dict):
        return super.__new__(    json_node['detector']           if 'detector' in json_node else 'orb',
                             int(json_node['norm'])              if 'norm' in json_node else cv2.NORM_L2,
                             int(json_node['algorithm'])         if 'algorithm' in json_node else FLANN_INDEX_LSH,
                             int(json_node['table_number'])      if 'table_number' in json_node else 6,
                             int(json_node['key_size'])          if 'key_size' in json_node else 12,
                             int(json_node['multi_probe_level']) if 'multi_probe_level' in json_node else 1)

    def __str__(self):
        return f"{{\n" \
               f"\t\"detector\":          \"{self.detector}\",\n" \
               f"\t\"norm\":              {self.norm},\n" \
               f"\t\"algorithm\":         {self.algorithm},\n" \
               f"\t\"table_number\":      {self.table_number},\n" \
               f"\t\"key_size\":          {self.key_size},\n" \
               f"\t\"multi_probe_level\": {self.multi_probe_level}\n" \
               f"}}"


def init_detector_matcher(settings: DetectorSettings):
    if settings.detector == 'sift':
        detector = cv2.SIFT_create()
        norm = cv2.NORM_L2
    elif settings.detector == 'surf':
        detector = cv2.xfeatures2d.SURF_create(800)
        norm = cv2.NORM_L2
    elif settings.detector == 'orb':
        detector = cv2.ORB_create(400)
        norm = cv2.NORM_HAMMING
    elif settings.detector == 'akaze':
        detector = cv2.AKAZE_create()
        norm = cv2.NORM_HAMMING
    elif settings.detector == 'brisk':
        detector = cv2.BRISK_create()
        norm = cv2.NORM_HAMMING
    else:
        return None, None   # Return None if unknown detector name

    if 'flann' in chunks:
        if norm == cv2.NORM_L2:
            flann_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        else:
            flann_params = dict(algorithm=FLANN_INDEX_LSH,
                                table_number=6,  # 12
                                key_size=12,  # 20
                                multi_probe_level=1)  # 2

        matcher = cv2.FlannBasedMatcher(flann_params)
    else:
        matcher = cv2.BFMatcher(norm)

    return detector, matcher


class POdometry:
    def __init__(self):
        ...