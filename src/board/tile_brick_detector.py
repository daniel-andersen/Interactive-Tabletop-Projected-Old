from board.board_descriptor import BoardDescriptor
import cv2


class TileBrickDetector(object):
    """
    Class capable of recognizing tile bricks on a board.
    """

    def __init__(self):
        pass

    def find_brick_among_tiles(self, board_descriptor, coordinates):
        """
        Returns the coordinate of a brick from one the given tile coordinates.

        :param board_descriptor: Board descriptor
        :param coordinates: Coordinates [(x, y), ...] on which to search for a brick
        :return: Coordinate (x, y) of the brick, or None if no brick is found
        """
        return None
