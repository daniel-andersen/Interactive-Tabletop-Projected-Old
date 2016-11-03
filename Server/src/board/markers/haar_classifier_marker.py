import tempfile
import os
import cv2
from threading import RLock
from board.markers.marker import Marker


class HaarClassifierMarker(Marker):
    def __init__(self, marker_id, cascade_data):
        """
        :param marker_id: Marker ID
        :param cascade_data: Haar cascade classifier data
        """
        super(HaarClassifierMarker, self).__init__(marker_id)

        self.lock = RLock()

        # Create the classifier from a temporary file containing the given data
        cascade_file = tempfile.NamedTemporaryFile(delete=False)

        try:
            cascade_file.write(cascade_data)
            cascade_file.close()

            # Create classifier
            self.cascade_data = cv2.CascadeClassifier(cascade_file.name)
        finally:
            os.remove(cascade_file.name)

    def find_marker_in_image(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return self.find_marker_in_thresholded_image(image)

    def find_marker_in_thresholded_image(self, image):

        # Find all markers
        markers = self.find_markers_in_thresholded_image(image)

        # Return first marker
        return markers[0] if len(markers) > 0 else None

    def find_markers_in_image(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return self.find_markers_in_thresholded_image(image)

    def find_markers_in_thresholded_image(self, image):

        # Find markers
        with self.lock:
            matches = self.cascade_data.detectMultiScale(image)

        # Return markers
        return [{"markerId": self.marker_id,
                 "x": int(x - (width / 2)),
                 "y": int(y - (height / 2)),
                 "width": int(width),
                 "height": int(height),
                 "angle": 0} for (x, y, width, height) in matches]
