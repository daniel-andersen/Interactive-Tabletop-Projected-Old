from reporter import Reporter


class MarkerTracker(Reporter):

    def __init__(self, board_area, marker, reporter_id, callback_function):
        """
        :param board_area: Board area
        :param marker: Marker
        """
        super(MarkerTracker, self).__init__(reporter_id, callback_function)

        self.board_area = board_area
        self.marker = marker

    def run_iteration(self):

        # Get area image
        image = self.board_area.area_image(reuse=True)

        # Check if we have a board area image
        if image is None:
            return

        # Find marker
        marker_result = self.marker.find_marker_in_image(image)
        if marker_result is not None:
            self.callback_function(marker_result)
