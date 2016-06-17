import numpy as np
import cv2
from board_descriptor import BoardDescriptor


class TiledBoardDescriptor(BoardDescriptor):
    """
    Represents a description of a board with tiled bricks.

    Field variables:
    tile_count -- [width, height]
    """

    def __init__(self):
        super(TiledBoardDescriptor, self).__init__()
        self.tile_count = None

    def tile_size(self):
        """
        Calculates the size of a tile.

        :return: Tile (width, height)
        """
        board_width, board_height = self.board_region()[4:6]
        return (float(board_width) / float(self.tile_count[0]),
                float(board_height) / float(self.tile_count[1]))

    def tile_region(self, x, y):
        """
        Calculates the tile region for tile at x, y.

        :param x: X coordinate
        :param y: Y coordinate
        :return: The (x1, y1, x2, y2, width, height) tile region
        """
        board_x1, board_y1, board_x2, board_y2, board_width, board_height = self.board_region()

        tile_width, tile_height = self.tile_size()

        return (int(board_x1 + (float(x) * tile_width)),
                int(board_y1 + (float(y) * tile_height)),
                int(board_x1 + (float(x) * tile_width)) + int(tile_width),
                int(board_y1 + (float(y) * tile_height)) + int(tile_height),
                int(tile_width),
                int(tile_height))

    def tile(self, x, y, source_image=None, grayscaled=False):
        """
        Returns the tile at x, y.

        :param x: X coordinate
        :param y: Y coordinate
        :param source_image: Source image, or None if using board image
        :param grayscaled: If true and source_image is None, use grayscaled image as source
        :return: The tile at x, y
        """
        if source_image is None:
            source_image = self.snapshot.board_image if not grayscaled else self.snapshot.grayscaled_board_image
        x1, y1, x2, y2 = self.tile_region(x, y)[:4]
        return source_image[y1:y2, x1:x2]

    def tile_strip(self, coordinates, source_image=None, grayscaled=False):
        """
        Returns the tiles at the specified coordinates.

        :param coordinates: List of coordinates [(x, y), ...]
        :param source_image: Source image, or None if using board image
        :param grayscaled: If true and source_image is None, use grayscaled image as source
        :return: The tiles in a single horizontal image strip
        """
        if source_image is None:
            source_image = self.snapshot.board_image if not grayscaled else self.snapshot.grayscaled_board_image

        tile_width, tile_height = self.tile_size()

        channels = source_image.shape[2] if len(source_image.shape) > 2 else 1
        if channels > 1:
            size = (int(tile_height), int(float(len(coordinates)) * tile_width), channels)
        else:
            size = (int(tile_height), int(float(len(coordinates)) * tile_width))

        image = np.zeros(size, source_image.dtype)

        offset = 0.0
        for (x, y) in coordinates:
            x1, y1, x2, y2 = self.tile_region(x, y)[:4]
            tile_image = source_image[y1:y2, x1:x2]
            image[0:int(tile_height), int(offset):int(offset) + int(tile_width)] = tile_image
            offset += tile_width

        return image

    def tile_from_strip_image(self, index, tile_strip_image):
        """
        Returns the tile at the given index from the given tile strip image.

        :param index: Tile index
        :param tile_strip_image: Tile strip image
        :return: The tile at the given index
        """
        tile_width, tile_height = self.tile_size()
        x1 = int(float(index) * tile_width)
        x2 = x1 + int(tile_width)
        return tile_strip_image[0:int(tile_height), x1:x2]
