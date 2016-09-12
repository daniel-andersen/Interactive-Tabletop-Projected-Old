from server import globals
from reporter import Reporter


class TiledBrickPositionReporter(Reporter):

    def __init__(self, tiled_board_area, valid_positions, stability_level, reporter_id, callback_function):
        """
        :param tiled_board_area: Tiled board area
        :param valid_positions Positions to search for brick in
        :param stability_level Minimum area stability level
        """
        super(TiledBrickPositionReporter, self).__init__(reporter_id, callback_function)

        self.tiled_board_area = tiled_board_area
        self.valid_positions = valid_positions
        self.stability_level = stability_level

    def run_iteration(self):

        # Check if we have a board area image
        if self.tiled_board_area.area_image() is None:
            return

        #if globals.debug:
            #cv2.imwrite("debug/output_board_recognized_{0}.png".format(self.reporter_id), globals.board_descriptor.snapshot.board_image())

        # Check sufficient stability
        if self.tiled_board_area.stability_score() < self.stability_level:
            return

        # Find brick
        position, probabilities = globals.brick_detector.find_brick_among_tiles(self.tiled_board_area, self.valid_positions)

        if self.is_position_ok(position):
            if globals.debug:
                print("%i: Brick recognized: %s" % (self.reporter_id, probabilities))
                #image = globals.camera.read()
                #cv2.imwrite("debug/output_brick_recognized_{0}.png".format(self.reporter_id), image)
                #cv2.imwrite("debug/output_brick_recognized_{0}_board.png".format(self.reporter_id), globals.board_descriptor.snapshot.board_image())
                #cv2.imwrite("debug/output_brick_recognized_{0}_strip.png".format(self.reporter_id), globals.board_descriptor.tile_strip(self.valid_positions))
            self.callback_function(position)
            self.stop()

    def is_position_ok(self, position):
        return position is not None
