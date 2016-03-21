from util import enum
from board.board_descriptor import BoardDescriptor
from board import transform
import cv2
import math
import itertools
import numpy as np


class BoardRecognizer(object):
    """
    Class capable of recognizing a game board.
    """
    ThresholdModes = enum.Enum('OTSU', 'AUTO', 'NORMAL', 'BRIGHT_ROOM', 'DARK_ROOM')

    # Constants
    marker_area_min = 0
    marker_area_max = 0

    marker_arc_length_max = 0

    marker_score_max = 0.3

    board_area_min = 0

    board_aspect_ratio = 0.0
    aspect_ratio_deviation_max = 0.25

    cosinus_max_deviation = math.cos(70.0 * math.pi / 180.0)

    marker_contour_cache = {}

    def __init__(self):
        pass

    def find_board(self, image, board_descriptor):
        """
        Finds a board, if any, in the source image and populates the board descriptor.
        :param image: Source image from which to recognize board
        :param board_descriptor: Board descriptor
        :return Board descriptor
        """
        source_image = self.prepare_image(image)

        self.prepare_constants_from_image(source_image, board_descriptor)

        # Find markers
        for (threshold_mode, _) in self.ThresholdModes.tuples():

            # Find threshold levels
            thresholded_image = self.threshold_image(source_image, threshold_mode)

            # Dilate image
            #dilated_image = cv2.dilate(thresholded_image, (3, 3))
            dilated_image = thresholded_image.copy()

            # Find contours
            contours, hierarchy =\
                cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) == 0:
                continue

            # Find corners
            corners = self.find_corners(contours, hierarchy, board_descriptor.corner_marker, image)
            if corners is not None:
                transformed_image = transform.transform_image(image, corners)
                return BoardDescriptor.Snapshot(transformed_image, corners)

        return None

    def prepare_constants_from_image(self, image, board_descriptor):
        image_width, image_height = image.shape[:2]
        board_width, board_height = board_descriptor.board_size

        self.marker_area_min = (image_width * 0.01) * (image_height * 0.01)
        self.marker_area_max = (image_width * 0.05) * (image_height * 0.05)
        self.marker_arc_length_max = (image_width * 0.05 * 2.0) + (image_height * 0.05 * 2.0)

        self.marker_image_margin_max = [image_width * 0.25, image_height * 0.25]

        self.board_area_min = (image_width * 0.65) * (image_height * 0.65)

        self.board_aspect_ratio = float(max(board_width, board_height)) / float(min(board_width, board_height))

    def prepare_image(self, image):
        grayscaled_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
        blurred_image = cv2.medianBlur(grayscaled_image, 3)
        return blurred_image

    def find_corners(self, contours, hierarchy, corner_marker, image):

        # Calculate approx multiplier
        approx_multiplier = self.approx_multiplier_for_marker(corner_marker)

        # Simplify contours
        approxed_contours = []
        for contour in contours:
            approxed_contours.append(cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * approx_multiplier, True))

        # Find valid contours
        valid_contour_indexes = []

        for i in range(0, len(approxed_contours)):
            #image2 = image.copy()
            #cv2.drawContours(image2, [approxed_contours[i]], -1, (255, 0, 255), 1)
            #cv2.imshow('Contours', image2)
            #cv2.waitKey(0)
            if self.are_marker_conditions_satisfied_for_contour(contours[i], approxed_contours[i], corner_marker):
                valid_contour_indexes.append(i)

        ###
        cts = [approxed_contours[i] for i in valid_contour_indexes]
        #cts = approxed_contours
        #image2 = image.copy()
        #cv2.drawContours(image2, cts, -1, (255, 0, 255), 1)
        #cv2.imshow('Contours', image2)
        #cv2.waitKey(0)
        ###

        # Find best contours
        best_contour_indices = []

        for i in valid_contour_indexes:
            score = self.score_for_contour(contours[i], corner_marker)
            best_contour_indices.append((i, score))

        if len(best_contour_indices) < 4:
            return None

        # Find best combination of corners
        best_corners = []

        for corner_indices in itertools.combinations(range(0, len(best_contour_indices)), 4):

            # Extract all points
            all_points = []
            for best_contour_index in corner_indices:
                index = best_contour_indices[best_contour_index][0]
                for p in approxed_contours[index]:
                    all_points.append(p[0])

            # Find corners
            corners = transform.order_corners(all_points)
            contour = np.int32(corners).reshape(-1, 1, 2)

            # Check if valid
            if not self.is_corner_combination_valid(contour):
                continue

            ###
            #image2 = image.copy()
            #cv2.drawContours(image2, [contour], -1, (255, 0, 255), 2)
            #cv2.imshow('Contours', image2)
            #cv2.waitKey(0)
            ###

            # Calculate score
            score = self.score_for_corners(contour)
            best_corners.append((corners, score))

        if len(best_corners) == 0:
            return None

        # Return best combination
        best_corners = sorted(best_corners, key=lambda c: c[1], reverse=True)

        ###
        #image2 = image.copy()
        #cv2.drawContours(image2, [np.int32(best_corners[0][0]).reshape(-1, 1, 2)], -1, (0, 255, 0), 2)
        #cv2.imshow('Contours', image2)
        #cv2.waitKey(0)
        ###
        return best_corners[0][0]

    def is_corner_combination_valid(self, contour):
        if abs(cv2.contourArea(contour)) < self.board_area_min:
            return False

        if not self.has_correct_aspect_ratio(contour):
            return False

        if self.max_cosine_from_contour(contour) > self.cosinus_max_deviation:
            return False

        return True

    def has_correct_aspect_ratio(self, contour):
        (_, _), (width, height), _ = cv2.minAreaRect(contour)
        aspect_ratio = max(float(width) / float(height), float(height) / float(width))
        return abs(aspect_ratio - self.board_aspect_ratio) <= self.aspect_ratio_deviation_max

    def score_for_corners(self, contour):
        return cv2.contourArea(contour, False)

    def score_for_contour(self, contour, corner_marker):
        marker_contour = self.marker_contour_for_marker(corner_marker)
        return cv2.matchShapes(contour, marker_contour, 1, 0.0)

    def are_marker_conditions_satisfied_for_contour(self, contour, approxed_contour, corner_marker):
        # Check number of lines
        if len(approxed_contour) != 3:
            return False

        # Check area
        area = cv2.contourArea(approxed_contour, False)
        if area < self.marker_area_min or area > self.marker_area_max:
            return False

        # Check arc length
        length = cv2.arcLength(approxed_contour, True)
        if length > self.marker_arc_length_max:
            return False

        # Check angles - must have two 45 degrees and one 90 degrees
        angle_count_45 = 0
        angle_count_90 = 0

        for i in range(2, len(approxed_contour) + 2):
            cosine = abs(self.angle(approxed_contour[i % len(approxed_contour)][0],
                                    approxed_contour[(i - 2) % len(approxed_contour)][0],
                                    approxed_contour[(i - 1) % len(approxed_contour)][0]))
            if abs(math.cos(45 * math.pi / 180.0) - cosine) <= 0.2:
                angle_count_45 += 1
            if abs(math.cos(90 * math.pi / 180.0) - cosine) <= 0.3:
                angle_count_90 += 1

        if angle_count_45 != 2 or angle_count_90 != 1:
            return False

        # Match shape
        if self.score_for_contour(contour, corner_marker) > self.marker_score_max:
            return False

        return True

    def threshold_image(self, image, mode):
        if mode == self.ThresholdModes.OTSU:
            return self.otsu_image(image)
        else:
            return self.canny_image(image, mode)

    def otsu_image(self, image):
        image = cv2.blur(image, (2, 2))
        ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return image

    def canny_image(self, image, mode):
        if mode == self.ThresholdModes.AUTO:
            threshold_min, threshold_max = self.automatic_thresholding_for_image(image)
        elif mode == self.ThresholdModes.BRIGHT_ROOM:
            threshold_min, threshold_max = 40, 70
        elif mode == self.ThresholdModes.DARK_ROOM:
            threshold_min, threshold_max = 100, 300
        else:
            threshold_min, threshold_max = 60, 120

        return cv2.Canny(image, threshold_min, threshold_max)

    def automatic_thresholding_for_image(self, image):
        # Calculate histogram
        histogram = self.calculate_histogram_from_image(image)

        # Calculate mean
        min_index = 255
        max_index = 0
        for i in range(0, 256):
            value = histogram.item(i)
            if value != 0:
                min_index = min(min_index, i)
                max_index = max(max_index, i)

        # Mean value
        mean = (min_index + max_index) / 2.0

        # Threshold values
        return mean * 2.0 / 3.0, mean * 4.0 / 3.0

    def approx_multiplier_for_marker(self, corner_marker):
        if corner_marker == BoardDescriptor.BoardCornerMarker.DEFAULT:
            return 0.05
        else:
            return 0.02

    def marker_contour_for_marker(self, corner_marker):
        # Check cache
        if corner_marker in self.marker_contour_cache:
            return self.marker_contour_cache[corner_marker]

        # Read corner marker image
        filename = "default"
        image = cv2.imread("assets/corner_markers/" + filename + ".png", cv2.IMREAD_GRAYSCALE)

        # Find contour
        contours = cv2.findContours(image, 2, 1)
        contour = np.int32(contours[0][0]).reshape(-1, 1, 2)

        # Insert into cache
        self.marker_contour_cache[corner_marker] = contour

        return contour

    def calculate_histogram_from_image(self, image):
        return cv2.calcHist([image], [0], None, [256], [0, 256])

    def max_cosine_from_contour(self, contour):
        max_cosine = 0.0

        for i in range(2, len(contour) + 2):
            cosine = abs(self.angle(contour[i % len(contour)][0],
                                    contour[(i - 2) % len(contour)][0],
                                    contour[(i - 1) % len(contour)][0]))
            max_cosine = max(cosine, max_cosine)

        return max_cosine

    def angle(self, pt1, pt2, pt0):
        dx1 = float(pt1[0] - pt0[0])
        dy1 = float(pt1[1] - pt0[1])
        dx2 = float(pt2[0] - pt0[0])
        dy2 = float(pt2[1] - pt0[1])

        return (dx1*dx2 + dy1*dy2) / math.sqrt((dx1*dx1 + dy1*dy1) * (dx2*dx2 + dy2*dy2) + 1e-10)
