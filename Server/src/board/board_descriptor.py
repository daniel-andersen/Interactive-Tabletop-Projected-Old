import numpy as np
import cv2
from random import randint
from threading import RLock
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
    SnapshotSize = enum.Enum('EXTRA_SMALL', 'SMALL', 'MEDIUM', 'LARGE', 'ORIGINAL')

    def __init__(self):
        self.snapshot = None
        self.board_size = None
        self.border_percentage_size = [0.0, 0.0]
        self.tile_count = None
        self.corner_marker = None

    def is_recognized(self):
        """
        Indicates whether the board has been recognized in the source image or not.

        :return: True, if the board has been recognized in the source image, else false
        """
        return True if self.snapshot is not None and self.snapshot.status == BoardStatus.RECOGNIZED else False

    def border_size(self, image_size=SnapshotSize.SMALL):
        """
        Calculates the border pixel size.

        :param image_size: Image size
        :return: (width, height) in image
        """
        height, width = self.snapshot.board_image(image_size).shape[:2]
        return float(width) * float(self.border_percentage_size[0]), float(height) * float(self.border_percentage_size[1])

    def board_region(self, image_size=SnapshotSize.SMALL):
        """
        Calculates the board region, that is, the non-border image region.

        :param image_size: Image size
        :return: (x1, y1, x2, y2, width, height) in image
        """
        image_height, image_width = self.snapshot.board_image(image_size).shape[:2]
        border_width, border_height = self.border_size(image_size)

        return (float(border_width),
                float(border_height),
                float(image_width) - float(border_width),
                float(image_height) - float(border_height),
                float(image_width) - float((border_width * 2)),
                float(image_height) - float((border_height * 2)))

    def board_canvas(self, image_size=SnapshotSize.SMALL):
        """
        Extracts the board canvas, that is, the non-border area of the image.

        :param image_size: Image size
        :return: The board canvas image
        """

        if self.border_percentage_size == [0.0, 0.0]:
            return self.snapshot.board_image(image_size)
        else:
            return self.snapshot.board_canvas_image(self.board_region(image_size), image_size)

    def tile_size(self, image_size=SnapshotSize.SMALL):
        """
        Calculates the size of a tile.

        :param image_size: Image size
        :return: Tile (width, height)
        """
        board_width, board_height = self.board_region(image_size)[4:6]
        return (float(board_width) / float(self.tile_count[0]),
                float(board_height) / float(self.tile_count[1]))

    def tile_region(self, x, y, image_size=SnapshotSize.SMALL):
        """
        Calculates the tile region for tile at x, y.

        :param x: X coordinate
        :param y: Y coordinate
        :param image_size: Image size
        :return: The (x1, y1, x2, y2, width, height) tile region
        """
        board_x1, board_y1, board_x2, board_y2, board_width, board_height = self.board_region(image_size)

        tile_width, tile_height = self.tile_size(image_size)

        return (int(board_x1 + (float(x) * tile_width)),
                int(board_y1 + (float(y) * tile_height)),
                int(board_x1 + (float(x) * tile_width)) + int(tile_width),
                int(board_y1 + (float(y) * tile_height)) + int(tile_height),
                int(tile_width),
                int(tile_height))

    def tile(self, x, y, source_image=None, grayscaled=False, image_size=SnapshotSize.SMALL):
        """
        Returns the tile at x, y.

        :param x: X coordinate
        :param y: Y coordinate
        :param source_image: Source image, or None if using board image
        :param grayscaled: If true and source_image is None, use grayscaled image as source
        :param image_size: Image size
        :return: The tile at x, y
        """
        if source_image is None:
            source_image = self.snapshot.board_image(image_size) if not grayscaled else self.snapshot.grayscaled_board_image(image_size)
        x1, y1, x2, y2 = self.tile_region(x, y, image_size)[:4]
        return source_image[y1:y2, x1:x2]

    def tile_strip(self, coordinates, source_image=None, grayscaled=False, image_size=SnapshotSize.SMALL):
        """
        Returns the tiles at the specified coordinates.

        :param coordinates: List of coordinates [(x, y), ...]
        :param source_image: Source image, or None if using board image
        :param grayscaled: If true and source_image is None, use grayscaled image as source
        :param image_size: Image size
        :return: The tiles in a single horizontal image strip
        """
        if source_image is None:
            source_image = self.snapshot.board_image(image_size) if not grayscaled else self.snapshot.grayscaled_board_image(image_size)

        tile_width, tile_height = self.tile_size(image_size)

        channels = source_image.shape[2] if len(source_image.shape) > 2 else 1
        if channels > 1:
            size = (int(tile_height), int(float(len(coordinates)) * tile_width), channels)
        else:
            size = (int(tile_height), int(float(len(coordinates)) * tile_width))

        image = np.zeros(size, source_image.dtype)

        offset = 0.0
        for (x, y) in coordinates:
            x1, y1, x2, y2 = self.tile_region(x, y, image_size)[:4]
            tile_image = source_image[y1:y2, x1:x2]
            image[0:int(tile_height), int(offset):int(offset) + int(tile_width)] = tile_image
            offset += tile_width

        return image

    def tile_from_strip_image(self, index, tile_strip_image, image_size=SnapshotSize.SMALL):
        """
        Returns the tile at the given index from the given tile strip image.

        :param index: Tile index
        :param tile_strip_image: Tile strip image
        :param image_size: Image size
        :return: The tile at the given index
        """
        tile_width, tile_height = self.tile_size(image_size)
        x1 = int(float(index) * tile_width)
        x2 = x1 + int(tile_width)
        return tile_strip_image[0:int(tile_height), x1:x2]


class BoardSnapshot:
    """Represents a snapshot (current camera feed image) of a board.

    Field variables:
    status -- Board recognition status
    camera_image -- Original camera image
    board_images -- The recognized and transformed images in all sizes
    grayscaled_board_images -- A grayscale version of the board images in all sizes
    board_corners -- The four points in the source image representing the corners of the recognized board
    missing_corners -- Dictionary of missing corners, if board was not recognized. {topLeft, topRight, bottomLeft, bottomRight}
    id -- Random ID for the actual snapshot. Is set automatically when created
    """

    def __init__(self, status=BoardStatus.RECOGNIZED, camera_image=None, board_image=None, board_corners=None, missing_corners=None):
        self.status = status
        self.camera_image = camera_image
        self.board_images = {}
        self.grayscaled_board_images = {}
        self.board_canvas_images = {}
        self.board_corners = board_corners
        self.missing_corners = missing_corners

        self.id = randint(0, 100000)

        self.lock = RLock()

        if board_image is not None:
            self.board_images[BoardDescriptor.SnapshotSize.ORIGINAL] = board_image

    def board_image(self, image_size=BoardDescriptor.SnapshotSize.SMALL):
        """
        Returns the board image in the given size.

        :param image_size:
        :return: Board image in given size
        """

        with self.lock:

            # Check if image already exists
            if image_size in self.board_images:
                return self.board_images[image_size]

            if BoardDescriptor.SnapshotSize.ORIGINAL not in self.board_images:
                return None

            # Original image measurements
            original_image = self.board_images[BoardDescriptor.SnapshotSize.ORIGINAL]
            original_height, original_width = original_image.shape[:2]
            aspect_ratio = float(original_height) / float(original_width)

            # Find scaled width
            dest_width = original_width
            if image_size is BoardDescriptor.SnapshotSize.EXTRA_SMALL:
                dest_width = 320.0
            elif image_size is BoardDescriptor.SnapshotSize.SMALL:
                dest_width = 640.0
            elif image_size is BoardDescriptor.SnapshotSize.MEDIUM:
                dest_width = 800.0
            elif image_size is BoardDescriptor.SnapshotSize.LARGE:
                dest_width = 1200.0

            # Resize image
            if dest_width < original_width:
                self.board_images[image_size] = cv2.resize(original_image, (int(dest_width), int(dest_width * aspect_ratio)))
            else:
                self.board_images[image_size] = original_image

            return self.board_images[image_size]

    def grayscaled_board_image(self, image_size=BoardDescriptor.SnapshotSize.SMALL):
        """
        Returns the grayscaled board image in the given size.

        :param image_size: Image size
        :return: Grayscaled board image in given size
        """

        with self.lock:

            # Check if image already exists
            if image_size in self.grayscaled_board_images:
                return self.grayscaled_board_images[image_size]

            # Check for original board image
            if BoardDescriptor.SnapshotSize.ORIGINAL not in self.board_images:
                return None

            # Grayscale imagae
            self.grayscaled_board_images[image_size] = cv2.cvtColor(self.board_image(image_size), cv2.COLOR_BGR2GRAY)
            return self.grayscaled_board_images[image_size]

    def board_canvas_image(self, canvas_region, image_size=BoardDescriptor.SnapshotSize.SMALL):
        """
        Returns the grayscaled board image in the given size.

        :param canvas_region: Canvas region (x1, y1, x2, y2)
        :param image_size: Image size
        :return: Grayscaled board image in given size
        """

        with self.lock:

            # Check if already present
            if image_size not in self.board_canvas_images:

                # Extract board image
                board_image = self.board_image(image_size)
                if board_image is None:
                    return None

                # Extract region
                self.board_canvas_images[image_size] = board_image[
                                                       int(canvas_region[1]):int(canvas_region[3]),
                                                       int(canvas_region[0]):int(canvas_region[2])]

            return self.board_canvas_images[image_size]
