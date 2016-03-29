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
        self.brick_detection_minimum_probability = 0.25
        self.brick_detection_maximum_deviation = 0.6

    def find_brick_among_tiles(self, board_descriptor, coordinates):
        """
        Returns the coordinate of a brick from one the given tile coordinates.

        :param board_descriptor: Board descriptor
        :param coordinates: Coordinates [(x, y), ...] on which to search for a brick
        :return: Coordinate (x, y) of the brick, or None if no brick is found
        """

        # Extract tile strip
        tile_strip_image = board_descriptor.tile_strip(coordinates, grayscaled=True)

        # OTSU strip
        _, tile_strip_image = cv2.threshold(tile_strip_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Calculate probabilities
        probabilities = self.probabilities_of_bricks(tile_strip_image, coordinates, board_descriptor)
        max_probability, second_max_probability = heapq.nlargest(2, probabilities)[:2]

        # Check probabilities
        #print("1) %f - %f vs %f" % (max_probability, second_max_probability, self.brick_detection_minimum_probability))
        if max_probability < self.brick_detection_minimum_probability:
            return None

        #print("2) %f - %f vs %f - %f" % (max_probability, second_max_probability, second_max_probability / max_probability, self.brick_detection_maximum_deviation))
        if second_max_probability / max_probability >= self.brick_detection_maximum_deviation:
            return None

        return coordinates[np.argmax(probabilities)]


        """
        median_min, median_max = self.median_min_max_from_coordinates(tile_strip_image, coordinates, board_descriptor)
        if median_max - median_min < self.brick_detection_minimum_median_delta:
            return None

        histogram_bin_count = [self.histogram_bin_count, self.histogram_bin_count_fallback, self.histogram_bin_count_fallback_2]
        for i in range(0, len(histogram_bin_count)):
            probabilities = self.probabilities_of_bricks(tile_strip_image, coordinates, histogram_bin_count[i], board_descriptor)
            max_probability, second_max_probability = heapq.nlargest(2, probabilities)[:2]

            print(max_probability)
            if max_probability < self.brick_detection_minimum_probability:
                continue
            if second_max_probability / max_probability >= self.brick_detection_minimum_deviation:
                continue

            return coordinates[np.argmax(probabilities)]

        return None
        """

    def median_min_max_from_coordinates(self, tile_strip_image, coordinates, board_descriptor):
        """
        :param tile_strip_image: Tile strip
        :param coordinates: Coordinates
        :param board_descriptor: Board descriptor
        :return: Median (min, max)
        """
        tile_images = [board_descriptor.tile_from_strip_image(i, tile_strip_image) for i in range(0, len(coordinates))]
        histograms = [self.histogram_from_image(tile_images[i], 256) for i in range(0, len(coordinates))]
        medians = [self.histogram_median(histograms[i], board_descriptor) for i in range(0, len(coordinates))]
        return np.min(medians), np.max(medians)

    def histogram_median(self, histogram, board_descriptor):
        width, height = board_descriptor.tile_size()
        tile_pixel_size = width * height
        median = 0
        for i in range(0, len(histogram)):
            median += histogram[i] * i / tile_pixel_size
        return median

    def histogram_from_image(self, image, bin_count):
        return cv2.calcHist([image], [0], None, [bin_count], [0, 256])

    def histogram_from_bw_image(self, image):
        return self.histogram_from_image(image, 2)

    def probabilities_of_bricks(self, tile_strip_image, coordinates, board_descriptor):
        return [self.probability_of_brick(i, tile_strip_image, board_descriptor) for i in range(0, len(coordinates))]

    def probability_of_brick(self, index, tile_strip_image, board_descriptor):
        # Extract brick image
        brick_image = board_descriptor.tile_from_strip_image(index, tile_strip_image)

        # Calculate histogram from b/w image
        histogram = self.histogram_from_bw_image(brick_image)

        # Return black percentage
        tile_width, tile_height = board_descriptor.tile_size()
        return histogram[0][0] / (tile_width * tile_height)
