from server import globals
from reporter import Reporter


class FindMarkersReporter(Reporter):

    def __init__(self, board_area, marker, stability_level, reporter_id, callback_function):
        """
        :param board_area: Board area
        :param marker: Marker
        :param stability_level Minimum board area stability level before searching for marker
        """
        super(FindMarkersReporter, self).__init__(reporter_id, callback_function)

        self.board_area = board_area
        self.marker = marker
        self.stability_level = stability_level

    def run_iteration(self):

        # Get area image
        image = self.board_area.area_image(reuse=True)

        # Check if we have a board area image
        if image is None:
            return

        # Check sufficient stability
        if self.board_area.stability_score() < self.stability_level:
            return

        # Find marker
        markers = self.marker.find_markers_in_image(image)

        if globals.debug:
            print("%i: Markers found" % self.reporter_id)
        self.callback_function(markers)
        self.stop()
