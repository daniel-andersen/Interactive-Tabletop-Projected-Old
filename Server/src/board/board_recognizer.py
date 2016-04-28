import cv2
import numpy as np
import math
from util import enum
from util import misc_math
from board.board_descriptor import BoardDescriptor
from board import transform
from board import histogram_util

class BoardRecognizedState(object):
    def __init__(self):
        self.marker_rects = [None, None, None, None]
        self.threshold_mode = BoardRecognizer.ThresholdModes.OTSU


class BoardRecognizer(object):
    """
    Class capable of recognizing a game board.
    """
    ThresholdModes = enum.Enum('OTSU', 'AUTO', 'ADAPTIVE')

    # Constants
    marker_search_width = 0
    marker_search_height = 0

    board_area_min = 0

    board_aspect_ratio = 0.0
    board_aspect_ratio_deviation_max = 0.25

    board_cosinus_max_deviation = math.cos(75.0 * math.pi / 180.0)

    image_width = 0
    image_height = 0

    def __init__(self):
        self.state = BoardRecognizedState()

    def find_board(self, image, board_descriptor):
        """
        Finds a board, if any, in the source image and populates the board descriptor.
        :param image: Source image from which to recognize board
        :param board_descriptor: Board descriptor
        :return Board descriptor
        """

        source_image = self.prepare_image(image)

        self.prepare_constants_from_image(source_image, board_descriptor)

        # Search for board in different threshold levels
        for (threshold_mode, _) in self.ThresholdModes.tuples():

            # Find markers in all four part of image
            marker_contours = [None, None, None, None]
            self.state.marker_rects[2], marker_contours[2] = self.find_marker(source_image, 0, 1, self.state.marker_rects[2], threshold_mode, board_descriptor.corner_marker)
            self.state.marker_rects[0], marker_contours[0] = self.find_marker(source_image, 0, 0, self.state.marker_rects[0], threshold_mode, board_descriptor.corner_marker)
            self.state.marker_rects[1], marker_contours[1] = self.find_marker(source_image, 1, 0, self.state.marker_rects[1], threshold_mode, board_descriptor.corner_marker)
            self.state.marker_rects[3], marker_contours[3] = self.find_marker(source_image, 1, 1, self.state.marker_rects[3], threshold_mode, board_descriptor.corner_marker)

            # Check if all markers are found
            if marker_contours[0] is None or marker_contours[1] is None or marker_contours[2] is None or marker_contours[3] is None:
                continue

            # Find corners
            corners = self.find_corners(marker_contours, image)
            if corners is not None:
                transformed_image = transform.transform_image(image, corners)
                return BoardDescriptor.Snapshot(transformed_image, corners)

        return None

    def prepare_constants_from_image(self, image, board_descriptor):
        self.image_height, self.image_width = image.shape[:2]
        board_width, board_height = board_descriptor.board_size

        self.board_area_min = (self.image_width * 0.65) * (self.image_height * 0.65)

        self.board_aspect_ratio = float(max(board_width, board_height)) / float(min(board_width, board_height))

        self.marker_search_width = int(self.image_width * 0.1)
        self.marker_search_height = int(self.image_height * 0.1)

    def prepare_image(self, image):
        grayscaled_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
        blurred_image = grayscaled_image #cv2.medianBlur(grayscaled_image, 1)
        return blurred_image

    def find_marker(self, image, part_x, part_y, current_marker_rect, threshold_mode, corner_marker):

        # Calculate part rect
        part_width = int(self.image_width / 2)
        part_height = int(self.image_height / 2)

        part_offset_x = part_x * part_width
        part_offset_y = part_y * part_height

        # Find marker in previous marker rect
        #if part_x == 0 and part_y == 0:
            #current_marker_rect = [72 - self.marker_search_width / 2, 132 - self.marker_search_height, 72 + self.marker_search_width, 132 + self.marker_search_height]
        #if part_x == 1 and part_y == 0:
            #current_marker_rect = [567 - self.marker_search_width / 2, 153 - self.marker_search_height, 567 + self.marker_search_width, 153 + self.marker_search_height]
        #if part_x == 0 and part_y == 1:
            #current_marker_rect = [54 - self.marker_search_width / 2, 450 - self.marker_search_height, 54 + self.marker_search_width, 450 + self.marker_search_height]
        #if part_x == 1 and part_y == 1:
            #current_marker_rect = [567 - self.marker_search_width / 2, 450 - self.marker_search_height, 567 + self.marker_search_width, 450 + self.marker_search_height]

        if current_marker_rect is not None:
            #print("Searching in current rect")
            contour = self.find_marker_in_rect(image, current_marker_rect, threshold_mode, corner_marker)
            if contour is not None:
                #print("Marker same as previous")
                return self.centered_search_rect(contour), contour

        # Go through whole image
        for y in range(part_offset_y, part_offset_y + part_height, self.marker_search_height / 2):
            for x in range(part_offset_x, part_offset_x + part_width, self.marker_search_width / 2):

                # Check bounds
                bx = min(x, part_offset_x + part_width - self.marker_search_width)
                by = min(y, part_offset_y + part_height - self.marker_search_height)

                # Calculate search rect
                search_rect = [bx, by, bx + self.marker_search_width, by + self.marker_search_height]

                # Search for contour
                contour = self.find_marker_in_rect(image, search_rect, threshold_mode, corner_marker)
                if contour is not None:
                    return self.centered_search_rect(contour), contour

        # No marker found
        #print("NO MARKER FOUND")
        return None, None

    def centered_search_rect(self, contour):
        x, y, width, height = cv2.boundingRect(contour)

        # Calculate offset
        offset_x = max(0, min(self.image_width - self.marker_search_width, x + ( width - self.marker_search_width) / 2))
        offset_y = max(0, min(self.image_height - self.marker_search_height, y + (height - self.marker_search_height) / 2))

        return [offset_x, offset_y, offset_x + self.marker_search_width, offset_y + self.marker_search_height]

    def find_marker_in_rect(self, image, search_rect, threshold_mode, corner_marker):

        # Extract rect
        image = image[search_rect[1]:search_rect[3], search_rect[0]:search_rect[2]]

        # Threshold image
        thresholded_image = self.threshold_image(image, threshold_mode)

        # Find marker contour
        contour = corner_marker.find_marker_in_thresholded_image(thresholded_image)
        if contour is None:
            return None

        # Translate points to offset
        for i in range(0, len(contour)):
            contour[i][0][0] += search_rect[0]
            contour[i][0][1] += search_rect[1]

        return contour

    def find_corners(self, marker_contours, image):

        # Find corner points
        all_points = []
        for contour in marker_contours:
            for p in contour:
                all_points.append(p[0])

        corners = transform.order_corners(all_points)
        contour = np.int32(corners).reshape(-1, 1, 2)

        # Check if valid
        if not self.is_corner_combination_valid(contour):
            return None

        return [c[0] for c in contour]

    def is_corner_combination_valid(self, contour):
        if abs(cv2.contourArea(contour)) < self.board_area_min:
            return False

        if not self.has_correct_aspect_ratio(contour):
            return False

        if misc_math.max_cosine_from_contour(contour) > self.board_cosinus_max_deviation:
            return False

        return True

    def has_correct_aspect_ratio(self, contour):
        aspect_ratio = self.contour_aspect_ratio(contour)
        return abs(aspect_ratio - self.board_aspect_ratio) <= self.board_aspect_ratio_deviation_max

    def contour_aspect_ratio(self, contour):
        (_, _), (width, height), _ = cv2.minAreaRect(contour)
        return max(float(width) / float(height), float(height) / float(width))

    def score_for_corners(self, contour):
        l1 = misc_math.line_length(contour[0][0], contour[2][0])
        l2 = misc_math.line_length(contour[1][0], contour[3][0])
        return (1.0 / abs(l1 - l2)) * cv2.contourArea(contour, False)

    def threshold_image(self, image, mode):
        if mode == self.ThresholdModes.OTSU:
            return self.otsu_image(image)
        else:
            return self.adaptive_threshold_image(image, mode)

    def otsu_image(self, image):
        image = cv2.blur(image, (2, 2))
        ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return image

    def adaptive_threshold_image(self, image, mode):
        if mode == self.ThresholdModes.ADAPTIVE:
            return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        elif mode == self.ThresholdModes.AUTO:
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
        histogram = histogram_util.histogram_from_image(image, 256)

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
