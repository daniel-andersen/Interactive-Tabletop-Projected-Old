import numpy as np
import cv2
import math


def order_corners(corners):
    """
    Orders the four corner points from top/left, top/right, bottom/right, bottom/left.
    :param corners: Corner points
    :return: Ordered points, clockwise from top/left corner
    """
    sum = np.array([corner[0] + corner[1] for corner in corners])
    diff = np.array([corner[0] - corner[1] for corner in corners])

    top_left = corners[np.argmin(sum)]       # Top/left corner has smallest sum
    top_right = corners[np.argmax(diff)]     # Top/right corner has largest difference
    bottom_right = corners[np.argmax(sum)]   # Bottom/right corner has largest sum
    bottom_left = corners[np.argmin(diff)]   # Bottom/left corner has smallest difference

    return [top_left, top_right, bottom_right, bottom_left]


def warp_corners(corners):
    """
    Warps the corner points to a rectangle.
    :param corners: Source points
    :return: Points warped to a rectangle, clockwise from top/left corner
    """
    (top_left, top_right, bottom_right, bottom_left) = corners

    # Find width
    width_upper = distance(top_left, top_right)
    width_lower = distance(bottom_left, bottom_right)
    width = int(max(width_upper, width_lower))

    # Find height
    height_left = distance(top_left, bottom_left)
    height_right = distance(top_right, bottom_right)
    height = int(max(height_left, height_right))

    return [[0, 0],
            [width, 0],
            [width, height],
            [0, height]]


def distance(p1, p2):
    """
    Calculates the distance between the two points.
    :param p1: First point
    :param p2: Second point
    :return: Distance between points
    """
    return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))


def transform_image(image, corners):
    """
    Perspective transform source image into rectangle.
    :param image: Source image to transform
    :param corners: Corners in source image
    :return: Transformed image
    """
    source_points = order_corners(corners)
    dest_points = warp_corners(source_points)

    perspective_transform = cv2.getPerspectiveTransform(np.array(source_points, np.float32),
                                                        np.array(dest_points, np.float32))

    return cv2.warpPerspective(image, perspective_transform, (dest_points[2][0], dest_points[2][1]))
