import cv2
import numpy as np
import heapq
import histogram_util


class TileBrickDetector(object):
    """
    Class capable of recognizing tile bricks on a board.
    """

    def __init__(self):
        self.brick_detection_minimum_median_delta = 20.0
        self.brick_detection_minimum_probability = 0.15
        self.brick_detection_minimum_probability_delta = 0.35

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

        # Check medians
        #print("1) %f - %f = %f" % (min_median, second_min_median, second_min_median - min_median))
        if second_min_median - min_median < self.brick_detection_minimum_median_delta:
            return None, [0.0 for _ in medians]

        # OTSU strip
        _, tile_strip_image = cv2.threshold(tile_strip_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Calculate probabilities
        probabilities = self.probabilities_of_bricks(tile_strip_image, coordinates, board_descriptor)
        max_probability, second_max_probability = heapq.nlargest(2, probabilities)[:2]

        # Check probabilities
        #print("2) %f - %f = %f" % (max_probability, second_max_probability, max_probability - second_max_probability))
        #print(probabilities)
        if max_probability < self.brick_detection_minimum_probability:
            return None, probabilities

        if max_probability - second_max_probability < self.brick_detection_minimum_probability_delta:
            return None, probabilities

        return coordinates[np.argmin(medians)], probabilities

    def medians_of_tiles(self, tile_strip_image, coordinates, board_descriptor):
        return [self.median_of_tile(i, tile_strip_image, board_descriptor) for i in range(0, len(coordinates))]

    def median_of_tile(self, index, tile_strip_image, board_descriptor):

        # Extract brick image
        brick_image = board_descriptor.tile_from_strip_image(index, tile_strip_image)

        # Remove border
        tile_width, tile_height = board_descriptor.tile_size()
        border_width = int(float(tile_width) * 0.1)
        border_height = int(float(tile_height) * 0.1)
        brick_image = brick_image[border_height:int(tile_height) - border_height, border_width:int(tile_width) - border_width]

        # Calculate histogram from b/w image
        histogram = histogram_util.histogram_from_bw_image(brick_image)

        # Return median and black percentage
        return histogram_util.histogram_median(histogram, ((tile_width - (border_width * 2)) * (tile_height - (border_height * 2))))

    def probabilities_of_bricks(self, tile_strip_image, coordinates, board_descriptor):
        return [self.probability_of_brick(i, tile_strip_image, board_descriptor) for i in range(0, len(coordinates))]

    def probability_of_brick(self, index, tile_strip_image, board_descriptor):

        # Extract brick image
        brick_image = board_descriptor.tile_from_strip_image(index, tile_strip_image)

        # Remove border
        tile_width, tile_height = board_descriptor.tile_size()
        border_width = int(float(tile_width) * 0.1)
        border_height = int(float(tile_height) * 0.1)
        brick_image = brick_image[border_height:int(tile_height) - border_height, border_width:int(tile_width) - border_width]

        # Calculate histogram from b/w image
        histogram = histogram_util.histogram_from_bw_image(brick_image)

        # Return black percentage
        return histogram[0][0] / (tile_width * tile_height)
