import cv2
import time
from random import uniform
from server import globals
from reporter import Reporter


class TiledBrickPositionReporter(Reporter):
    def __init__(self, valid_locations, stable_time):
        """
        :param valid_locations Locations to search for brick in
        :param stable_time Amount of time to wait for image to stabilize
        :param board_recognizer Board recognizer
        :param board_descriptor Board descriptor
        :param tile_brick_detector Tile brick detector
        :param camera Camera
        """
        self.valid_locations = valid_locations
        self.stable_time = stable_time
        self.stability_level = 1.0

    def run(self):
        """
        Waits for brick to be positioned at any of the valid positions.
        Callback function: (tile) -> ()
        """
        image_stable_history = []

        while not self.stopped:

            # Prevent the poor Raspberry Pi from overheating
            time.sleep(uniform(0.1, 0.2))

            # Read image from camera
            image = globals.camera.read()
            if image is None:
                continue

            # Find board from image
            globals.board_descriptor.snapshot = globals.board_recognizer.find_board(image, globals.board_descriptor)

            if globals.board_descriptor.is_recognized():
                #if globals.debug:
                    #cv2.imwrite("debug/output_board_recognized_{0}.png".format(self.reporter_id), globals.board_descriptor.snapshot.board_image)

                # Find brick
                (tile, probabilities) = globals.brick_detector.find_brick_among_tiles(globals.board_descriptor, self.valid_locations)

                # Update stability history
                image_stable_history.append({"time": time.time, "probabilities": probabilities})
                while len(image_stable_history) > 0 and image_stable_history[0]["time"] < time.time() - self.stable_time:
                    image_stable_history.pop(0)

                # Calculate image stability score
                total_deviation = 0.0

                for i in range(0, len(self.valid_locations)):
                    tile_probabilities = [h["probabilities"][i] for h in image_stable_history]
                    total_deviation += max(tile_probabilities) - min(tile_probabilities)

                    total_deviation /= float(len(self.valid_locations))

                if globals.debug:
                    print("Stability score: %f" % total_deviation)

                # Check sufficient stability
                if total_deviation > self.stability_level:
                    continue

                if tile is not None:
                    if globals.debug:
                        print("Brick recognized: %i" % self.reporter_id)
                        cv2.imwrite("debug/output_brick_recognized_{0}.png".format(self.reporter_id), image)
                    self.callback_function(tile)
                    self.stop()
            else:
                if globals.debug:
                    #cv2.imwrite("debug/output_board_not_recognized_{0}.png".format(self.reporter_id), image)
                    print("Board NOT recognized: %i" % self.reporter_id)
