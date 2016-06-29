import cv2
import numpy as np
from marker import Marker


class ImageMarker(Marker):
    def __init__(self, marker_image, min_matches=10):
        """
        :param marker_image: Marker image
        :param min_matches: Minimum number of matches for marker to be detected
        """
        super(ImageMarker, self).__init__()

        self.min_matches = min_matches

        # Get size of query image
        self.query_image_height, self.query_image_width = marker_image.shape[:2]

        # Initialize SIFT detector
        self.sift = cv2.SIFT()

        # Initialize FLANN matcher
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)

        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

        # Find features in marker image
        self.kp1, self.des1 = self.sift.detectAndCompute(marker_image, None)

    def find_marker_in_image(self, image):
        """
        Find marker in image.

        :param image: Image
        :return: Marker in form (contour, [centerX, centerY, width, height, rotation])
        """

        # Find features in image
        kp2, des2 = self.sift.detectAndCompute(image, None)

        if len(self.kp1) < 2 or len(kp2) < 2:
            return None, None

        # Find matches
        matches = self.flann.knnMatch(self.des1, des2, k=2)

        # Sort out bad matches
        good_matches = []
        for m, n in matches:
            if m.distance < 0.65 * n.distance:
                good_matches.append(m)

        # Check number of matches
        if len(good_matches) < self.min_matches:
            return None, None

        # Find homography between matches
        src_pts = np.float32([self.kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([     kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # Transform points to board area
        pts = np.float32([[0, 0], [0, self.query_image_height - 1], [self.query_image_width - 1, self.query_image_height - 1], [self.query_image_width - 1, 0]]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts, M)

        # Return resulting points
        return self.contour_to_marker_result(image, np.int32(dst))

    def find_marker_in_thresholded_image(self, image):
        return self.find_marker_in_image(image)

    def find_markers_in_image(self, image):
        """
        Find all markers in image.

        :param image: Image
        :return: List of markers each in form (contour, [centerX, centerY, width, height, rotation])
        """

        # TODO! Extract all markers!
        contour, box = self.find_marker_in_image(image)
        return [(contour, box)] if contour is not None else []

    def find_markers_in_thresholded_image(self, image):
        """
        Find all markers in image which has already been thresholded.

        :param image: Thresholded image
        :return: List of markers each in form (contour, [centerX, centerY, width, height, rotation])
        """
        return self.find_markers_in_image(image)
