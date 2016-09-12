import cv2
import time
import math
from reporter import Reporter
from board.board_descriptor import BoardDescriptor

class MarkerTracker(Reporter):

    def __init__(self, board_area, marker, reporter_id, callback_function):
        """
        :param board_area: Board area
        :param marker: Marker
        """
        super(MarkerTracker, self).__init__(reporter_id, callback_function)

        self.board_area = board_area
        self.marker = marker
        self.marker_bounds_pct = None
        self.marker_history = []
        self.marker_history_time = 2.0

    def run_iteration(self):

        # Update marker history
        while len(self.marker_history) > 0 and self.marker_history[0]["timestamp"] < time.time() - self.marker_history_time:
            self.marker_history.pop(0)

        # Get area image
        area_image = self.board_area.area_image(BoardDescriptor.SnapshotSize.SMALL)

        # Check if we have a board area image
        if area_image is None:
            return

        # Reset bounds if marker not found in a while
        if len(self.marker_history) is 0:
            self.marker_bounds_pct = None

        # Extract sub-image in which marker was last found
        area_image_bounded = self.image_from_bounds(area_image, self.marker_bounds_pct) if self.marker_bounds_pct else area_image

        #if self.marker_bounds_pct:
        #    cv2.imwrite("test.png", area_image_bounded)

        # Find marker
        marker_result = self.marker.find_marker_in_image(area_image_bounded, size_constraint_offset=0.1 if self.marker_bounds_pct else 0.0)

        if marker_result is not None:

            # Adjust size of marker if detected in smaller region
            if self.marker_bounds_pct:
                bounded_image_height, bounded_image_width = area_image_bounded.shape[:2]
                image_height, image_width = area_image.shape[:2]

                scale_x = float(bounded_image_width) / float(image_width)
                scale_y = float(bounded_image_height) / float(image_height)

                marker_result["x"] = (marker_result["x"] * scale_x) + self.marker_bounds_pct[0]
                marker_result["y"] = (marker_result["y"] * scale_y) + self.marker_bounds_pct[1]
                marker_result["width"] *= scale_x
                marker_result["height"] *= scale_y

            # Append marker to history
            self.marker_history.append({"timestamp": time.time(), "marker_result": marker_result})

            # Update bounds
            self.update_bounds(area_image, marker_result)

            # Notify client
            self.callback_function(marker_result)

    def update_bounds(self, area_image_bounded, marker_result):

        # Calculate offset into area image
        offset_x = self.marker_bounds_pct[0] if self.marker_bounds_pct else 0.0
        offset_y = self.marker_bounds_pct[1] if self.marker_bounds_pct else 0.0

        # Get image size
        image_height, image_width = area_image_bounded.shape[:2]

        # Get contour bounding rect
        x, y, width, height = cv2.boundingRect(marker_result["contour"])

        # Calculate top/left in percentage of image
        x = float(offset_x) + (float(x) / float(image_width))
        y = float(offset_y) + (float(y) / float(image_height))

        # Calculate size in percentage of image
        width = float(width) / float(image_width)
        height = float(height) / float(image_height)

        # Calculate padding
        padding_x = max(0.1, 20.0 / float(image_width))
        padding_y = max(0.1, 20.0 / float(image_height))

        # Update bounds
        self.marker_bounds_pct = [
            max(0.0, x - padding_x),
            max(0.0, y - padding_y),
            min(image_width, x + width + padding_x),
            min(image_height, y + height + padding_y)
        ]

    def image_from_bounds(self, image, bounds_pct):
        """
        Extracts subimage with given bounds in percentage.

        :param image: Original image
        :param bounds_pct: Bounds in percentage [x1, y1, x2, y2] in [0..1]
        :return: Sub-image
        """

        # Calculate bounds in image coordinates
        image_height, image_width = image.shape[:2]

        x1 = int(max(0.0, min(image_width - 1, float(image_width) * bounds_pct[0])))
        y1 = int(max(0.0, min(image_height - 1, float(image_height) * bounds_pct[1])))
        x2 = int(max(0.0, min(image_width - 1, float(image_width) * bounds_pct[2])))
        y2 = int(max(0.0, min(image_height - 1, float(image_height) * bounds_pct[3])))

        # Extract image
        return image[y1:y2, x1:x2]
