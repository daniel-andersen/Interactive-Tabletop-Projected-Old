import math


def angle(pt0, pt1, pt2):
    dx1 = float(pt0[0]) - float(pt1[0])
    dy1 = float(pt0[1]) - float(pt1[1])
    dx2 = float(pt2[0]) - float(pt1[0])
    dy2 = float(pt2[1]) - float(pt1[1])

    return (dx1 * dx2 + dy1 * dy2) / math.sqrt((dx1 * dx1 + dy1 * dy1) * (dx2 * dx2 + dy2 * dy2) + 1e-10)


def max_cosine_from_contour(contour):
    max_cosine = 0.0

    for i in range(2, len(contour) + 2):
        cosine = abs(angle(contour[i % len(contour)][0],
                           contour[(i - 1) % len(contour)][0],
                           contour[(i - 2) % len(contour)][0]))
        max_cosine = max(cosine, max_cosine)

    return max_cosine


def angle_difference(angle1, angle2):
    return (((angle1 - angle2) + math.pi) % (math.pi * 2.0)) - math.pi


def line_length(p1, p2):
    return math.sqrt(((p1[0] - p2[0]) * (p1[0] - p2[0])) + ((p1[1] - p2[1]) * (p1[1] - p2[1])))


def angle_from_homography_matrix(M):
    return math.atan2(M[1][0], M[0][0])
