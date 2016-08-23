import tempfile
import os
import cv2
from marker import Marker


class HaarClassifierMarker(Marker):
    def __init__(self, cascade_data):
        """
        :param cascade_data: Haar cascade classifier data
        """
        super(HaarClassifierMarker, self).__init__()

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
        """
        Find marker in image.

        :param image: Image
        :return: Marker in form (contour, [centerX, centerY, width, height, rotation])
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return self.find_marker_in_thresholded_image(image)

    def find_marker_in_thresholded_image(self, image):

        # Find all markers
        markers = self.find_markers_in_thresholded_image(image)

        # Return first marker
        return markers[0] if len(markers) > 0 else (None, None)

    def find_markers_in_image(self, image):
        """
        Find all markers in image.

        :param image: Image
        :return: List of markers each in form (contour, [centerX, centerY, width, height, rotation])
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return self.find_markers_in_thresholded_image(image)

    def find_markers_in_thresholded_image(self, image):
        """
        Find all markers in image which has already been thresholded.

        :param image: Thresholded image
        :return: List of markers each in form (contour, [centerX, centerY, width, height, rotation])
        """
        matches = self.cascade_data.detectMultiScale(image)
        return [(None, [[int(x - (width / 2)), int(y - (height / 2))], [int(width), int(height)], 0]) for (x, y, width, height) in matches]
