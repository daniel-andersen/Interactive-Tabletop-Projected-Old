import util
import numpy as np
import cv2
import math

class BrickRecognizer(object):

    output_src = None

    def __init__(self):
        pass

    def recognize_bricks(self, image):

        self.output_src = image.copy()

        params = cv2.SimpleBlobDetector_Params()

        # Change thresholds
        params.minThreshold = 10
        params.maxThreshold = 300

        # Filter by Area
        params.filterByArea = True
        params.minArea = 40

        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = 0.3

        # Filter by Convexity
        params.filterByConvexity = False
        params.minConvexity = 0.87

        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0.1

        detector = cv2.SimpleBlobDetector_create(params)

        return detector.detect(image)


    def get_output_image(self, index):
        return self.output_src


    def draw_bricks_on_image(self, image, keypoints):
        return cv2.drawKeypoints(image, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
