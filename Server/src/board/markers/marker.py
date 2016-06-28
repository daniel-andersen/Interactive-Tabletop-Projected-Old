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

    def contour_to_marker_result(self, image, contour):
        """
        Extracts marker result from contour.

        :param image: Image
        :param contour: Contour
        :return: Result in form (contour, (contour, [centerX, centerY, width, height, rotation]))
        """
        image_height, image_width = image.shape[:2]
        box = cv2.minAreaRect(contour)

        return contour, [[float(box[0][0]) / float(image_width), float(box[0][1]) / float(image_height)],  # Center
                         [float(box[1][0]) / float(image_width), float(box[1][1]) / float(image_height)],  # Size
                         box[2]]  # Angle

    def contours_to_marker_result(self, image, contours):
        """
        Extracts marker results from contours.

        :param image: Image
        :param contour: Contour
        :return: Result in form [(contour, [centerX, centerY, width, height, rotation])]
        """
        return [self.contour_to_marker_result(image, contour) for contour in contours]
