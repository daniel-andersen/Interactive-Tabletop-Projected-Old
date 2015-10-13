from screen.screen import Screen


class BoardDescriptor(object):
    """Represents a description of a board.

    board_image -- The recognized and transformed image
    board_corners -- The four points in the source image representing the corners of the recognized board

    border_size -- [width pixels, height pixels]

    tile_count -- [width, height]
    """
    def __init__(self, board_image, board_corners):
        self.board_image = board_image
        self.board_corners = board_corners
        self.border_size = [0, 0]
        self.tile_count = [0, 0]

    def is_recognized(self):
        """
        Indicates whether the board has been recognized in the source image or not.
        :return: True, if the board has been recognized in the source image, else false
        """
        return True if self.board_image is not None else False

    def border_size_in_transformed_image(self):
        """
        Calculates the border size in the transformed image.
        :return: [width, height] in transformed image
        """
        return [self.board_image.cols * self.border_size[0] / Screen().width,
                self.board_image.rows * self.border_size[1] / Screen().height]
