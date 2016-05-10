import cv2
import math
import itertools
from util import misc_math


class CustomMarker(object):

    def __init__(self, contour, distance_tolerance=0.15, angle_tolerance=0.15, fine_grained=True, spike_tolerance=0.025,
                 approx_multiplier=0.02, closed=True, min_arclength=0.1, max_arclength=100.0,
                 min_area=0.02, max_area=1.0):
        """
        :param contour: Simplified marker contour (containing fx. only corners)
        :param distance_tolerance: Distance tolerance in multitudes of length
        :param angle_tolerance: Angle tolerance in radians in range [0..pi]
        :param fine_grained: If true, verify that all points lies on contour edge
        :param spike_tolerance: Spike distance tolerance for fine-grained lines
        :param approx_multiplier: Multiplier to use when approximating contour
        :param closed: Indicated wheter the contour is closed or not
        :param min_arclength: Minimum arc length scaled in multitudes of max(image width, image height)
        :param max_arclength: Maximum arc length scaled in multitudes of max(image width, image height)
        :param min_area: Minimum area scaled in percentage [0, 1] of image size
        :param max_area: Maximum area scaled in percentage [0, 1] of image size
        """
        self.marker_contour = contour
        self.distance_tolerance = distance_tolerance
        self.angle_tolerance = angle_tolerance
        self.fine_grained = fine_grained
        self.spike_tolerance = spike_tolerance
        self.approx_multiplier = approx_multiplier
        self.closed = closed
        self.min_arclength = min_arclength
        self.max_arclength = max_arclength
        self.min_area = min_area
        self.max_area = max_area

        self.marker_arclength = cv2.arcLength(self.marker_contour, self.closed)
        self.marker_distance_map = self.distance_map_for_contour(self.marker_contour)
        self.marker_angle_map = self.angle_map_for_contour(self.marker_contour)

    def find_marker_in_thresholded_image(self, image):
        """
        Find marker in image which has already been thresholded.

        :param image: Thresholded image
        :return: Marker contour
        """

        #cv2.imshow("Contours", image)
        #cv2.waitKey(0)

        # Find contours
        contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            return None

        # Find marker from contours
        for contour in contours:

            # Verify contour
            if self.verify_contour(contour, image):
                print("SUCCESS!")
                image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
                cv2.drawContours(image2, [contour], 0, (255, 255, 0), 1)
                cv2.imshow('Contours', image2)
                cv2.waitKey(0)
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
        approxed_contour = cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * self.approx_multiplier, True)

        #image2 = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
        #cv2.drawContours(image2, [approxed_contour], 0, (255, 0, 255), 1)
        #cv2.imshow('Contours', image2)
        #cv2.waitKey(0)

        # Check number of lines compared to marker
        #print("Num lines marker: %i" % len(self.marker_contour))
        #print("Num lines contour: %i" % len(approxed_contour))

        if len(approxed_contour) < len(self.marker_contour):
            return False

        if len(approxed_contour) > len(self.marker_contour) * 2:
            return False

        #for p in approxed_contour:
        #    print("C: %f, %f" % (p[0][0], p[0][1]))
        #for p in self.marker_contour:
        #    print("M: %f, %f" % (p[0][0], p[0][1]))

        # Go through all combinations of points in contour
        marker_length = len(self.marker_contour)
        contour_length = len(approxed_contour)

        for indices in itertools.combinations(range(0, contour_length), marker_length):
            #print("Index map: %s" % list(indices))
            indices_list = list(indices)

            # Try all "rotations" of this index map
            angle_map = None
            distance_map = None

            for start_index in range(0, marker_length):

                # Compute angle map
                if angle_map is None:
                    angle_map = self.angle_map_for_contour(approxed_contour, indices_list, orientation)

                # Verify angle map
                if not self.verify_angle_map(angle_map, start_index):
                    continue

                # Compute distance map
                if distance_map is None:
                    distance_map = self.distance_map_for_contour(approxed_contour, indices_list)

                # Verify distance map
                if not self.verify_distance_map(distance_map, start_index):
                    continue

                # Fine grained checks
                if self.fine_grained:

                    # Check all lines not covered by index map
                    if not self.verify_fine_grained_lines(approxed_contour, indices_list, distance_map, start_index):
                        continue

                # Success
                return True

        return False

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

    def verify_distance_map(self, distance_map, start_index=0):
        """
        Verifies the distance map.

        :param distance_map: Distance map
        :param start_index: Index at which to start
        :return: Whether the distance map matches the markers distance map
        """

        min_threshold = 0.1

        distance_map_length = len(distance_map)

        #print("Marker distance map: %s" % self.marker_distance_map)
        #print("Contour distance map: %s" % distance_map)

        # Check all lines
        for i in range(0, len(distance_map)):

            # Calculate distance ratio
            marker_unit_distance = max(self.marker_distance_map[i][1], min_threshold)
            contour_unit_distance = max(distance_map[(i + start_index) % distance_map_length][1], min_threshold)

            distance_ratio = max(contour_unit_distance, marker_unit_distance) / min(contour_unit_distance, marker_unit_distance)
            #print("%i: Distance: %f vs %s = ratio: %f" % (i, contour_unit_distance, marker_unit_distance, distance_ratio))

            # Check validity
            if distance_ratio - 1.0 > self.distance_tolerance:
                return False

        return True

    def verify_angle_map(self, angle_map, start_index=0):
        """
        Verifies the angle map.

        :param angle_map: Angle map
        :param start_index: Index at which to start
        :return: Whether the angle map matches the markers angle map
        """

        #print("Marker angles: %s" % self.marker_angle_map)
        #print("Contour angles: %s" % angle_map)

        angle_map_length = len(angle_map)

        # Verify angle map
        for i in range(0, len(self.marker_angle_map)):

            # Calculate angle difference
            marker_angle = self.marker_angle_map[i]
            contour_angle = angle_map[(i + start_index) % angle_map_length]

            delta_angle = math.atan2(math.sin(marker_angle - contour_angle), math.cos(marker_angle - contour_angle))

            #print("Angles: %f vs %f = %f deg" % (marker_angle, contour_angle, delta_angle * 180.0 / math.pi))

            # Check if valid
            if abs(delta_angle) > self.angle_tolerance:
                #print("--------")
                return False

        return True

    def distance_map_for_contour(self, contour, index_map=None):
        """
        Calculates the distance map of each point of the contour in range [0, arc length] and [0, 1].

        :param contour: Contour
        :param index_map: Index map to use
        :return: Distance map in form [(distance, normalized distance), ...]
        """

        # Use standard index map if none given
        if index_map is None:
            index_map = [i for i in range(0, len(contour))]

        index_map_length = len(index_map)

        # Calculate distance offset
        distance_map = []
        arclength = 0.0

        for i in range(0, index_map_length):
            idx1 = index_map[i]
            idx2 = index_map[(i + 1) % index_map_length]

            line_length = misc_math.line_length(contour[idx1][0], contour[idx2][0])

            arclength += line_length

            distance_map.append(line_length)

        # Return distances including unit distances
        return [(distance, distance / arclength) for distance in distance_map]

    def angle_map_for_contour(self, contour, index_map=None, orientation=None):
        """
        Calculates the angle map of each point of the contour.

        :param contour: Contour
        :param index_map: If provided, only use the given indices
        :param orientation: Orientation (1 = counter-clockwise, -1 = clockwise). Is calculated if none is given
        :return: Angle map
        """

        # Calculate orientation if none given
        if orientation is None:
            area = cv2.contourArea(contour, oriented=True)
            orientation = -1 if area < 0 else 1

        # Use standard index map if none given
        if index_map is None:
            index_map = [i for i in range(0, len(contour))]

        index_map_length = len(index_map)

        # Calculate index map orientation
        #print("Orientation: %i" % orientation)
        #print("Angle index map: %s" % index_map)

        # Compute angle map
        angle_map = []

        for i in range(0, index_map_length):
            idx1 = (index_map_length + i - 1) % index_map_length
            idx2 = (index_map_length + i    ) % index_map_length
            idx3 = (index_map_length + i + 1) % index_map_length

            pt1 = contour[index_map[idx1]][0]
            pt2 = contour[index_map[idx2]][0]
            pt3 = contour[index_map[idx3]][0]

            v1 = [pt1[0] - pt2[0], pt1[1] - pt2[1]]
            v2 = [pt3[0] - pt2[0], pt3[1] - pt2[1]]
            #print("%s - %s - %s" % (pt1, pt2, pt3))

            angle = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])
            if orientation == 1:
                angle = (math.pi * 2.0) - angle

            angle = angle % (math.pi*2.0)
            angle_map.append(angle)

        return angle_map
