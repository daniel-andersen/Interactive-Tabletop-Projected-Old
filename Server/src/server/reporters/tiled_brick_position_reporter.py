import cv2
import time
from server import globals
from reporter import Reporter


class TiledBrickPositionReporter(Reporter):

    def __init__(self, tiled_board_area, valid_positions, stable_time, reporter_id, callback_function):
        """
        :param tiled_board_area: Tiled board area
        :param valid_positions Positions to search for brick in
        :param stable_time Amount of time to wait for image to stabilize
        """
        super(TiledBrickPositionReporter, self).__init__(reporter_id, callback_function)

        self.tiled_board_area = tiled_board_area
        self.image_stable_history = []
        self.valid_positions = valid_positions
        self.stable_time = stable_time
        self.stability_level = 30.0

    def run_iteration(self):

        # Check if we have a board area image
        if self.tiled_board_area.area_image() is None:
            return

        #if globals.debug:
            #cv2.imwrite("debug/output_board_recognized_{0}.png".format(self.reporter_id), globals.board_descriptor.snapshot.board_image)

        # Calculate medians
        tile_strip_image = self.tiled_board_area.tile_strip(self.valid_positions, grayscaled=True)
        medians = globals.brick_detector.medians_of_tiles(tile_strip_image, self.valid_positions, self.tiled_board_area)

        # Update stability history
        oldest_time = self.image_stable_history[0]["time"] if len(self.image_stable_history) > 0 else time.time()

        self.image_stable_history.append({"time": time.time(), "medians": medians})
        while len(self.image_stable_history) > 1 and self.image_stable_history[0]["time"] < time.time() - self.stable_time:
            self.image_stable_history.pop(0)

        # Check if enough time has ellapsed
        if oldest_time > time.time() - self.stable_time:
            return

        # Calculate image stability score
        max_deviation = 0.0

        for i in range(0, len(self.valid_positions)):
            tile_medians = [h["medians"][i] for h in self.image_stable_history]
            deviation = max(tile_medians) - min(tile_medians)
            max_deviation = max(max_deviation, deviation)

        #if globals.debug:
        #    print("%i: Median deviation: %f" % (self.reporter_id, max_deviation))

        # Check sufficient stability
        if max_deviation > self.stability_level:
            return

        # Find brick
        position, probabilities = globals.brick_detector.find_brick_among_tiles(self.tiled_board_area, self.valid_positions)

        if self.is_position_ok(position):
            if globals.debug:
                print("%i: Brick recognized: %s" % (self.reporter_id, probabilities))
                #image = globals.camera.read()
                #cv2.imwrite("debug/output_brick_recognized_{0}.png".format(self.reporter_id), image)
                #cv2.imwrite("debug/output_brick_recognized_{0}_board.png".format(self.reporter_id), globals.board_descriptor.snapshot.board_image)
                #cv2.imwrite("debug/output_brick_recognized_{0}_strip.png".format(self.reporter_id), globals.board_descriptor.tile_strip(self.valid_positions))
            self.callback_function(position)
            self.stop()

    def is_position_ok(self, position):
        return position is not None
