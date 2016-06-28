import cv2


class Marker(object):

    def find_markers_in_image(self, image):
        """
        Find all markers in image.

        :param image: Image
        :return: List of markers each in form (contour, (contour, [centerX, centerY, width, height, rotation]))
        """
        return []

    def find_markers_in_thresholded_image(self, image):
        """
        Find all markers in image which has already been thresholded.

        :param image: Image
        :return: List of markers each in form (contour, (contour, [centerX, centerY, width, height, rotation]))
        """
        return []

    def find_marker_in_image(self, image):
        """
        Find marker in image.

        :param image: Image
        :return: Marker in form (contour, (contour, [centerX, centerY, width, height, rotation]))
        """
        return None

    def find_marker_in_thresholded_image(self, image):
        """
        Find marker in image which has already been thresholded.

        :param image: Thresholded image
        :return: Marker in form (contour, (contour, [centerX, centerY, width, height, rotation]))
        """
        return None

    def contour_to_marker_result(self, contour):
        """
        Extracts marker result from contour.

        :param contour: Contour
        :return: Result in form (contour, (contour, [centerX, centerY, width, height, rotation]))
        """
        return contour, cv2.minAreaRect(contour)

    def contours_to_marker_result(self, contours):
        """
        Extracts marker results from contours.

        :param contour: Contour
        :return: Result in form [(contour, [centerX, centerY, width, height, rotation])]
        """
        return [(contour, cv2.minAreaRect(contour)) for contour in contours]
