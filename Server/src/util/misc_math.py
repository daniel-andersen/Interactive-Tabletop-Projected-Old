import math


def angle(pt1, pt2, pt0):
    dx1 = float(pt1[0] - pt0[0])
    dy1 = float(pt1[1] - pt0[1])
    dx2 = float(pt2[0] - pt0[0])
    dy2 = float(pt2[1] - pt0[1])

    return (dx1 * dx2 + dy1 * dy2) / math.sqrt((dx1 * dx1 + dy1 * dy1) * (dx2 * dx2 + dy2 * dy2) + 1e-10)


def max_cosine_from_contour(contour):
    max_cosine = 0.0

    for i in range(2, len(contour) + 2):
        cosine = abs(angle(contour[i % len(contour)][0],
                           contour[(i - 2) % len(contour)][0],
                           contour[(i - 1) % len(contour)][0]))
        max_cosine = max(cosine, max_cosine)

    return max_cosine


def line_length(p1, p2):
    return math.sqrt(((p1[0] - p2[0]) * (p1[0] - p2[0])) + ((p1[1] - p2[1]) * (p1[1] - p2[1])))
