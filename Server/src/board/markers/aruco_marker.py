from threading import RLock

import cv2
from board.markers.marker import Marker
from board.board_descriptor import BoardDescriptor
from util import aruco_util


class ArUcoMarker(Marker):
    def __init__(self, marker_id, aruco_marker_id, marker_size, dictionary_size=100):
        """
        :param marker_id: Marker ID
        :param aruco_marker_id: ArUco marker ID
        :param marker_size: Marker size. Can be any of 4, 5, 6 and 7.
        :param dictionary_size: Maximum number of markers in dictionary. Can be any of 100, 250, 1000.
        """
        super(ArUcoMarker, self).__init__(marker_id)

        self.aruco_marker_id = aruco_marker_id
        self.marker_size = marker_size
        self.dictionary_size = dictionary_size
        self.lock = RLock()

        # Initialize dictionary
        self.dictionary = cv2.aruco.getPredefinedDictionary(aruco_util.dictionary_from_parameters(self.marker_size, self.dictionary_size))

    def preferred_input_image_resolution(self):
        return BoardDescriptor.SnapshotSize.LARGE

    def find_marker_in_image(self, image):

        # Detect markers
        with self.lock:
            res = cv2.aruco.detectMarkers(image, self.dictionary)

        # Extract ArUco marker with correct ID
        if len(res[0]) > 0:
            for i1 in range(0, len(res[0])):
                for i2 in range(0, len(res[0][i1])):
                    if res[1][i1][i2] == self.aruco_marker_id:
                        return aruco_util.aruco_result_to_marker_result(res, i1, i2, image)

        return None

    def find_marker_in_thresholded_image(self, image):
        return self.find_marker_in_image(image)

    def find_markers_in_image(self, image):

        # Detect markers
        with self.lock:
            res = cv2.aruco.detectMarkers(image, self.dictionary)

        # Nothing found
        if len(res[0]) == 0:
            return []

        # Extract ArUco markers with correct ID
        markers = []
        for i1 in range(0, len(res[0])):
            for i2 in range(0, len(res[0][i1])):
                if res[1][i1][i2] == self.aruco_marker_id:
                    markers.append(aruco_util.aruco_result_to_marker_result(res, i1, i2, image))

        return markers

    def find_markers_in_thresholded_image(self, image):
        """
        Find all markers in image which has already been thresholded.

        :param image: Thresholded image
        :return: List of markers each in form {"markerId", "x", "y", "width", "height", "angle", "contour"}
        """
        return self.find_markers_in_image(image)
