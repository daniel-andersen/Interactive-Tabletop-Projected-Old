import util
import numpy as np
import cv2
import math

class BoardDescriptor:
    """Represents a description of a board.

    board_image -- The recognized and transformed image
    board_corners -- The four points in the source image representing the corners of the recognized board
    """
    def __init__(self, board_image, board_corners):
        self.board_image = board_image
        self.board_corners = board_corners

    def is_recognized(self):
        """Indicates whether the board has been recognized in the source image or not.
        :return: True, if the board has been recognized in the source image, else false
        """
        return True if self.board_image is not None else False


class BoardRecognizer(object):
    """A class capable of recognizing a game board.
    """
    ThresholdModes = util.Enum('OTSU', 'AUTO', 'NORMAL', 'BRIGHT_ROOM', 'DARK_ROOM')
    # ThresholdModes = util.Enum('OTSU')

    min_contour_area = 0
    max_contour_area = 0

    min_line_length = 0
    min_line_length_squared = 0

    dilated_images = {}
    contours = {}
    output_src = None

    def __init__(self):
        pass

    def recognize_paper(self, image):

        self.output_src = image.copy()

        # Prepare constants
        self.prepare_constants_from_image(image)

        # Grayscale
        grayscaled_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grayscaled_image = cv2.medianBlur(grayscaled_image, 3)

        # Find non-obstructed bounds
        return self.find_bounds_from_image(grayscaled_image)

    def get_output_image(self, index):
        return self.output_src
        # return self.dilated_images[index] if len(self.dilated_images) > index else None

    def get_output_contour(self, index):
        return self.contours[index] if len(self.contours) > index else None

    def find_bounds_from_image(self, image):

        self.dilated_images = {}
        self.contours = {}

        # Find non-obstructed bounds
        for (threshold_mode, str) in self.ThresholdModes.tuples():

            # Find threshold levels
            thresholded_image = self.threshold_image(image, threshold_mode)

            # Dilate image
            dilated_image = cv2.dilate(thresholded_image, (3, 3))

            self.dilated_images[threshold_mode] = dilated_image

            # Find contours
            out_image, self.contours[threshold_mode], hierarchy =\
                cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if len(self.contours[threshold_mode]) == 0:
                continue

            # Find non-obstructed bounds
            corners = self.find_non_obstructed_bounds_from_contours(self.contours[threshold_mode])
            if corners is not None:
                return corners

        # Find obstructed bounds
        for (threshold_mode, str) in self.ThresholdModes.tuples():

            # Find obstructed bounds
            corners = self.find_obstructed_bounds_from_contours(self.contours[threshold_mode])
            if corners is not None:
                return corners

        return None

    def find_non_obstructed_bounds_from_contours(self, contours):

        # Simplify contours
        approxed_contours = []
        for contour in contours:
            approxed_contours.append(cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * 0.02, True))

        # Find valid contours
        valid_contour_indexes = []

        for i in range(0, len(approxed_contours)):
            if self.are_contour_conditions_satisfied_for_contour(approxed_contours[i]):
                valid_contour_indexes.append(i)

        # Find best contour
        best_score = None
        best_index = None

        for i in valid_contour_indexes:
            score = self.score_for_contour(approxed_contours[i])
            if best_score is None or score > best_score:
                best_score = score
                best_index = i

        return approxed_contours[best_index] if best_index is not None else None

    def find_obstructed_bounds_from_contours(self, contours):

        # Simplify contours
        approxed_contours = []
        for contour in contours:
            approxed_contours.append(cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * 0.002, True))

        # Find all valid lines
        valid_lines = []

        for contour in approxed_contours:
            length = len(contour)
            for i in range(0, length):
                p1 = contour[(i + 0) % length][0]
                p2 = contour[(i + 1) % length][0]

                delta_x = p1[0] - p2[0]
                delta_y = p1[1] - p2[1]
                sqr_line_length = (delta_x * delta_x) + (delta_y * delta_y)

                if sqr_line_length > self.min_line_length_squared:
                    valid_lines.append((p1, p2))
                    cv2.line(self.output_src, (p1[0], p1[1]), (p2[0], p2[1]), color=(0, 0, 255), thickness=5)

        return None

    def score_for_contour(self, contour):
        return cv2.contourArea(contour, False) # * (1.0 - self.max_cosine_from_contour(contour))

    def are_contour_conditions_satisfied_for_contour(self, contour):
        if len(contour) != 4:
            return False

        area = cv2.contourArea(contour, False)
        if area < self.min_contour_area or area > self.max_contour_area:
            return False

        if not cv2.isContourConvex(contour):
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

    def calculate_histogram_from_image(self, image):
        return cv2.calcHist([image], [0], None, [256], [0, 256])

    def prepare_constants_from_image(self, image):
        width, height = image.shape[:2]

        self.min_contour_area = (width * 0.1) * (height * 0.1)
        self.max_contour_area = (width * 0.95) * (height * 0.95)

        self.min_line_length = min(width, height) * 0.1
        self.min_line_length_squared = self.min_line_length * self.min_line_length

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
