import math
import cv2
import numpy as np
from threading import RLock
from board.markers.marker import Marker
from board.board_descriptor import BoardDescriptor
from util import misc_math


class ImageMarker(Marker):
    def __init__(self, marker_id, marker_image, min_matches=8):
        """
        :param marker_id: Marker ID
        :param marker_image: Marker image
        :param min_matches: Minimum number of matches for marker to be detected
        """
        super(ImageMarker, self).__init__(marker_id)

        self.min_matches = min_matches

        self.lock = RLock()

        # Get size of query image
        self.query_image_height, self.query_image_width = marker_image.shape[:2]

        # Initialize SIFT detector
        self.sift = cv2.xfeatures2d.SIFT_create()

        # Initialize FLANN matcher
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)

        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

        # Find features in marker image
        self.kp1, self.des1 = self.sift.detectAndCompute(marker_image, None)

    def preferred_input_image_resolution(self):
        return BoardDescriptor.SnapshotSize.ORIGINAL

    def find_marker_in_image(self, image):

        #cv2.imwrite("area_{}.png".format(self.marker_id), image)

        # Find features in image
        with self.lock:
            kp2, des2 = self.sift.detectAndCompute(image, None)

        if len(self.kp1) < 2 or len(kp2) < 2:
            return None

        # Find matches
        with self.lock:
            matches = self.flann.knnMatch(self.des1, des2, k=2)

        # Sort out bad matches
        good_matches = []
        for m, n in matches:
            if m.distance < 0.666 * n.distance:
                good_matches.append(m)

        # Check number of matches
        if len(good_matches) < self.min_matches:
            return None

        # Find homography between matches
        src_pts = np.float32([self.kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([     kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # Transform points to board area
        pts = np.float32([[0, 0], [0, self.query_image_height - 1], [self.query_image_width - 1, self.query_image_height - 1], [self.query_image_width - 1, 0]]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts, M)

        # Convert into marker result
        marker_result = self.contour_to_marker_result(image, np.int32(dst))

        # Calculate correct angle
        marker_result["angle"] = misc_math.angle_from_homography_matrix(M) * 180.0 / math.pi

        # Return result
        return marker_result

    def find_marker_in_thresholded_image(self, image):
        return self.find_marker_in_image(image)

    def find_markers_in_image(self, image):

        # TODO! Extract all markers!
        result = self.find_marker_in_image(image)
        return [result] if result is not None else []

    def find_markers_in_thresholded_image(self, image):
        return self.find_markers_in_image(image)
