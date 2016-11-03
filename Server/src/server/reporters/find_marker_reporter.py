import cv2
from server import globals
from server.reporters.reporter import Reporter


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

    def update(self):

        # Get area image
        image = self.board_area.area_image(snapshot_size=self.marker.preferred_input_image_resolution())

        # Check if we have a board area image
        if image is None:
            return

        # Check sufficient stability
        if self.board_area.stability_score() < self.stability_level:
            return

        # Find marker
        marker_result = self.marker.find_marker_in_image(image)
        if marker_result is None:
            #cv2.imwrite("area.png", self.board_area.area_image())
            return

        if globals.get_state().debug:
            print("%i: Marker recognized" % self.reporter_id)
            #cv2.imwrite("area.png", self.board_area.area_image())

        self.callback_function(marker_result)
        self.stop()
