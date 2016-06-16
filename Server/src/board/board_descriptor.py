import numpy as np
import cv2
from markers.default_marker import DefaultMarker
from util import enum


BoardStatus = enum.Enum('NOT_RECOGNIZED', 'RECOGNIZED')


class BoardDescriptor(object):
    """
    Represents a description of a board.

    Field variables:
    snapshot -- Board snapshot
    board_size -- [width, height]
    border_percentage_size -- [width (percent / 100), height (percent / 100)]
    tile_count -- [width, height]
    corner_marker -- Corner marker to use as detection
    """
    class Snapshot:
        """Represents a snapshot (current camera feed image) of a board.

        Field variables:
        status -- Board recognition status
        board_image -- The recognized and transformed image
        grayscaled_board_image -- A grayscale version of the board image
        board_corners -- The four points in the source image representing the corners of the recognized board
        missing_corners -- Dictionary of missing corners, if board was not recognized. {topLeft, topRight, bottomLeft, bottomRight}
        """
        def __init__(self, status=BoardStatus.RECOGNIZED, board_image=None, board_corners=None, missing_corners=None):
            self.status = status
            self.board_image = board_image
            self.board_corners = board_corners
            self.missing_corners = missing_corners
            self.grayscaled_board_image = cv2.cvtColor(board_image, cv2.COLOR_BGR2GRAY) if board_image is not None else None
            self.board_canvas_image = None

    def __init__(self):
        self.snapshot = None
        self.board_size = None
        self.border_percentage_size = None
        self.tile_count = None
        self.corner_marker = DefaultMarker()

    def is_recognized(self):
        """
        Indicates whether the board has been recognized in the source image or not.
        :return: True, if the board has been recognized in the source image, else false
        """
        return True if self.snapshot is not None and self.snapshot.status == BoardStatus.RECOGNIZED else False

    def border_size(self):
        """
        Calculates the border pixel size.
        :return: (width, height) in image
        """
        height, width = self.snapshot.board_image.shape[:2]
        return float(width) * float(self.border_percentage_size[0]), float(height) * float(self.border_percentage_size[1])

    def board_region(self):
        """
        Calculates the board region, that is, the non-border image region.
        :return: (x1, y1, x2, y2, width, height) in image
        """
        image_height, image_width = self.snapshot.board_image.shape[:2]
        border_width, border_height = self.border_size()

        return (float(border_width),
                float(border_height),
                float(image_width) - float(border_width),
                float(image_height) - float(border_height),
                float(image_width) - float((border_width * 2)),
                float(image_height) - float((border_height * 2)))

    def board_canvas(self):
        """
        Extracts the board canvas, that is, the non-border area of the image.
        :return: The board canvas image
        """
        if self.snapshot.board_canvas_image is None:
            region = self.board_region()
            self.snapshot.board_canvas_image = self.snapshot.board_image[region[1]:region[3], region[0]:region[2]]

        return self.snapshot.board_canvas_image

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
