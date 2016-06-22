import cv2
import numpy as np
from marker import Marker
from util import misc_math


class DefaultMarker(Marker):

    def find_marker_in_image(self, image):
        """
        Find marker in image.

        :param image: Image
        :return: Marker contour
        """

        # OTSU image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.blur(image, (2, 2))
        ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Find marker in OTSU'ed image
        return self.find_marker_in_thresholded_image(image)

    def find_marker_in_thresholded_image(self, image):
        """
        Find marker in image which has already been thresholded.

        :param image: Thresholded image
        :return: Marker contour
        """

        image_height, image_width = image.shape[:2]
        image = cv2.resize(image, (image_width * 2, image_height * 2))

        # Prepare constants
        image_height, image_width = image.shape[:2]
        min_marker_size = (image_width * 0.1) * (image_height * 0.1)
        max_marker_size = (image_width * 0.5) * (image_height * 0.5)

        # Filter away small noise
        #image = cv2.blur(image, (1, 1))
        #ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        #cv2.imshow("Marker image", image)
        #cv2.waitKey(0)

        # Find contours
        contours, hierarchy = \
            cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            return None

        # Filter away noise images
        if len(contours) > 8:
            return None

        # Simplify contours
        approxed_contours = []
        for contour in contours:

            # Approx contour
            approxed_contour = cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * 0.03, True)

            # Add to list
            approxed_contours.append(approxed_contour)

        #image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
        #cv2.drawContours(image2, contours, -1, (255, 0, 255), 1)
        #cv2.imshow('Contours', image2)

        #image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
        #cv2.drawContours(image2, approxed_contours, -1, (255, 0, 255), 1)
        #cv2.imshow('Approxed Contours', image2)
        #cv2.waitKey(0)

        # Find marker
        for i in range(0, len(approxed_contours)):
            #image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
            #cv2.drawContours(image2, [approxed_contours[i]], -1, (255, 0, 255), 1)
            #cv2.imshow('Contours', image2)
            #cv2.waitKey(0)

            if self.are_marker_conditions_satisfied_for_contour(contours, approxed_contours, hierarchy, i, min_marker_size, max_marker_size, (image_width, image_height)):

                #image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
                #cv2.drawContours(image2, [approxed_contours[hierarchy[0][i][2]]], -1, (255, 0, 255), 1)
                #cv2.imshow('Contours', image2)
                #cv2.waitKey(0)

                ac = approxed_contours[i]
                for i in range(0, len(ac)):
                    ac[i][0][0] /= 2
                    ac[i][0][1] /= 2
                return ac

        # No marker found
        return None

    def are_marker_conditions_satisfied_for_contour(self, contours, approxed_contours, hierachy, index, min_marker_size, max_marker_size, image_size):

        approxed_contour = approxed_contours[index]
        contour = contours[index]

        # Check number of lines
        if len(approxed_contour) != 6:
            #print("Len lines: %i" % len(approxed_contour))
            return False

        # Check area
        area = cv2.contourArea(contour, False)
        if area < min_marker_size:
            #print("Area too small: %f vs %f" % (area, min_marker_size))
            return False
        if area > max_marker_size:
            #print("Area too big: %f vs %f" % (area, max_marker_size))
            return False

        # Convex hulled contour must be approximately twice as big
        convex_hull_contour = cv2.convexHull(contour)
        convex_hull_area = cv2.contourArea(convex_hull_contour, False)

        if area < convex_hull_area * 2.0 / 4.0:
            #print("Convex hull area too big: %f vs %f" % (area, convex_hull_area))
            return False
        if area > convex_hull_area * 3.0 / 4.0:
            #print("Convex hull area too small: %f vs %f" % (area, convex_hull_area))
            return False

        # Get min and max line lengths
        min_length_index = np.argmin(np.array([self.line_length(approxed_contour, i) for i in range(0, len(approxed_contour))]))
        max_length_index = np.argmax(np.array([self.line_length(approxed_contour, i) for i in range(0, len(approxed_contour))]))

        # Small edges are at max half the length of the longest edges
        if self.line_length(approxed_contour, min_length_index) > self.line_length(approxed_contour, max_length_index) * 0.6:
            #print("Small edges too long")
            return False

        # Check that the long edges are approx same length
        if not self.are_lines_approx_same_length(approxed_contour, min_length_index + 1, min_length_index + 2, 0.8):
            #print("Long edges 1 not same length")
            return False

        if not self.are_lines_approx_same_length(approxed_contour, min_length_index - 1, min_length_index - 2, 0.7):
            #print("Long edges 2 not same length")
            return False

        # Not allowed to touch border
        x, y, width, height = cv2.boundingRect(contour)
        if x <= 0 or x + width >= image_size[0] - 1:
            #print("Touching horizontal border")
            return False
        if y <= 0 or y + height >= image_size[1] - 1:
            #print("Touching vertical border")
            return False

        #print("OK!")
        return True

    def are_lines_approx_same_length(self, contour, index1, index2, deviation=0.8):
        len1 = self.line_length(contour, index1)
        len2 = self.line_length(contour, index2)
        return min(len1, len2) >= max(len1, len2) * deviation

    def line_length(self, contour, index):
        index1 = (index + len(contour)) % len(contour)
        index2 = (index + 1 + len(contour)) % len(contour)
        return misc_math.line_length(contour[index1][0], contour[index2][0])

    """
    def are_marker_conditions_satisfied_for_contour_old(self, contour, approxed_contours, hierachy, index, min_marker_size, max_marker_size):
        approxed_contour = approxed_contours[index]

        # Check number of lines
        if len(approxed_contour) != 3:
            #print("Len lines: %i" % len(approxed_contour))
            return False

        # Check area
        area = cv2.contourArea(contour, False)
        if area < min_marker_size:
            #print("Area too small: %f vs %f" % (area, min_marker_size))
            return False
        if area > max_marker_size:
            #print("Area too big: %f vs %f" % (area, max_marker_size))
            return False

        # Check angles - must have two 45 degrees and one 90 degrees
        angle_count_45 = 0
        angle_count_90 = 0

        for i in range(2, len(approxed_contour) + 2):
            cosine = abs(misc_math.angle(approxed_contour[i % len(approxed_contour)][0],
                                         approxed_contour[(i - 2) % len(approxed_contour)][0],
                                         approxed_contour[(i - 1) % len(approxed_contour)][0]))
            if abs(math.cos(45 * math.pi / 180.0) - cosine) <= 0.2:
                angle_count_45 += 1
            if abs(math.cos(90 * math.pi / 180.0) - cosine) <= 0.3:
                angle_count_90 += 1

        if angle_count_45 != 2 or angle_count_90 != 1:
            #print("Angle: %i vs %i" % (angle_count_45, angle_count_90))
            return False

        #print("OK!")
        return True
    """