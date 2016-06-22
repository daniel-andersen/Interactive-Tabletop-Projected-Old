import cv2
import math
import numpy as np
from marker import Marker
from util import misc_math
from util import contour_util


class CustomMarker(Marker):

    def __init__(self, contour=None, marker_image=None, distance_tolerance=0.15, angle_tolerance=0.15,
                 fine_grained=True, spike_tolerance=0.025, closed=True, min_arclength=0.1, max_arclength=100.0,
                 min_area=0.02, max_area=1.0):
        """
        :param contour: Simplified marker contour (containing fx. only corners)
        :param marker_image: Image from which to extract marker contour
        :param distance_tolerance: Distance tolerance in multitudes of length
        :param angle_tolerance: Angle tolerance in radians in range [0..pi]
        :param fine_grained: If true, verify that all points lies on contour edge
        :param spike_tolerance: Spike distance tolerance for fine-grained lines
        :param closed: Indicated wheter the contour is closed or not
        :param min_arclength: Minimum arc length scaled in multitudes of max(image width, image height)
        :param max_arclength: Maximum arc length scaled in multitudes of max(image width, image height)
        :param min_area: Minimum area scaled in percentage [0, 1] of image size
        :param max_area: Maximum area scaled in percentage [0, 1] of image size
        """
        super(CustomMarker, self).__init__()

        self.marker_contour = contour
        self.distance_tolerance = distance_tolerance
        self.angle_tolerance = angle_tolerance
        self.fine_grained = fine_grained
        self.spike_tolerance = spike_tolerance
        self.closed = closed
        self.min_arclength = min_arclength
        self.max_arclength = max_arclength
        self.min_area = min_area
        self.max_area = max_area

        if marker_image is not None:
            self.marker_contour = self.extract_marker_contour_from_image(marker_image)

        self.marker_length = len(self.marker_contour)
        self.marker_arclength = cv2.arcLength(self.marker_contour, self.closed)
        self.marker_area = cv2.contourArea(self.marker_contour, True)
        self.marker_distance_map = [self.distance_map_for_contour(self.marker_contour, -1),
                                    self.distance_map_for_contour(self.marker_contour,  1)]
        self.marker_angle_map = [self.angle_map_for_contour(self.marker_contour, -1),
                                 self.angle_map_for_contour(self.marker_contour,  1)]

        self.marker_orientation = -1 if self.marker_area < 0 else 1

    def extract_marker_contour_from_image(self, image):

        # OTSU image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        if len(contours) == 0:
            print("No contours found in marker image! Bailing out!")
            return None

        if len(contours) > 1:
            print("More than one contour found in marker image! Bailing out!")
            return None

        # Simplify contour
        approxed_contour = contour_util.simplify_contour(contours[0])

        return approxed_contour

    def find_marker_in_image(self, image):
        """
        Find marker in image.

        :param image: Image
        :return: Marker contour
        """

        # OTSU image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Find marker in OTSU'ed image
        return self.find_marker_in_thresholded_image(image)

    def find_marker_in_thresholded_image(self, image):
        """
        Find marker in image which has already been thresholded.

        :param image: Thresholded image
        :return: Marker contour
        """

        # Find contours
        contours, _ = cv2.findContours(image.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        if len(contours) == 0:
            return None

        # Find marker from contours
        for contour in contours:

            # Verify contour
            if self.verify_contour(contour, image):
                #image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
                #cv2.drawContours(image2, [contour], 0, (255, 255, 0), 1)
                #cv2.imshow('Contours', image2)
                #cv2.waitKey(0)
                return contour

        # No marker found
        return None

    def verify_contour(self, contour, image):
        """
        Algorithm: XXX
        """

        image_height, image_width = image.shape[:2]

        # Check contour arc length
        arclength = cv2.arcLength(contour, self.closed)

        min_contour_length = max(image_width, image_height) * self.min_arclength
        max_contour_length = max(image_width, image_height) * self.max_arclength

        if arclength < min_contour_length:
            return False

        if arclength > max_contour_length:
            return False

        # Check contour area
        area = cv2.contourArea(contour, True)

        orientation = -1 if area < 0 else 1

        area = abs(area)

        min_contour_area = image_width * image_height * self.min_area
        max_contour_area = image_width * image_height * self.max_area

        if area < min_contour_area:
            return False

        if area > max_contour_area:
            return False

        # Simplify contour
        approxed_contour = contour_util.simplify_contour(contour)

        #contour_util.draw_contour(image.copy(), contour=approxed_contour, points_color=(0, 255, 0))
        #cv2.waitKey(0)

        # Check number of lines compared to marker
        if len(approxed_contour) < len(self.marker_contour):
            return False

        if len(approxed_contour) > len(self.marker_contour) * 2:
            return False

        # Go through source points
        for start_index in range(0, self.marker_length):

            # Match points in contour with marker
            matched_contour = self.match_contour(approxed_contour, start_index, 1 if orientation == self.marker_orientation else -1, contour_arc_length=arclength, image=None)

            # Check match
            if matched_contour is not None:
                #image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
                #cv2.drawContours(image2, [matched_contour], 0, (255, 0, 255), 1)
                #cv2.imshow('Contours 2', image2)
                #cv2.waitKey(0)
                return True

        return False

    def match_contour(self, contour, marker_start_offset, direction, contour_arc_length=None, image=None):

        # Prepare constants
        min_threshold = 0.1
        orientation = 0 if direction == -1 else 1

        contour_length = len(contour)
        marker_offset = marker_start_offset

        # Calculate arc length
        if contour_arc_length is None:
            contour_arc_length = cv2.arcLength(contour, True)

        # Reset indices
        contour_idx1 = contour_length - 1
        contour_idx2 = 0
        contour_idx3 = 1

        # Reset drifting
        contour_idx_drifting = 0

        # Try matching
        matched_points = []

        while True:

            # Check if match is impossible by now
            if contour_idx2 >= contour_length:
                return None

            if contour_idx_drifting > 4 or contour_idx3 == contour_idx1:
                return None

            # Debug
            if image is not None:
                draw_image = contour_util.draw_line(image=image, points=[contour[contour_idx1 % contour_length][0], contour[contour_idx2 % contour_length][0]], line_color=(0, 0, 255), name="Progress")
                draw_image = contour_util.draw_line(scaled_image=draw_image, points=[contour[contour_idx2 % contour_length][0], contour[contour_idx3 % contour_length][0]], line_color=(128, 128, 255), name="Progress")

                draw_image = contour_util.draw_contour(scaled_image=draw_image, contour=self.marker_contour, contour_color=(255, 0, 0), name="Progress")

                draw_image = contour_util.draw_line(scaled_image=draw_image, points=[self.marker_contour[(marker_offset + (direction*-1) + self.marker_length) % self.marker_length][0], self.marker_contour[marker_offset][0]], line_color=(0, 0, 255), name="Progress")
                draw_image = contour_util.draw_line(scaled_image=draw_image, points=[self.marker_contour[marker_offset][0], self.marker_contour[(marker_offset + direction + self.marker_length) % self.marker_length][0]], line_color=(128, 128, 255), name="Progress")

                cv2.waitKey(0)

            # Calculate contour line length
            contour_line_length = misc_math.line_length(contour[contour_idx2 % contour_length][0], contour[contour_idx3 % contour_length][0])

            # Get line unit lengths
            marker_unit_distance = max(self.marker_distance_map[orientation][marker_offset][1], min_threshold)
            contour_unit_distance = max(contour_line_length / contour_arc_length, min_threshold)

            distance_ratio = max(contour_unit_distance, marker_unit_distance) / min(contour_unit_distance, marker_unit_distance)

            # Check line length
            #print("%i, %i: Distance: %f vs %s = %f" % (marker_offset, contour_idx3, contour_unit_distance, marker_unit_distance, distance_ratio))
            if distance_ratio - 1.0 <= self.distance_tolerance:

                # Calculate angles
                marker_angle = self.marker_angle_map[orientation][marker_offset]
                contour_angle = self.contour_angle(contour, contour_idx1 % contour_length, contour_idx2 % contour_length, contour_idx3 % contour_length)

                delta_angle = math.atan2(math.sin(marker_angle - contour_angle), math.cos(marker_angle - contour_angle))

                # Check angle
                #print("%i, %i: Angle: %f vs %s = %f" % (marker_offset, contour_idx3, contour_angle, marker_angle, abs(delta_angle)))
                if abs(delta_angle) <= self.angle_tolerance:

                    # Build contour
                    matched_points.append(contour[contour_idx2 % contour_length])

                    # Next point in marker
                    marker_offset = (marker_offset + direction + self.marker_length) % self.marker_length

                    if marker_offset == marker_start_offset:
                        return np.int32(matched_points).reshape(-1, 1, 2)

                    # Next point in contour
                    contour_idx1 = contour_idx2
                    contour_idx2 = contour_idx3
                    contour_idx3 += 1

                    continue

            # Try next contour offset
            if contour_idx1 < contour_idx2 - 1:
                contour_idx1 += 1
            elif contour_idx2 < contour_idx3 - 1:
                contour_idx2 += 1
            else:
                contour_idx3 += 1
                contour_idx_drifting += 1




    def verify_fine_grained_lines(self, contour, index_map, distance_map, start_index):
        """
        Verifies that all lines not covered by index map points lies within range of lines spanned by points in
        distance map.

        :param contour: Contour
        :param index_map: Index map
        :param distance_map: Distance map
        :param start_index: Index at which to start
        :return: Whether all lines not covered by index map points lies on lines spanned by points in distance map
        """

        # Check all points not covered by index map
        contour_length = len(contour)
        index_map_length = len(index_map)

        for i in range(0, index_map_length):

            # Calculate delta index
            idx1 = index_map[i]
            idx2 = index_map[(i + 1) % index_map_length]

            delta_index = abs(idx1 - idx2)

            # Check if there are any points between
            if delta_index == 1 or delta_index == contour_length - 1:
                continue

            # Calculate total length of lines
            lines_distance = 0.0

            idx = idx1
            prev_idx = idx

            while idx != idx2:
                idx = (idx + 1) % contour_length

                # Calculate line length
                lines_distance += misc_math.line_length(contour[idx][0], contour[prev_idx][0])
                #print("Line distance: %f" % misc_math.line_length(contour[idx][0], contour[prev_idx][0]))

                prev_idx = idx

            # Check distances
            distance = distance_map[i][0]
            distance_ratio = max(distance, lines_distance) / min(distance, lines_distance)

            #print("Distance: %f vs %f = ratio: %f" % (lines_distance, distance_map[i][0], distance_ratio))
            if distance_ratio - 1.0 > self.spike_tolerance:
                return False

        # Success
        return True

    def distance_map_for_contour(self, contour, direction):
        """
        Calculates the distance map of each point of the contour in range [0, arc length] and [0, 1].

        :param contour: Contour
        :param direction: Direction
        :return: Distance map in form [(distance, normalized distance), ...]
        """

        contour_length = len(contour)
        contour_arclength = cv2.arcLength(contour, self.closed)

        offset = -1 if direction == -1 else 0

        # Calculate distance offset
        distance_map = []

        for i in range(0, contour_length):
            idx1 = ((i + offset    ) + contour_length) % contour_length
            idx2 = ((i + offset + 1) + contour_length) % contour_length

            line_length = misc_math.line_length(contour[idx1][0], contour[idx2][0])

            distance_map.append(line_length)

        # Return distances including unit distances
        return [(distance, distance / contour_arclength) for distance in distance_map]

    def angle_map_for_contour(self, contour, direction):
        """
        Calculates the angle map of each point of the contour.

        :param contour: Contour
        :param direction: Direction
        :return: Angle map
        """

        contour_length = len(contour)

        offset = 0  #-1 if direction == -1 else 0

        # Compute angle map
        angle_map = []

        for i in range(0, contour_length):
            idx1 = ((i + offset - direction) + contour_length) % contour_length
            idx2 = ((i + offset            ) + contour_length) % contour_length
            idx3 = ((i + offset + direction) + contour_length) % contour_length

            angle = self.contour_angle(contour, idx1, idx2, idx3)
            angle_map.append(angle)

        return angle_map

    def contour_angle(self, contour, idx1, idx2, idx3):
        return self.points_angle(contour[idx1][0], contour[idx2][0], contour[idx3][0])

    def points_angle(self, pt1, pt2, pt3):
        v1 = [pt1[0] - pt2[0], pt1[1] - pt2[1]]
        v2 = [pt3[0] - pt2[0], pt3[1] - pt2[1]]

        angle = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])

        return angle % (math.pi * 2.0)
