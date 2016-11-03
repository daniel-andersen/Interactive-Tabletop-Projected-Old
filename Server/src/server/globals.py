from threading import RLock
from board.tile_brick_detector import TileBrickDetector


class GlobalState:

    debug = False

    board_not_recognized_notify_delay = 10.0

    """
    Reporters
    """

    _reporters = {}
    reporters_lock = RLock()

    def get_reporters(self):
        with self.reporters_lock:
            return self._reporters

    def get_reporter(self, reporter_id):
        with self.reporters_lock:
            return self._reporters[reporter_id]

    def set_reporters(self, reporters):
        with self.reporters_lock:
            self._reporters = reporters

    def set_reporter(self, reporter_id, reporter):
        with self.reporters_lock:
            self._reporters[reporter_id] = reporter

    def remove_reporter(self, reporter_id):
        with self.reporters_lock:
            del self._reporters[reporter_id]

    """
    Markers
    """

    _markers = {}
    markers_lock = RLock()

    def get_markers(self):
        with self.markers_lock:
            return self._markers

    def get_marker(self, marker_id):
        with self.markers_lock:
            return self._markers[marker_id]

    def set_markers(self, markers):
        with self.markers_lock:
            self._markers = markers

    def set_marker(self, marker_id, marker):
        with self.markers_lock:
            self._markers[marker_id] = marker

    def remove_marker(self, marker_id):
        with self.markers_lock:
            del self._markers[marker_id]

    """
    Board areas
    """

    _board_areas = {}
    board_areas_lock = RLock()

    def get_board_areas(self):
        with self.board_areas_lock:
            return self._board_areas

    def get_board_area(self, board_area_id):
        with self.board_areas_lock:
            return self._board_areas[board_area_id]

    def set_board_areas(self, board_areas):
        with self.board_areas_lock:
            self._board_areas = board_areas

    def set_board_area(self, board_area_id, board_area):
        with self.board_areas_lock:
            self._board_areas[board_area_id] = board_area

    def remove_board_area(self, board_area_id):
        with self.board_areas_lock:
            del self._board_areas[board_area_id]

    """
    Camera
    """

    _camera = None
    camera_lock = RLock()

    def get_camera(self):
        with self.camera_lock:
            return self._camera

    def set_camera(self, camera):
        with self.camera_lock:
            self._camera = camera

    """
    Board descriptor
    """

    _board_descriptor = None
    board_descriptor_lock = RLock()

    def get_board_descriptor(self):
        with self.board_descriptor_lock:
            return self._board_descriptor

    def set_board_descriptor(self, board_descriptor):
        with self.board_descriptor_lock:
            self._board_descriptor = board_descriptor

    """
    Board recognizer
    """

    _board_recognizer = None
    board_recognizer_lock = RLock()

    def get_board_recognizer(self):
        with self.board_recognizer_lock:
            return self._board_recognizer

    def set_board_recognizer(self, board_recognizer):
        with self.board_recognizer_lock:
            self._board_recognizer = board_recognizer

    """
    Brick detector
    """

    _brick_detector = TileBrickDetector()
    brick_detector_lock = RLock()

    def get_brick_detector(self):
        with self.brick_detector_lock:
            return self._brick_detector

    def set_brick_detector(self, brick_detector):
        with self.brick_detector_lock:
            self._brick_detector = brick_detector


_global_state_instance = GlobalState()


def get_state():
    return _global_state_instance
