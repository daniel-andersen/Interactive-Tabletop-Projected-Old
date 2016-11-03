from server import globals
from server.reporters.reporter import Reporter


class TiledBrickPositionsReporter(Reporter):

    def __init__(self, tiled_board_area, valid_positions, stability_level, reporter_id, callback_function):
        """
        :param tiled_board_area: Tiled board area
        :param valid_positions Positions to search for bricks in
        :param stability_level Minimum area stability level
        """
        super(TiledBrickPositionsReporter, self).__init__(reporter_id, callback_function)

        self.tiled_board_area = tiled_board_area
        self.valid_positions = valid_positions
        self.stability_level = stability_level

    def update(self):

        # Check if we have a board area image
        if self.tiled_board_area.area_image() is None:
            return

        # Check sufficient stability
        if self.tiled_board_area.stability_score() < self.stability_level:
            return

        # Find bricks
        result = globals.get_state().get_brick_detector().find_bricks_among_tiles(self.tiled_board_area, self.valid_positions)

        self.callback_function([position for position, detected, propability in result if detected])
        self.stop()
