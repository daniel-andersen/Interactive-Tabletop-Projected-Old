import cv2
import math
from marker import Marker
from util import misc_math


class TriangleMarker(Marker):

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

        # Prepare constants
        image_height, image_width = image.shape[:2]
        min_marker_size = (image_width * 0.1) * (image_height * 0.1)
        max_marker_size = (image_width * 0.5) * (image_height * 0.5)

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
            approxed_contour = cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * 0.04, True)

            # Add to list
            approxed_contours.append(approxed_contour)

        #image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
        #cv2.drawContours(image2, approxed_contours, -1, (255, 0, 255), 1)
        #cv2.imshow('Contours', image2)
        #cv2.waitKey(0)

        # Find marker
        for i in range(0, len(approxed_contours)):
            #image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
            #cv2.drawContours(image2, [approxed_contours[i]], -1, (255, 0, 255), 1)
            #cv2.imshow('Contours', image2)
            #cv2.waitKey(0)

            if self.are_marker_conditions_satisfied_for_contour(contours, approxed_contours, hierarchy, i, min_marker_size, max_marker_size):

                #image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
                #cv2.drawContours(image2, [approxed_contours[hierarchy[0][i][2]]], -1, (255, 0, 255), 1)
                #cv2.imshow('Contours', image2)
                #cv2.waitKey(0)

                return approxed_contours[i]

        # No marker found
        return None

    def are_marker_conditions_satisfied_for_contour(self, contours, approxed_contours, hierachy, index, min_marker_size, max_marker_size):

        contour = contours[index]
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
