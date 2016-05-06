import cv2
import numpy as np
import math
from util import misc_math


class CustomMarker(object):

    def __init__(self, contour, similarity_threshold=0.15, fine_grained=False, approx_multiplier=0.02, closed=True, min_arclength=0.1, max_arclength=0.2):
        """
        :param contour: Simplified marker contour (containing fx. only corners)
        :param similarity_threshold: Similarity threshold in range [0..1]
        :param fine_grained: Indicates whether to check against all points of source contour (NOT IMPLEMENTED)
        :param approx_multiplier: Multiplier to use when approximating contour
        :param closed: Indicated wheter the contour is closed or not
        :param min_arclength: Minimum arc length scaled in percent of max(image width, image height)
        :param max_arclength: Maximum arc length scaled in percent of max(image width, image height)
        """
        self.marker_contour = contour
        self.similarity_threshold = similarity_threshold
        self.fine_grained = fine_grained
        self.approx_multiplier = approx_multiplier
        self.closed = closed
        self.min_arclength = min_arclength
        self.max_arclength = max_arclength

        self.marker_arclength = cv2.arcLength(self.marker_contour, self.closed)
        self.marker_distance_map = self.distance_map_for_contour(self.marker_contour, start_index=0, direction=1, arclength=self.marker_arclength)

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

        #cv2.imshow("Contours", image)
        #cv2.waitKey(0)

        # Find contours
        contours, hierarchy = \
            cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            return None

        # Find marker from contours
        for contour in contours:
            if self.is_contour_correct(contour, image):
                return contour

        # No marker found
        return None

    def is_contour_correct(self, contour, image):
        """
        Algorithm: First project points (approxed contour points ~= corners) onto marker contour. If fine-grained,
        follow source contour and for each point, check if it matches marker.

        1) Find approxed contour.
        2) Try to project source contour points (corners) onto marker contour points.
        2a) For each marker point, loop clockwise through source contour points and project onto marker contour
            by rotating source contour in angle defined by the first marker points.
        2b) Do the same counter-clockwise.
        2c) If not fine-grained or matching failed, return result.
        3) Follow source contour from start to end.
        3a) Start by placing a circle around marker point with radius matching choosen similarity threshold.
        3b) Follow source contour in rotation found previously (2).
        3c) When point is outside marker circle, move circle on marker contour by radius/2 points.
        3d) If point is outside new circle, fail.
        3e) Continue until reaching start.
        """

        # Check arc length
        # TODO!

        # Approximate contour
        approxed_contour = cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * self.approx_multiplier, True)

        # Find scale ratio
        arclength = cv2.arcLength(approxed_contour, self.closed)
        arclength_ratio = arclength / self.marker_arclength

        print("Num lines marker: %i" % len(self.marker_contour))
        print("Num lines contour: %i" % len(approxed_contour))
        print("Arclength ratio: %f" % arclength_ratio)

        # Match points
        count = 0
        #self.match_points(approxed_contour, 2, -1, arclength)
        for i in range(0, len(approxed_contour)):
            for direction in range(-1, 2, 2):
                match = self.match_points(approxed_contour, i, direction, arclength)
                print("Match %i, %i: %s" % (i, direction, match))
                if match:
                    count += 1

        print("Result: %i matches" % count)

        image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
        cv2.drawContours(image2, [contour], 0, (255, 255, 255), 1)
        cv2.drawContours(image2, [approxed_contour], 0, (255, 0, 255), 1)
        cv2.imshow('Contours', image2)
        cv2.waitKey(0)

        return False

    def match_points(self, contour, start_index, direction, arclength):

        # Calculate distance mapping
        distance_map = self.distance_map_for_contour(contour, start_index, direction, arclength)

        # Verify that contour distance map is a subset of the marker's distance map
        if not self.verify_distance_map(distance_map):
            return False

        print("Marker distance map: %s" % self.marker_distance_map)
        print("Contour distance map: %s" % distance_map)

        # Verify points
        return self.verify_points(contour, distance_map, start_index, direction)

    def verify_points(self, contour, distance_map, start_index, direction):
        for p in contour:
            print("C: %f, %f" % (p[0][0], p[0][1]))
        for p in self.marker_contour:
            print("M: %f, %f" % (p[0][0], p[0][1]))

        contour_length = len(contour)
        marker_length = len(self.marker_contour)

        # Start at first marker point
        start_point = self.marker_contour[marker_length - 1][0]
        current_point = self.marker_contour[0][0]

        contour_index = start_index
        distance_map_index = 1

        # Calculate starting angle
        marker_angle = math.atan2(self.marker_contour[1][0][1] - self.marker_contour[0][0][1],
                                  self.marker_contour[1][0][0] - self.marker_contour[0][0][0])

        #contour_start_angle = self.angle_with_reference_point(contour, start_index, start_point, reverse=True)
        contour_start_angle = math.atan2(contour[(start_index + direction + contour_length) % contour_length][0][1] - contour[start_index][0][1],
                                         contour[(start_index + direction + contour_length) % contour_length][0][0] - contour[start_index][0][0])

        current_angle = marker_angle + contour_start_angle

        # Loop through all points in marker
        for marker_index in range(0, marker_length):

            print("-----------------------------------------")

            # Match all contour points within this marker line
            while distance_map[distance_map_index] <= self.marker_distance_map[(marker_index + 1) % marker_length] or marker_index == marker_length - 1:

                # Project point onto line

                # Calculate new contour angle
                #contour_angle = self.angle_with_reference_point(contour, contour_index, start_point, reverse=True)
                #current_angle += contour_angle

                # Calculate line distance
                distance = (distance_map[distance_map_index] - distance_map[distance_map_index - 1]) * self.marker_arclength

                # Calculate movement offset
                prev_contour_index = (contour_index + contour_length - 1) % contour_length

                line_length = misc_math.line_length(contour[prev_contour_index][0], contour[contour_index][0])

                move_offset = [(contour[prev_contour_index][0][0] - contour[contour_index][0][0]) * distance / line_length,
                               (contour[prev_contour_index][0][1] - contour[contour_index][0][1]) * distance / line_length]

                print(move_offset)

                # Move point on contour
                c = math.cos(current_angle)
                s = math.sin(current_angle)

                current_point = [current_point[0] + (move_offset[0] * c - move_offset[1] * s),
                                 current_point[0] + (move_offset[0] * s + move_offset[1] * c)]

                # Calculate marker angle
                marker_point = self.marker_contour[marker_index][0]
                marker_angle = math.atan2(self.marker_contour[(marker_index + 1) % marker_length][0][1] - self.marker_contour[marker_index][0][1],
                                          self.marker_contour[(marker_index + 1) % marker_length][0][0] - self.marker_contour[marker_index][0][0])

                print("Angle: %f" % current_angle)
                print("Marker angle: %f" % marker_angle)

                # Calculate marker comparison point
                distance_from_marker = (distance_map[distance_map_index] - self.marker_distance_map[marker_index]) * self.marker_arclength
                comparison_point = [marker_point[0] + (math.cos(marker_angle) * distance_from_marker),
                                    marker_point[1] + (math.sin(marker_angle) * distance_from_marker)]

                print("%i, %i: %f, %f --> %f, %f vs %f, %f" % (marker_index, contour_index, distance, distance_from_marker, current_point[0], current_point[1], comparison_point[0], comparison_point[1]))

                # Compute similarity radius
                similarity_radius = max(5.0, max(distance_from_marker, distance) * self.similarity_threshold)
                print("Similarity radius: %f" % similarity_radius)

                # Compare points
                points_distance = misc_math.line_length(current_point, comparison_point)
                if points_distance > similarity_radius:
                    print("No luck! %f vs %f" % (points_distance, similarity_radius))
                    return False

                # Next contour index
                contour_index = (contour_index + contour_length + direction) % contour_length
                distance_map_index += 1

                # Check if done
                if contour_index == start_index:
                    return True

            start_point = current_point

        return True

    def verify_distance_map(self, distance_map):
        """
        Verifies that the given distance map is a subset of the marker distance map.

        :param distance_map: Distance map
        """
        marker_distance_map_length = len(self.marker_distance_map)
        distance_map_length = len(distance_map)

        i = 0
        j = 0

        while i < marker_distance_map_length and j < distance_map_length:

            # Compute line distances of adjacent lines
            line_distance_prev = (self.marker_distance_map[i] - self.marker_distance_map[i - 1]) if i > 0 else 1.0 - self.marker_distance_map[marker_distance_map_length - 1]
            line_distance_next = (self.marker_distance_map[i + 1] - self.marker_distance_map[i]) if i < marker_distance_map_length - 1 else 1.0 - self.marker_distance_map[i]

            # Compute max deviation based on distance of adjacent lines
            max_line_distance = max(line_distance_prev, line_distance_next)
            max_deviation = max_line_distance * self.similarity_threshold * 0.5

            # Compute delta difference from marker to contour
            delta_difference = self.marker_distance_map[i] - distance_map[j]

            # Check distance and move indices
            if abs(delta_difference) < max_deviation:  # Both close
                i += 1
                j += 1
            elif delta_difference > max_deviation:  # Source contour behind
                j += 1
            else:
                return False

        # Distance map valid
        return True

    def distance_map_for_contour(self, contour, start_index, direction, arclength):
        """
        Calculates the distance map of each point of the contour in range [0, 1].

        :param contour: Contour
        :param start_index: Start index
        :param direction: Direction
        :param arclength: Arc length of contour (for optimizations)
        :return: Distance map
        """
        contour_length = len(contour)

        # Calculate distance offset
        distance_offsets = [0.0]
        for i in range(0, contour_length):
            idx1 = (start_index + contour_length + ( i      * direction)) % contour_length
            idx2 = (start_index + contour_length + ((i + 1) * direction)) % contour_length

            line_length = misc_math.line_length(contour[idx1][0], contour[idx2][0])

            distance = distance_offsets[i] + line_length
            distance_offsets.append(distance)

        # Normalize
        return [distance / arclength for distance in distance_offsets]

    def angle(self, contour, index, reverse=False):
        length = len(contour)
        pt1 = contour[(index + length - 1) % length][0]
        pt2 = contour[index % length][0]
        pt3 = contour[(index + 1) % length][0]

        v1 = [pt1[0] - pt2[0], pt1[1] - pt2[1]]
        v2 = [pt3[0] - pt2[0], pt3[1] - pt2[1]]

        angle = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])

        return angle if not reverse else (math.pi - angle)

    def angle_with_reference_point(self, contour, index, pt1, reverse=False):
        length = len(contour)
        pt2 = contour[index % length][0]
        pt3 = contour[(index + 1) % length][0]

        v1 = [pt1[0] - pt2[0], pt1[1] - pt2[1]]
        v2 = [pt3[0] - pt2[0], pt3[1] - pt2[1]]

        angle = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])
        print("Angle between %s and %s = %f" % (v1, v2, angle if not reverse else (math.pi - angle)))

        return angle if not reverse else (math.pi - angle)
