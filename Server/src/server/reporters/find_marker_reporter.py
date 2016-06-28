import cv2
import time
from server import globals
from reporter import Reporter


class FindMarkerReporter(Reporter):

    def __init__(self, board_area, marker, stable_time, sleep_time, reporter_id, callback_function):
        """
        :param board_area: Board area
        :param marker: Marker
        :param stable_time Amount of time to wait for image to stabilize
        :param sleep_time: Time to sleep between searches
        """
        super(FindMarkerReporter, self).__init__(reporter_id, callback_function)

        self.board_area = board_area
        self.marker = marker
        self.stable_time = stable_time
        self.sleep_time = sleep_time

        self.marker_found_history = []

    def run_iteration(self):

        # Check if we have a board area image
        if self.board_area.area_image() is None:
            return

        # Find marker
        contour, box = self.marker.find_marker_in_image(self.board_area.area_image(reuse=True))

        # Update marker history
        self.marker_found_history.append({"time": time.time(), "found": box is not None})
        while len(self.marker_found_history) > 1 and self.marker_found_history[0]["time"] < time.time() - self.stable_time:
            self.marker_found_history.pop(0)

        # Count percentage of successes
        found_list = [entry["found"] for entry in self.marker_found_history]
        found_count = found_list.count(True)

        percentage = float(found_count) / float(len(found_list))

        if percentage >= 0.8:
            if globals.debug:
                print("%i: Marker recognized")
            self.callback_function(box)
            self.stop()
