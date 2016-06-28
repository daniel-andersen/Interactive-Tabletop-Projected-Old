import cv2
import time
from server import globals
from reporter import Reporter


class FindMarkersReporter(Reporter):

    def __init__(self, board_area, marker, stable_time, reporter_id, callback_function):
        """
        :param board_area: Board area
        :param marker: Marker
        :param stable_time Amount of time to wait for image to stabilize
        """
        super(FindMarkersReporter, self).__init__(reporter_id, callback_function)

        self.board_area = board_area
        self.marker = marker
        self.stable_time = stable_time

        self.markers_history = []

    def run_iteration(self):

        # Check if we have a board area image
        if self.board_area.area_image() is None:
            return

        # Find marker
        markers = self.marker.find_markers_in_image(self.board_area.area_image(reuse=True))

        # Update marker history
        self.markers_history.append({"time": time.time(), "markerCount": len(markers)})
        while len(self.markers_history) > 1 and self.markers_history[0]["time"] < time.time() - self.stable_time:
            self.markers_history.pop(0)

        # Check that all markers are the same
        marker_count = len(markers)
        for entry in self.markers_history:
            if entry["markerCount"] != marker_count:
                return

        if globals.debug:
            print("%i: Markers found")
        self.callback_function(markers)
        self.stop()
