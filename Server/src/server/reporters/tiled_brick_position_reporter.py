import cv2
import time
import heapq
from server import globals
from reporter import Reporter


class TiledBrickPositionReporter(Reporter):
    image_stable_history = []

    def __init__(self, valid_positions, stable_time, reporter_id, callback_function):
        """
        :param valid_positions Positions to search for brick in
        :param stable_time Amount of time to wait for image to stabilize
        """
        super(TiledBrickPositionReporter, self).__init__(reporter_id, callback_function)

        self.valid_positions = valid_positions
        self.stable_time = stable_time
        self.stability_level = 1.0

    def run_iteration(self):

        # Check if we have recognized the board
        if not globals.board_descriptor.is_recognized():
            return

        # Read image from camera
        image = globals.camera.read()
        if image is None:
            return

        #if globals.debug:
            #cv2.imwrite("debug/output_board_recognized_{0}.png".format(self.reporter_id), globals.board_descriptor.snapshot.board_image)

        # Find brick
        position, probabilities = globals.brick_detector.find_brick_among_tiles(globals.board_descriptor, self.valid_positions)

        # Update stability history
        self.image_stable_history.append({"time": time.time, "probabilities": probabilities})
        while len(self.image_stable_history) > 0 and self.image_stable_history[0]["time"] < time.time() - self.stable_time:
            self.image_stable_history.pop(0)

        # Calculate image stability score
        total_deviation = 0.0

        for i in range(0, len(self.valid_positions)):
            print("--> {0}".format(len(self.valid_positions)))
            for h in self.image_stable_history:
                print(len(h["probabilities"]))
            tile_probabilities = [h["probabilities"][i] for h in self.image_stable_history]
            total_deviation += max(tile_probabilities) - min(tile_probabilities)

        total_deviation /= float(len(self.valid_positions))

        if globals.debug:
            max_probability, second_max_probability = heapq.nlargest(2, probabilities)[:2]
            print("%i: Max/second max probabilities: %f, %f vs %f" % (self.reporter_id, max_probability, second_max_probability, total_deviation))

        # Check sufficient stability
        if total_deviation > self.stability_level:
            return

        if self.is_position_ok(position):
            if globals.debug:
                print("%i: Brick recognized" % self.reporter_id)
                cv2.imwrite("debug/output_brick_recognized_{0}.png".format(self.reporter_id), image)
            self.callback_function(position)
            self.stop()

    def is_position_ok(self, position):
        return position is not None
