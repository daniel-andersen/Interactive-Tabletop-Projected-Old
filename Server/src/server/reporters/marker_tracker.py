import cv2
import time
from reporter import Reporter
from board.board_descriptor import BoardDescriptor
from util import misc_math


class MarkerTracker(Reporter):

    def __init__(self, board_area, marker, reporter_id, callback_function):
        """
        :param board_area: Board area
        :param marker: Marker
        """
        super(MarkerTracker, self).__init__(reporter_id, callback_function)

        self.board_area = board_area
        self.marker = marker
        self.marker_history = []
        self.marker_history_time = 2.0

    def run_iteration(self):

        # Update marker history
        while len(self.marker_history) > 0 and self.marker_history[0]["timestamp"] < time.time() - self.marker_history_time:
            self.marker_history.pop(0)

        # Get area image
        area_image = self.board_area.area_image(snapshot_size=self.marker.preferred_input_image_resolution())

        # Check if we have a board area image
        if area_image is None:
            return

        #cv2.imwrite("test.png", area_image_bounded)

        # Find marker
        marker_result = self.marker.find_marker_in_image(area_image)

        if marker_result is not None:

            # Append marker to history
            self.marker_history.append({"timestamp": time.time(), "marker_result": marker_result})

            # Notify client
            self.callback_function(marker_result)
