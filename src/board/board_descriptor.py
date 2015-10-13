from screen.screen import Screen


class BoardDescriptor(object):
    """Represents a description of a board. Can be initialized (and reset) with a board descriptor object.

    Field variables:

    board_image -- The recognized and transformed image
    board_corners -- The four points in the source image representing the corners of the recognized board

    border_percentage_size -- [width (percent / 100), height (percent / 100)]

    tile_count -- [width, height]
    tile_size -- [width, height]
    """
    def __init__(self, board_descriptor=None):
        self.board_image = board_descriptor.board_image if board_descriptor is not None else None
        self.board_corners = board_descriptor.board_corners if board_descriptor is not None else None
        self.border_percentage_size = board_descriptor.border_percentage_size if board_descriptor is not None else None
        self.tile_count = board_descriptor.tile_count if board_descriptor is not None else None
        self.board_canvas_image = None
        self.tile_canvas_image = None
        self.tile_size = None

    def is_recognized(self):
        """
        Indicates whether the board has been recognized in the source image or not.
        :return: True, if the board has been recognized in the source image, else false
        """
        return True if self.board_image is not None else False

    def border_size(self, image):
        """
        Calculates the border size in the given image.
        :return: (width, height) in image
        """
        height, width = image.shape[:2]
        return width * self.border_percentage_size[0], height * self.border_percentage_size[1]

    def board_region(self, image):
        """
        Calculates the board region in the given image, that is, the non-border image region.
        :return: (x1, y1, x2, y2) in image
        """
        image_height, image_width = image.shape[:2]
        border_width, border_height = self.border_size(image)
        return [border_width,
                border_height,
                image_width - border_width,
                image_height - border_height]

    def board_canvas(self):
        """
        Extracts the board canvas from the transformed image, that is, the non-border area of the image.
        :return: The board canvas image
        """
        if self.board_canvas_image is None:
            region = self.board_region(self.board_image)
            self.board_canvas_image = self.board_image[region[1]:region[3], region[0]:region[2]]

        return self.board_canvas_image

    def tile_canvas(self):
        """
        Extracts the tile canvas from the transformed image, that is, the area of the image containing tiles.
        :return: The tile canvas image
        """
