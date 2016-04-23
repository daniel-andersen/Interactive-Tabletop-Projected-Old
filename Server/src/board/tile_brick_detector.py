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

        self.brick_detection_minimum_probability = 25.0
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

        # Calculate medians
        medians = self.medians_of_tiles(tile_strip_image, coordinates, board_descriptor)
        min_median, second_min_median = heapq.nsmallest(2, medians)[:2]
        max_median = max(medians)

        # Check medians
        #print(probabilities)
        #print("1) %f - %f vs %f" % (min_median, second_min_median, self.brick_detection_minimum_probability))
        if second_min_median - min_median < self.brick_detection_minimum_probability:
            return None, medians

        return coordinates[np.argmin(medians)], medians

    def medians_of_tiles(self, tile_strip_image, coordinates, board_descriptor):
        return [self.median_of_tile(i, tile_strip_image, board_descriptor) for i in range(0, len(coordinates))]

    def median_of_tile(self, index, tile_strip_image, board_descriptor):

        # Extract brick image
        brick_image = board_descriptor.tile_from_strip_image(index, tile_strip_image)

        # Remove border
        tile_width, tile_height = board_descriptor.tile_size()
        border_width = float(tile_width) * 0.1
        border_height = float(tile_height) * 0.1
        brick_image = brick_image[border_height:int(tile_height) - border_height, border_width:int(tile_width) - border_width]

        #cv2.imshow('OTSU Board Tiles {0}'.format(index), brick_image)

        # Calculate histogram from b/w image
        histogram = histogram_util.histogram_from_bw_image(brick_image)

        # Return median
        return histogram_util.histogram_median(histogram, ((tile_width - (border_width * 2.0)) * (tile_height - (border_height * 2.0))))
