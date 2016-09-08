from server import globals
from reporter import Reporter


class FindMarkersReporter(Reporter):

    def __init__(self, board_area, markers, stability_level, reporter_id, callback_function):
        """
        :param board_area: Board area
        :param markers: Markers to search for
        :param stability_level Minimum board area stability level before searching for markers
        """
        super(FindMarkersReporter, self).__init__(reporter_id, callback_function)

        self.board_area = board_area
        self.markers = markers
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

        # Find markers
        result = []
        for marker in self.markers:
            marker_result = marker.find_marker_in_image(image)
            if marker_result:
                result.append(marker_result)

        if globals.debug:
            print("%i: Markers found: %i" % (self.reporter_id, len(result)))
        self.callback_function(result)
        self.stop()
