import cv2
from board.board_descriptor import BoardDescriptor


class Marker(object):

    def __init__(self, marker_id):
        """
        :param marker_id: Marker ID
        """
        self.marker_id = marker_id

    def preferred_input_image_resolution(self):
        """
        Returns the preferred input resolution for this marker detector. Defaults to medium.

        :return: Input resolution (of type BoardDescriptor.SnapshotSize)
        """
        return BoardDescriptor.SnapshotSize.MEDIUM

    def find_markers_in_image(self, image, size_constraint_offset=0.0):
        """
        Find all markers in image.

        :param image: Image
        :param size_constraint_offset: Offset for size constraint. Used fx. when tracking in smaller areas.
        :return: List of markers each in form {"markerId", "x", "y", "width", "height", "angle", "contour"}
        """
        return []

    def find_markers_in_thresholded_image(self, image, size_constraint_offset=0.0):
        """
        Find all markers in image which has already been thresholded.

        :param image: Image
        :param size_constraint_offset: Offset for size constraint. Used fx. when tracking in smaller areas.
        :return: List of markers each in form {"markerId", "x", "y", "width", "height", "angle", "contour"}
        """
        return []

    def find_marker_in_image(self, image, size_constraint_offset=0.0):
        """
        Find marker in image.

        :param image: Image
        :param size_constraint_offset: Offset for size constraint. Used fx. when tracking in smaller areas.
        :return: Marker in form {"markerId", "x", "y", "width", "height", "angle", "contour"}
        """
        return None

    def find_marker_in_thresholded_image(self, image, size_constraint_offset=0.0):
        """
        Find marker in image which has already been thresholded.

        :param image: Thresholded image
        :param size_constraint_offset: Offset for size constraint. Used fx. when tracking in smaller areas.
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
