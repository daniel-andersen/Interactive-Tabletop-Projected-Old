import cv2
from server.reporters.reporter import Reporter
from board.board_descriptor import BoardDescriptor


class FindContoursReporter(Reporter):

    def __init__(self, board_area, approximation, remove_convex_hulls, stability_level, reporter_id, callback_function):
        """
        :param board_area: Board area
        :param approximation: Contour approximation constant
        :param remove_convex_hulls: Removes convex hulls
        :param stability_level Minimum board area stability level before searching for contours
        """
        super(FindContoursReporter, self).__init__(reporter_id, callback_function)

        self.board_area = board_area
        self.approximation = approximation
        self.remove_convex_hulls = remove_convex_hulls
        self.stability_level = stability_level

    def update(self):

        # Check sufficient stability
        if self.board_area.stability_score() < self.stability_level:
            return

        # Get area image
        image = self.board_area.grayscaled_area_image(snapshot_size=BoardDescriptor.SnapshotSize.ORIGINAL)
        if image is None:
            return

        image_height, image_width = image.shape[:2]

        # Threshold image
        image = cv2.blur(image, (3, 3))
        image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Find contours
        contours, hierarchy = cv2.findContours(image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        if len(contours) == 0:
            return []

        # Simplify contours
        approxed_contours = [cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * self.approximation, True) for contour in contours]

        # Remove convex hulls
        if self.remove_convex_hulls:
            approxed_contours = [cv2.convexHull(contour) for contour in approxed_contours]

        # Convert contours to result
        result_contours = []

        for index in range(0, len(contours)):
            contour = contours[index]
            approxed_contour = approxed_contours[index]
            result_contours.append({
                "contour": [[float(p[0][0]) / float(image_width), float(p[0][1]) / float(image_height)] for p in approxed_contour],
                "area": abs(cv2.contourArea(contour, True)) / float(image_width * image_height),
                "arclength": cv2.arcLength(contour, True)
            })

        # Convert hierarchy to result
        result_hierarchy = [[int(entry) for entry in h] for h in hierarchy[0]]

        # Return contours
        self.callback_function(result_contours, result_hierarchy)
        self.stop()
