from __future__ import print_function
import numpy as np
import cv2
import time


def triangulate(proj_mat1, pts0, pts1):
    proj_mat0 = np.zeros((3, 4))
    proj_mat0[:, :3] = np.eye(3)
    pts0, pts1 = self.normalize(pts0), self.normalize(pts1)
    pts4d = cv2.triangulatePoints(proj_mat0, proj_mat1, pts0.T, pts1.T).T
    pts4d /= pts4d[:, 3:]
    out = np.delete(pts4d, 3, 1)
    print(out)
    return out


def getP(rmat, tvec):
       P = np.concatenate([rmat, tvec.reshape(3, 1)], axis = 1)
       return P