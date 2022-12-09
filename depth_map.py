if __name__ == '__main__':
    import cv2 as cv
    from matplotlib import pyplot as plt
#    img_left = cv.imread('tsukuba_l.png', cv.IMREAD_GRAYSCALE)
#    img_right = cv.imread('tsukuba_r.png', cv.IMREAD_GRAYSCALE)
    img_left = cv.imread('motorcycle_l.png', cv.IMREAD_GRAYSCALE)
    img_right = cv.imread('motorcycle_r.png', cv.IMREAD_GRAYSCALE)

    stereo = cv.StereoBM_create(numDisparities=0, blockSize=21)
    disparity = stereo.compute(img_left, img_right)
    plt.imshow(disparity, 'gray')
    plt.show()





 #   sift = cv.SIFT_create(74)

   # kp_left, descriptors_left = sift.detectAndCompute(img_left, None)
   # kp_right, descriptors_right = sift.detectAndCompute(img_right, None)
  #  matcher = cv.BFMatcher(cv.NORM_L2)
  #  matches = matcher.match(descriptors_left, descriptors_right)
 #   print(matches)
   # points_left = []
  #  points_right = []
  #  for match in matches:
#        points_left. append(kp_left [match.queryIdx].pt)
#        points_right.append(kp_right[match.queryIdx].pt)
#    print(points_left)
 #  cv.findEssentialMat(points_left, points_right, None, cv.RANSAC, 0.9, 1.0)