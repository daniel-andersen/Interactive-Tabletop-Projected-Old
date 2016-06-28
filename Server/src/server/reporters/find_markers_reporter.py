import cv2
import time
from server import globals
from reporter import Reporter


class FindMarkersReporter(Reporter):

    def __init__(self, board_area, marker, reporter_id, callback_function):
        """
        :param board_area: Board area
        :param marker: Marker
        """
        super(FindMarkersReporter, self).__init__(reporter_id, callback_function)

        self.board_area = board_area
        self.marker = marker

    def run_iteration(self):

        # Check if we have a board area image
        if self.board_area.area_image() is None:
            self.callback_function([])
            self.stop()
            return

        # Find marker
        contour, box = self.marker.find_markers_in_image(self.board_area.area_image(reuse=True))

        # Callback
        self.callback_function(box)

        # Stop reporter
        self.stop()
