import numpy as np
import cv2
import math


def order_corners(corners):
    """
    Orders the four corner points from top/left, top/right, bottom/right, bottom/left.
    :param pts: Corner points
    :return: Ordered points, clockwise from top/left corner
    """
    sum = np.array([corners[i][0][0] + corners[i][0][1] for i in range(0, 4)])
    diff = np.array([corners[i][0][0] - corners[i][0][1] for i in range(0, 4)])

    topLeft = corners[np.argmin(sum)][0]       # Top/left corner has smallest sum
    topRight = corners[np.argmax(diff)][0]     # Top/right corner has largest difference
    bottomRight = corners[np.argmax(sum)][0]   # Bottom/right corner has largest sum
    bottomLeft = corners[np.argmin(diff)][0]   # Bottom/left corner has smallest difference

    return np.array([topLeft, topRight, bottomRight, bottomLeft], np.float32)


def warp_corners(corners):
    """
    Warps the corner points to a rectangle.
    :param corners: Source points
    :return: Points warped to a rectangle, clockwise from top/left corner
    """
    (topLeft, topRight, bottomRight, bottomLeft) = corners

    # Find width
    width_upper = math.sqrt(((topLeft[0] - topRight[0]) ** 2) + ((topLeft[1] - topRight[1]) ** 2))
    width_lower = math.sqrt(((bottomLeft[0] - bottomRight[0]) ** 2) + ((bottomLeft[1] - bottomRight[1]) ** 2))
    width = int(max(width_upper, width_lower))

    # Find height
    height_left = math.sqrt(((topLeft[0] - bottomLeft[0]) ** 2) + ((topLeft[1] - bottomLeft[1]) ** 2))
    height_right = math.sqrt(((topRight[0] - bottomRight[0]) ** 2) + ((topRight[1] - bottomRight[1]) ** 2))
    height = int(max(height_left, height_right))

    return np.array([[0, 0],
                     [width, 0],
                     [width, height],
                     [0, height]], np.float32)


def transform_image(image, corners):
    """Perspective transform source image into rectangle.
    :param image: Source image to transform
    :param corners: Corners in source image
    :return: Transformed image
    """
    source_points = order_corners(corners)
    dest_points = warp_corners(source_points)

    perspective_transform = cv2.getPerspectiveTransform(source_points, dest_points)

    return cv2.warpPerspective(image, perspective_transform, (dest_points[2][0], dest_points[2][1]))
