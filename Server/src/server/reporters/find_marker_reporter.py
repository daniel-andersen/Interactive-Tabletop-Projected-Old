import cv2
import time
from server import globals
from reporter import Reporter


class FindMarkerReporter(Reporter):

    def __init__(self, board_area, marker, stability_level, reporter_id, callback_function):
        """
        :param board_area: Board area
        :param marker: Marker
        :param stability_level Minimum board area stability level before searching for marker
        """
        super(FindMarkerReporter, self).__init__(reporter_id, callback_function)

        self.board_area = board_area
        self.marker = marker
        self.stability_level = stability_level

    def run_iteration(self):

        # Get area image
        image = self.board_area.area_image()

        # Check if we have a board area image
        if image is None:
            return

        # Check sufficient stability
        if self.board_area.stability_score() < self.stability_level:
            return

        # Find marker
        marker_result = self.marker.find_marker_in_image(image)
        if marker_result is None:
            return

        if globals.debug:
            print("%i: Marker recognized" % self.reporter_id)
            #cv2.imwrite("area.png", self.board_area.area_image())


        self.callback_function(marker_result)
        self.stop()
