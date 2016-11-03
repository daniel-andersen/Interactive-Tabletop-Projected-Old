import math
import cv2
import numpy as np
from board.markers.marker import Marker
from util import misc_math
from util import contour_util


def aruco_result_to_marker_result(aruco_result, index, subindex, image):
    """
    Converts an ArUco result to marker result.

    :param aruco_result: Result from ArUco
    :param index: Index
    :param subindex: Subindex (in ID list)
    :param image: Source image
    :return: Marker result
    """
    marker_id = aruco_result[1][index][subindex]
    box = aruco_result[0][index][subindex]
    contour = np.int32(box).reshape(-1, 1, 2)

    marker_result = Marker(int(marker_id)).contour_to_marker_result(image, contour)

    # Overwrite angle
    angle1 = contour_util.contour_angle(contour, contour[0][0])
    angle2 = contour_util.contour_angle(np.int32([[0, 0], [1, 0], [1, 1], [0, 1]]).reshape(-1, 1, 2), [0, 0])

    marker_result["angle"] = (angle1 - angle2) * 180.0 / math.pi

    return marker_result


def dictionary_from_parameters(marker_size, dictionary_size):
    """
    Converts class parameters to ArUco dictionary.

    :param marker_size: Marker size
    :param dictionary_size: Dictionary size
    :return: ArUco dictionary
    """
    if marker_size == 4:
        if dictionary_size == 100:
            return cv2.aruco.DICT_4X4_100
        elif dictionary_size == 250:
            return cv2.aruco.DICT_4X4_250
        elif dictionary_size == 1000:
            return cv2.aruco.DICT_4X4_1000
    elif marker_size == 5:
        if dictionary_size == 100:
            return cv2.aruco.DICT_5X5_100
        elif dictionary_size == 250:
            return cv2.aruco.DICT_5X5_250
        elif dictionary_size == 1000:
            return cv2.aruco.DICT_5X5_1000
    elif marker_size == 6:
        if dictionary_size == 100:
            return cv2.aruco.DICT_6X6_100
        elif dictionary_size == 250:
            return cv2.aruco.DICT_6X6_250
        elif dictionary_size == 1000:
            return cv2.aruco.DICT_6X6_1000
    elif marker_size == 7:
        if dictionary_size == 100:
            return cv2.aruco.DICT_7X7_100
        elif dictionary_size == 250:
            return cv2.aruco.DICT_7X7_250
        elif dictionary_size == 1000:
            return cv2.aruco.DICT_7X7_1000
    return cv2.aruco.DICT_6X6_100
