class Marker(object):

    def find_markers_in_image(self, image):
        """
        Find all markers in image.

        :param image: Image
        :return: List of marker contours
        """
        return []

    def find_marker_in_image(self, image):
        """
        Find marker in image.

        :param image: Image
        :return: Marker contour
        """
        return None

    def find_marker_in_thresholded_image(self, image):
        """
        Find marker in image which has already been thresholded.

        :param image: Thresholded image
        :return: Marker contour
        """
        return None
