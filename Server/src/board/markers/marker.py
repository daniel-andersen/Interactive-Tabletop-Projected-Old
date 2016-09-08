import cv2


class Marker(object):

    def __init__(self, marker_id):
        """
        :param marker_id: Marker ID
        """
        self.marker_id = marker_id

    def find_markers_in_image(self, image):
        """
        Find all markers in image.

        :param image: Image
        :return: List of markers each in form {"markerId", "x", "y", "width", "height", "angle", "contour"}
        """
        return []

    def find_markers_in_thresholded_image(self, image):
        """
        Find all markers in image which has already been thresholded.

        :param image: Image
        :return: List of markers each in form {"markerId", "x", "y", "width", "height", "angle", "contour"}
        """
        return []

    def find_marker_in_image(self, image):
        """
        Find marker in image.

        :param image: Image
        :return: Marker in form {"markerId", "x", "y", "width", "height", "angle", "contour"}
        """
        return None

    def find_marker_in_thresholded_image(self, image):
        """
        Find marker in image which has already been thresholded.

        :param image: Thresholded image
        :return: Marker in form {"markerId", "x", "y", "width", "height", "angle", "contour"}
        """
        return None

    def contour_to_marker_result(self, image, contour):
        """
        Extracts marker result from contour.

        :param image: Image
        :param contour: Contour
        :return: Result in form {"markerId", "x", "y", "width", "height", "angle", "contour"}
        """
        image_height, image_width = image.shape[:2]
        box = cv2.minAreaRect(contour)

        return {"markerId": self.marker_id,
                "x": float(box[0][0]) / float(image_width),
                "y": float(box[0][1]) / float(image_height),
                "width": float(box[1][0]) / float(image_width),
                "height": float(box[1][1]) / float(image_height),
                "angle": box[2],
                "contour": contour}

    def contours_to_marker_result(self, image, contours):
        """
        Extracts marker results from contours.

        :param image: Image
        :param contours: Contours
        :return: List of markers each in form {"markerId", "x", "y", "width", "height", "angle", "contour"}
        """
        return [self.contour_to_marker_result(image, contour) for contour in contours]
