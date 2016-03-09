from util import enum
from board.board_descriptor import BoardDescriptor
from board import transform
import cv2
import math
import numpy as np


class BoardRecognizer(object):
    """
    Class capable of recognizing a game board.
    """
    ThresholdModes = enum.Enum('OTSU', 'AUTO', 'NORMAL', 'BRIGHT_ROOM', 'DARK_ROOM')

    # Constants
    min_marker_area = 0
    max_marker_area = 0

    min_line_length = 0
    min_line_length_squared = 0

    def __init__(self):
        pass

    def find_board(self, image, corner_marker=BoardDescriptor.BoardCornerMarker.DEFAULT):
        """
        Finds a board, if any, in the source image and populates the board descriptor.
        :param image: Source image from which to recognize board
        :param corner_marker: Corner marker
        :return Board descriptor
        """
        source_image = self.prepare_image(image)

        self.prepare_constants_from_image(source_image)

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
            corners = self.find_corners(contours, hierarchy, corner_marker, image)
            if corners is not None:
                transformed_image = transform.transform_image(image, corners)
                print(corners)
                return BoardDescriptor.Snapshot(transformed_image, corners)

        return None

    def prepare_constants_from_image(self, image):
        width, height = image.shape[:2]

        self.min_marker_area = (width * 0.01) * (height * 0.01)
        self.max_marker_area = (width * 0.05) * (height * 0.05)

        self.min_line_length = min(width, height) * 0.1
        self.min_line_length_squared = self.min_line_length * self.min_line_length

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
            if self.are_marker_conditions_satisfied_for_contour(contours[i], corner_marker):
                child_index = hierarchy[0][i][2]
                parent_index = hierarchy[0][i][3]
                if child_index == -1 and parent_index != -1:
                    if self.are_marker_conditions_satisfied_for_contour(contours[parent_index], corner_marker):
                        valid_contour_indexes.append(i)

        ###
        #print("Valid contours: %i" % len(valid_contour_indexes))
        ##cts = [approxed_contours[i] for i in valid_contour_indexes]
        #cts = approxed_contours
        #image2 = image.copy()
        #cv2.drawContours(image2, cts, -1, (255,0,0), 2)
        #cv2.imshow('Contours', image2)
        #cv2.waitKey(0)
        ###

        # Find best contours
        best_contours = []

        for i in valid_contour_indexes:
            score = self.score_for_contour(approxed_contours[i], corner_marker)
            best_contours.append((i, score))
            best_contours = sorted(best_contours, key=lambda c: c[1])
            best_contours = best_contours[:min(4, len(best_contours))]

        if len(best_contours) != 4:
            return None

        # Extract all points
        all_points = []
        for (index, _) in best_contours:
            for p in approxed_contours[index]:
                all_points.append(p[0])

        # Return corner points
        return transform.order_corners(all_points)

    def score_for_contour(self, contour, corner_marker):
        marker_contour = self.marker_contour_for_marker(corner_marker)
        return cv2.matchShapes(contour, marker_contour, 1, 0.0)

    def are_marker_conditions_satisfied_for_contour(self, contour, corner_marker):
        # Check area
        area = cv2.contourArea(contour, False)
        if area < self.min_marker_area or area > self.max_marker_area:
            return False

        # Check convexity
        if cv2.isContourConvex(contour):
            return False

        # Check angles
        for i in range(2, len(contour) + 2):
            cosine = abs(self.angle(contour[i % len(contour)][0],
                                    contour[(i - 2) % len(contour)][0],
                                    contour[(i - 1) % len(contour)][0]))
            if abs(0.7 - cosine) > 0.05 and abs(cosine) > 0.05:
                return False

        # Check score
        return self.score_for_contour(contour, corner_marker) < 0.3

    """
    def are_default_marker_conditions_satisfied_for_contour(self, contour, corner_marker):
        marker_contour = self.marker_contour_for_marker(corner_marker)
        score = cv2.matchShapes(contour, marker_contour, 1, 0.0)
        return score < 0.1

        # Check number of points
        #print("%i" % len(contour))
        if len(contour) != 8:
            return False

        # Check area
        #print("1")
        area = cv2.contourArea(contour, False)
        if area < self.min_marker_area or area > self.max_marker_area:
            return False

        # Check aspect ratio
        _, _, width, height = cv2.boundingRect(contour)
        aspect_ratio = float(min(width, height)) / float(max(width, height))
        #print("2 - %f" % aspect_ratio)
        if aspect_ratio < 0.9:
            return False

        # Check convexity
        #print("3")
        if cv2.isContourConvex(contour):
            return False

        # Check angles
        #max_cosine = self.max_cosine_from_contour(contour)
        #print("-----> %f" % max_cosine)

        #print("4")
        return True
        """

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
            return 0.02
        else:
            return 0.02

    def marker_contour_for_marker(self, corner_marker):
        if corner_marker == BoardDescriptor.BoardCornerMarker.DEFAULT:
            #return np.int32([[0, 0], [0, 63], [63, 63], [63, 40], [40, 40], [40, 23], [23, 23], [24, 0]]).reshape(-1, 1, 2)
            return np.int32([[6, 6], [6, 18], [29, 18], [29, 34], [45, 34], [45, 57], [57, 57], [57, 6]]).reshape(-1, 1, 2)
        else:
            return None

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
        dx1 = pt1[0] - pt0[0] + 0.0
        dy1 = pt1[1] - pt0[1] + 0.0
        dx2 = pt2[0] - pt0[0] + 0.0
        dy2 = pt2[1] - pt0[1] + 0.0

        return (dx1*dx2 + dy1*dy2) / math.sqrt((dx1*dx1 + dy1*dy1) * (dx2*dx2 + dy2*dy2) + 1e-10)
