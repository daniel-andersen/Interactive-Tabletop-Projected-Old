from threading import RLock
import cv2
import numpy as np
import math
from util import enum
from util import misc_math
from board.board_descriptor import BoardSnapshot
from board.board_descriptor import BoardStatus
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
    ThresholdModes = enum.Enum('OTSU', 'AUTO', 'ADAPTIVE', 'BRIGHT_ROOM', 'DARK_ROOM')

    # Constants
    marker_search_width = 0
    marker_search_height = 0

    board_area_min = 0

    board_aspect_ratio = 0.0
    board_aspect_ratio_deviation_max = 0.25

    board_cosinus_max_deviation = math.cos(75.0 * math.pi / 180.0)

    image_width = 0
    image_height = 0

    lock = RLock()

    def __init__(self):
        self.state = BoardRecognizedState()

    def find_board(self, image, board_descriptor, force_detection=False):
        with self.lock:
            return self._find_board(image, board_descriptor, force_detection)

    def _find_board(self, image, board_descriptor, force_detection=False):
        """
        Finds a board, if any, in the source image and populates the board descriptor.

        :param image: Source image from which to recognize board
        :param board_descriptor: Board descriptor
        :param force_detection: Force detection of board
        :return Board descriptor
        """

        # Check if board is already detected
        if board_descriptor.is_recognized() and not force_detection:
            return BoardSnapshot(camera_image=image,
                                 board_image=transform.transform_image(image, board_descriptor.get_snapshot().board_corners),
                                 board_corners=board_descriptor.get_snapshot().board_corners)

        # Prepare image
        source_image = self.prepare_image(image)

        # Prepare search constants
        self.prepare_constants_from_image(source_image, board_descriptor)

        # Find markers in all four part of image
        parts = [[0, 0], [1, 0], [0, 1], [1, 1]]
        marker_contours = [None, None, None, None]

        # First try previous found rect, if any
        for (threshold_mode, _) in self.ThresholdModes.tuples():
            for i in range(0, len(parts)):

                # Already found this marker
                if marker_contours[i] is not None:
                    continue

                # Marker hasn't yet been foound
                if self.state.marker_rects[i] is None:
                    continue

                # Find marker
                marker_rect, marker_contours[i] = self.find_marker(source_image, parts[i][0], parts[i][1], self.state.marker_rects[i], threshold_mode, board_descriptor.corner_marker)

                if marker_rect is not None:
                    self.state.marker_rects[i] = marker_rect

        # Next try whole image
        for (threshold_mode, _) in self.ThresholdModes.tuples():
            for i in range(0, len(parts)):

                # Already found this marker
                if marker_contours[i] is not None:
                    continue

                # Find marker
                marker_rect, marker_contours[i] = self.find_marker(source_image, parts[i][0], parts[i][1], None, threshold_mode, board_descriptor.corner_marker)

                if marker_rect is not None:
                    self.state.marker_rects[i] = marker_rect

        # Check if all markers are found
        if marker_contours[0] is None or marker_contours[1] is None or marker_contours[2] is None or marker_contours[3] is None:
            return self.board_snapshot_with_missing_corners(image, marker_contours[0], marker_contours[1], marker_contours[2], marker_contours[3])

        # Find corners
        corners = self.find_corners(marker_contours, image)
        if corners is not None:
            return BoardSnapshot(camera_image=image,
                                 board_image=transform.transform_image(image, corners),
                                 board_corners=corners)

        return None

    def prepare_constants_from_image(self, image, board_descriptor):
        self.image_height, self.image_width = image.shape[:2]
        board_width, board_height = board_descriptor.board_size

        self.board_area_min = (self.image_width * 0.50) * (self.image_height * 0.50)

        self.board_aspect_ratio = float(max(board_width, board_height)) / float(min(board_width, board_height))

        self.marker_search_width = int(self.image_width * 0.1)
        self.marker_search_height = int(self.image_height * 0.1)

    def prepare_image(self, image):
        grayscaled_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return grayscaled_image

    def find_marker(self, image, part_x, part_y, current_marker_rect, threshold_mode, corner_marker):

        # Calculate part rect
        part_width = int(self.image_width / 2)
        part_height = int(self.image_height / 2)

        part_offset_x = part_x * part_width
        part_offset_y = part_y * part_height

        # Find marker in previous marker rect
        if current_marker_rect is not None:
            contour = self.find_marker_in_rect(image, current_marker_rect, threshold_mode, corner_marker)
            if contour is not None:
                return self.centered_search_rect(contour), contour

        # Go through whole image
        for y in range(int(part_offset_y), int(part_offset_y + part_height), int(self.marker_search_height / 2)):
            for x in range(int(part_offset_x), int(part_offset_x + part_width), int(self.marker_search_width / 2)):

                # Check bounds
                bx = min(x, part_offset_x + part_width - self.marker_search_width)
                by = min(y, part_offset_y + part_height - self.marker_search_height)

                # Calculate search rect
                search_rect = [bx, by, bx + self.marker_search_width, by + self.marker_search_height]

                # Search for contour
                contour = self.find_marker_in_rect(image, search_rect, threshold_mode, corner_marker)
                if contour is not None:

                    # Center search rect and find contour again in order to prevent it being "half found" at the edge
                    centered_rect = self.centered_search_rect(contour)
                    centered_contour = self.find_marker_in_rect(image, centered_rect, threshold_mode, corner_marker)
                    if centered_contour is not None:
                        return self.centered_search_rect(centered_contour), centered_contour

                    # Return contour no matter if contour is found in center or not
                    return self.centered_search_rect(contour), contour

        # No marker found
        return None, None

    def centered_search_rect(self, contour):
        x, y, width, height = cv2.boundingRect(contour)

        # Calculate offset
        offset_x = max(0, min(self.image_width - self.marker_search_width, x + ( width - self.marker_search_width) / 2))
        offset_y = max(0, min(self.image_height - self.marker_search_height, y + (height - self.marker_search_height) / 2))

        return [offset_x, offset_y, offset_x + self.marker_search_width, offset_y + self.marker_search_height]

    def find_marker_in_rect(self, image, search_rect, threshold_mode, corner_marker):

        #image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
        #search_contour = np.int32([(search_rect[0], search_rect[1]), (search_rect[2], search_rect[1]), (search_rect[2], search_rect[3]), (search_rect[0], search_rect[3])]).reshape(-1, 1, 2)
        #cv2.drawContours(image2, [search_contour], 0, (255, 0, 255), 1)
        #cv2.imshow("Search rect", image2)
        #cv2.waitKey(0)

        # Extract rect
        image = image[search_rect[1]:search_rect[3], search_rect[0]:search_rect[2]]

        # Threshold image
        thresholded_image = self.threshold_image(image, threshold_mode)

        # Find marker contour
        marker_result = corner_marker.find_marker_in_thresholded_image(thresholded_image)
        if marker_result is None:
            return None

        # Translate points to offset
        contour = marker_result["rawContour"]
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

        #image2 = image.copy()
        #cv2.drawContours(image2, [contour], 0, (255, 0, 255), 1)
        #cv2.imshow('Contour', image2)
        #cv2.waitKey(0)

        # Check if valid
        if not self.is_corner_combination_valid(contour):
            return None

        return [c[0] for c in contour]

    def is_corner_combination_valid(self, contour):
        if abs(cv2.contourArea(contour, False)) < self.board_area_min:
            #print("Contour area to small: %f < %f" % (abs(cv2.contourArea(contour, False)), self.board_area_min))
            return False

        if not self.has_correct_aspect_ratio(contour):
            #print("Contour has wrong aspect ratio: %f - %f < %f" % (self.contour_aspect_ratio(contour), self.board_aspect_ratio, self.board_aspect_ratio_deviation_max))
            return False

        if misc_math.max_cosine_from_contour(contour) > self.board_cosinus_max_deviation:
            #print("Contour has wrong angles: %f > %f" % (misc_math.max_cosine_from_contour(contour), self.board_cosinus_max_deviation))
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

        # Threshold image
        if mode == self.ThresholdModes.OTSU:
            image = cv2.blur(image, (2, 2))
            ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            return image
        elif mode == self.ThresholdModes.ADAPTIVE:
            return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        elif mode == self.ThresholdModes.AUTO:
            threshold_min, threshold_max = self.automatic_thresholding_for_image(image)
            return cv2.Canny(image, threshold_min, threshold_max)
        elif mode == self.ThresholdModes.BRIGHT_ROOM:
            return cv2.Canny(image, 40, 70)
        elif mode == self.ThresholdModes.DARK_ROOM:
            return cv2.Canny(image, 100, 300)
        else:
            return cv2.Canny(image, 60, 120)

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

    def board_snapshot_with_missing_corners(self, image, top_left, top_right, bottom_left, bottom_right):
        corners = []
        if top_left is None:
            corners.append("topLeft")
        if top_right is None:
            corners.append("topRight")
        if bottom_left is None:
            corners.append("bottomLeft")
        if bottom_right is None:
            corners.append("bottomRight")
        return BoardSnapshot(status=BoardStatus.NOT_RECOGNIZED, camera_image=image, missing_corners=corners)
