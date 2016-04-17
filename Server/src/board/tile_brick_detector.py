import cv2
import numpy as np
import heapq
import histogram_util


class TileBrickDetector(object):
    """
    Class capable of recognizing tile bricks on a board.
    """

    def __init__(self):
        self.histogram_bin_count = 4
        self.histogram_bin_count_fallback = 2
        self.histogram_bin_count_fallback_2 = 8

        self.brick_detection_minimum_median_delta = 40
        self.brick_detection_minimum_probability = 0.28
        self.brick_detection_maximum_deviation = 0.6

    def find_brick_among_tiles(self, board_descriptor, coordinates):
        """
        Returns the coordinate of a brick from one the given tile coordinates.

        :param board_descriptor: Board descriptor
        :param coordinates: Coordinates [(x, y), ...] on which to search for a brick
        :return: (x, y), [probabilities...] - where (x, y) is position of brick, or None if no brick is found, followed by list of probabilities.
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
            return None, probabilities

        #print("2) %f - %f vs %f - %f" % (max_probability, second_max_probability, second_max_probability / max_probability, self.brick_detection_maximum_deviation))
        if second_max_probability / max_probability >= self.brick_detection_maximum_deviation:
            return None, probabilities

        return coordinates[np.argmax(probabilities)], probabilities

    def probabilities_of_bricks(self, tile_strip_image, coordinates, board_descriptor):
        return [self.probability_of_brick(i, tile_strip_image, board_descriptor) for i in range(0, len(coordinates))]

    def probability_of_brick(self, index, tile_strip_image, board_descriptor):

        # Extract brick image
        brick_image = board_descriptor.tile_from_strip_image(index, tile_strip_image)
        #cv2.imshow('OTSU Board Tiles {0}'.format(index), brick_image)

        # Calculate histogram from b/w image
        histogram = histogram_util.histogram_from_bw_image(brick_image)

        # Return black percentage
        tile_width, tile_height = board_descriptor.tile_size()
        #print("%f vs %f, %f" % (histogram[0][0], tile_width, tile_height))
        return histogram[0][0] / (tile_width * tile_height)
