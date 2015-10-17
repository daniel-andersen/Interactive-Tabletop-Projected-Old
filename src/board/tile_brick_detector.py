from board.board_descriptor import BoardDescriptor
import cv2
import numpy as np
import heapq


class TileBrickDetector(object):
    """
    Class capable of recognizing tile bricks on a board.
    """

    def __init__(self):
        self.histogram_bin_count = 4
        self.histogram_bin_count_fallback = 2
        self.histogram_bin_count_fallback_2 = 8

        self.brick_detection_minimum_median_delta = 40
        self.brick_detection_minimum_probability = 0.4
        self.brick_detection_minimum_deviation = 0.7

    def find_brick_among_tiles(self, board_descriptor, coordinates):
        """
        Returns the coordinate of a brick from one the given tile coordinates.

        :param board_descriptor: Board descriptor
        :param coordinates: Coordinates [(x, y), ...] on which to search for a brick
        :return: Coordinate (x, y) of the brick, or None if no brick is found
        """
        # tile_strip_image = board_descriptor.tile_strip(coordinates)
        median_min, median_max = self.median_min_max_from_coordinates(coordinates, board_descriptor)
        if median_max - median_min < self.brick_detection_minimum_median_delta:
            return None

        histogram_bin_count = [self.histogram_bin_count, self.histogram_bin_count_fallback, self.histogram_bin_count_fallback_2]
        for i in range(0, len(histogram_bin_count)):
            probabilities = self.probabilities_of_bricks(coordinates, histogram_bin_count[i], board_descriptor)
            max_probability, second_max_probability = heapq.nlargest(2, probabilities)[:2]

            if max_probability < self.brick_detection_minimum_probability:
                continue
            if second_max_probability / max_probability >= self.brick_detection_minimum_deviation:
                continue

            return coordinates[np.argmax(probabilities)]

        return None

    def median_min_max_from_coordinates(self, coordinates, board_descriptor):
        """
        :param coordinates: Coordinates
        :param board_descriptor: Board descriptor
        :return: Median (min, max)
        """
        tile_images = [board_descriptor.tile(coordinates[i][0], coordinates[i][1]) for i in range(0, len(coordinates))]
        histograms = [self.histogram_from_image(tile_images[i], 256) for i in range(0, len(coordinates))]
        medians = [self.histogram_median(histograms[i], board_descriptor) for i in range(0, len(coordinates))]
        return np.min(medians), np.max(medians)

    def histogram_from_image(self, image, bin_count):
        return cv2.calcHist([image], [0], None, [bin_count], [0, 256])

    def histogram_median(self, histogram, board_descriptor):
        width, height = board_descriptor.tile_size()
        tile_pixel_size = width * height
        median = 0
        for i in range(0, len(histogram)):
            median += histogram[i] * i / tile_pixel_size
        return median

    def probabilities_of_bricks(self, coordinates, histogram_bin_count, board_descriptor):
        tile_strip_image = cv2.equalizeHist(board_descriptor.tile_strip(coordinates, board_descriptor.snapshot.grayscaled_board_image))
        return [self.probability_of_brick(i, tile_strip_image, histogram_bin_count, board_descriptor) for i in range(0, len(coordinates))]

    def probability_of_brick(self, index, tile_strip_image, histogram_bin_count, board_descriptor):
        equalized_brick_image = board_descriptor.tile_from_strip_image(index, tile_strip_image)
        histogram = self.histogram_from_image(equalized_brick_image, histogram_bin_count)
        tile_width, tile_height = board_descriptor.tile_size()
        return histogram[0][0] / (tile_width * tile_height)
