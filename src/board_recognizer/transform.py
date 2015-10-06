import numpy as np
import cv2


def order_corners(corners):
    """
    Orders the four corner points from top/left, top/right, bottom/right, bottom/left.
    :param pts: Corner points
    :return: Ordered points
    """
    print(corners)
    sum = (corners[0][0][0] + corners[0][0][1],
           corners[1][0][0] + corners[1][0][1],
           corners[2][0][0] + corners[2][0][1],
           corners[3][0][0] + corners[3][0][1])

    diff = (corners[0][0][0] - corners[0][0][1],
            corners[1][0][0] - corners[1][0][1],
            corners[2][0][0] - corners[2][0][1],
            corners[3][0][0] - corners[3][0][1])

    topLeft = [sum[0], corners[0][0]]
    topRight = [diff[1], corners[1][0]]
    bottomRight = [sum[2], corners[2][0]]
    bottomLeft = [diff[3], corners[3][0]]

    for i in range(0, 4):
        if sum[i] < topLeft[0]:
            topLeft[0] = sum[i]
            topLeft[1] = corners[i][0]
        if diff[i] < topRight[0]:
            topRight[0] = diff[i]
            topRight[1] = corners[i][0]
        if sum[i] > bottomRight[0]:
            bottomRight[0] = sum[i]
            bottomRight[1] = corners[i][0]
        if diff[i] > bottomLeft[0]:
            bottomLeft[0] = diff[i]
            bottomLeft[1] = corners[i][0]

    return [topLeft[1], topRight[1], bottomRight[1], bottomLeft[1]]


def transform_image(image, corners):
    points = order_corners(corners)
    print(points)
    return None
