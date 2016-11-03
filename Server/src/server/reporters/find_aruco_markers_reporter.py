import cv2
from board.board_descriptor import BoardDescriptor
from server.reporters.reporter import Reporter
from util import aruco_util


class FindArUcoMarkersReporter(Reporter):

    def __init__(self, board_area, marker_size, reporter_id, callback_function):
        """
        :param board_area: Board area
        :param marker_size: Marker size
        """
        super(FindArUcoMarkersReporter, self).__init__(reporter_id, callback_function)

        self.board_area = board_area
        self.marker_size = marker_size
        self.dictionary_size = 100
        self.dictionary = cv2.aruco.getPredefinedDictionary(aruco_util.dictionary_from_parameters(self.marker_size, self.dictionary_size))

    def update(self):

        # Get area image
        image = self.board_area.area_image(snapshot_size=BoardDescriptor.SnapshotSize.MEDIUM)
        if image is None:
            return

        # Find markers
        res = cv2.aruco.detectMarkers(image, self.dictionary)

        # Extract ArUco markers
        markers = []
        for i1 in range(0, len(res[0])):
            for i2 in range(0, len(res[0][i1])):
                markers.append(aruco_util.aruco_result_to_marker_result(res, i1, i2, image))

        #if globals.get_state().debug:
            #print("%i: Markers found: %i" % (self.reporter_id, len(markers)))
            #cv2.imwrite("area.png", self.board_area.area_image())

        self.callback_function(markers)
        self.stop()
