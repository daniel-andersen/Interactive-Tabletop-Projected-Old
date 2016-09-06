from __future__ import with_statement
import sys, traceback
import json
import time
import cv2
import globals
import base64
import numpy as np
from random import randint
from threading import Thread
from threading import Lock
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from util import misc_util
from board.markers.marker_util import *
from board.board_descriptor import BoardDescriptor
from board.board_areas.board_area import BoardArea
from board.board_areas.tiled_board_area import TiledBoardArea
from board.markers.image_marker import ImageMarker
from board.markers.haar_classifier_marker import HaarClassifierMarker
from board.markers.shape_marker import ShapeMarker
from reporters.tiled_brick_position_reporter import TiledBrickPositionReporter
from reporters.tiled_brick_moved_reporters import TiledBrickMovedToAnyOfPositionsReporter
from reporters.tiled_brick_moved_reporters import TiledBrickMovedToPositionReporter
from reporters.find_marker_reporter import FindMarkerReporter
from reporters.find_markers_reporter import FindMarkersReporter

if misc_util.module_exists("picamera"):
    print("Using Raspberry Pi camera")
    from camera_pi import Camera
else:
    print("Using desktop camera")
    from camera_desktop import Camera


class Server(WebSocket):
    """
    Server which communicates with the client library.
    """
    busy_lock = Lock()

    reporters = {}
    reporter_thread = None

    markers = {}

    board_areas = {}

    def handleMessage(self):
        """
        Handles incoming message.
        """
        try:
            print("Got message: %s" % self.data)
            json_dict = json.loads(self.data)

            if "action" in json_dict:
                action = json_dict["action"]

                with self.busy_lock:
                    result = self.handle_action(action, json_dict["payload"])

                if result is not None:
                    self.send_message(result[0], action, result[1])

        except Exception, e:
            print("Exception in handleMessage: %s" % str(e))
            traceback.print_exc(file=sys.stdout)

    def handle_action(self, action, payload):
        if action == "enableDebug":
            return self.enable_debug()
        if action == "reset":
            return self.reset(payload)
        if action == "resetReporters":
            return self.reset_reporters()
        if action == "resetReporter":
            return self.reset_reporter(payload)
        if action == "takeScreenshot":
            return self.take_screenshot(payload)
        if action == "initializeBoard":
            return self.initialize_board(payload)
        if action == "initializeBoardArea":
            return self.initialize_board_area(payload)
        if action == "initializeTiledBoardArea":
            return self.initialize_tiled_board_area(payload)
        if action == "removeBoardArea":
            return self.remove_board_area(payload)
        if action == "removeBoardAreas":
            return self.remove_board_areas()
        if action == "removeMarker":
            return self.remove_marker(payload)
        if action == "removeMarkers":
            return self.remove_markers()
        if action == "reportBackWhenBrickFoundAtAnyOfPositions":
            return self.report_back_when_brick_found_at_any_of_positions(payload)
        if action == "reportBackWhenBrickMovedToAnyOfPositions":
            return self.report_back_when_brick_moved_to_any_of_positions(payload)
        if action == "reportBackWhenBrickMovedToPosition":
            return self.report_back_when_brick_moved_to_position(payload)
        if action == "requestBrickPosition":
            return self.request_brick_position(payload)
        if action == "initializeShapeMarker":
            return self.initialize_shape_marker(payload)
        if action == "initializeImageMarker":
            return self.initialize_image_marker(payload)
        if action == "initializeHaarClassifierMarker":
            return self.initialize_haar_classifier_marker(payload)
        if action == "requestMarkers":
            return self.request_markers(payload)
        if action == "reportBackWhenMarkerFound":
            return self.report_back_when_marker_found(payload)

    def initialize_video(self, resolution):
        if globals.camera is not None:
            return

        globals.camera = Camera()
        globals.camera.start(resolution)

    def initialize_reporter_thread(self):
        if self.reporter_thread is None:
            self.reporter_thread = Thread(target=self.reporter_run, args=())
            self.reporter_thread.daemon = True
            self.reporter_thread.start()

    def reset(self, payload):
        """
        Resets the board.

        cameraResolution: (Optional) Camera resolution in [width, height]. Default: [640, 480].
        """
        resolution = payload["resolution"] if "resolution" in payload else [640, 480]

        globals.board_descriptor = BoardDescriptor()
        self.reset_board_descriptor()

        self.initialize_reporter_thread()
        self.reset_reporters()
        self.remove_board_areas()
        self.remove_markers()

        self.initialize_video(resolution)

        return "OK", {}

    def reset_board_descriptor(self):
        """
        Resets the board descriptor with standard values.
        """
        globals.board_descriptor.board_size = [1280, 800]
        globals.board_descriptor.border_percentage_size = [0.0, 0.0]

    def enable_debug(self):
        """
        Enables debug output.
        """
        globals.debug = True

        return "OK", {}

    def take_screenshot(self, payload):
        """
        Take a screenshot and saves it to disk.

        filename: (Optional) Screenshot filename
        """
        image = globals.camera.read()
        if image is not None:
            filename = "debug/board_{0}.png".format(time.strftime("%Y-%m-%d-%H%M%S"))\
                if "filename" not in payload else payload["filename"]
            cv2.imwrite(filename, image)
            return "OK", {}
        else:
            return "CAMERA_NOT_READY", {}

    def initialize_board(self, payload):
        """
        Initializes board with given parameters.

        borderPctX: (Optional) Border width in percentage of board size.
        borderPctY: (Optional) Border height in percentage of board size.
        cornerMarker: (Optional) Corner marker
        """
        globals.board_descriptor = BoardDescriptor()
        self.reset_board_descriptor()

        globals.board_descriptor.border_percentage_size = [
            payload["borderPctX"] if "borderPctX" in payload else 0.0,
            payload["borderPctY"] if "borderPctY" in payload else 0.0
        ]
        globals.board_descriptor.corner_marker = create_marker_from_name(payload["cornerMarker"], marker_id=-1) if "cornerMarker" in payload else DefaultMarker(marker_id=-1)

        return "OK", {}

    def initialize_board_area(self, payload):
        """
        Initializes board area with given parameters.

        id: (Optional) Area id
        x1: X1 in percentage of board size.
        y1: Y1 in percentage of board size.
        x2: X2 in percentage of board size.
        y2: Y2 in percentage of board size.
        """
        board_area = BoardArea(
            payload["id"] if "id" in payload else None,
            [payload["x1"], payload["y1"], payload["x2"], payload["y2"]],
            globals.board_descriptor
        )
        self.board_areas[board_area.area_id] = board_area

        return "OK", {"id": board_area.area_id}

    def initialize_tiled_board_area(self, payload):
        """
        Initializes tiled board area with given parameters.

        id: (Optional) Area id
        tileCountX: Number of horizontal tiles.
        tileCountY: Number of vertical tiles.
        x1: X1 in percentage of board size.
        y1: Y1 in percentage of board size.
        x2: X2 in percentage of board size.
        y2: Y2 in percentage of board size.
        """
        board_area = TiledBoardArea(
            payload["id"] if "id" in payload else None,
            [payload["tileCountX"], payload["tileCountY"]],
            [payload["x1"], payload["y1"], payload["x2"], payload["y2"]],
            globals.board_descriptor
        )
        self.board_areas[board_area.area_id] = board_area

        return "OK", {"id": board_area.area_id}

    def remove_board_areas(self):
        """
        Removes all board areas.
        """
        self.board_areas = {}

        return "OK", {}

    def remove_board_area(self, payload):
        """
        Removes the given board area.

        id: Area ID.
        """
        area_id = payload["id"]
        del self.board_areas[area_id]

        return "OK", {}

    def remove_markers(self):
        """
        Removes all markers.
        """
        self.markers = {}

        return "OK", {}

    def remove_marker(self, payload):
        """
        Removes the given marker.

        id: Marker ID.
        """
        marker_id = payload["id"]
        del self.markers[marker_id]

        return "OK", {}

    def report_back_when_brick_found_at_any_of_positions(self, payload):
        """
        Reports back when object is found in any of the given positions.

        areaId: Board area id
        validPositions: Positions to search for object in.
        stabilityLevel: (Optional) Minimum board area stability level before searching for object
        id: (Optional) Reporter id.
        """
        board_area = self.board_areas[payload["areaId"]]
        reporter_id = payload["id"] if "id" in payload else self.draw_reporter_id()
        valid_positions = payload["validPositions"]
        stability_evel = payload["stabilityLevel"] if "stabilityLevel" in payload else 0.95

        reporter = TiledBrickPositionReporter(
            board_area,
            valid_positions,
            stability_evel,
            reporter_id,
            callback_function=lambda tile: self.send_message("OK", "brickFoundAtPosition", {"id": reporter_id, "position": tile})
        )
        self.reporters[reporter_id] = reporter

        return "OK", {"id": reporter_id}

    def report_back_when_brick_moved_to_any_of_positions(self, payload):
        """
        Reports back when object is found in any of the given positions other than the initial position.

        areaId: Board area id
        initialPosition: Initial position.
        validPositions: Positions to search for object in.
        stabilityLevel: (Optional) Minimum board area stability level before searching for object
        id: (Optional) Reporter id.
        """
        board_area = self.board_areas[payload["areaId"]]
        reporter_id = payload["id"] if "id" in payload else self.draw_reporter_id()
        initial_position = payload["initialPosition"]
        valid_positions = payload["validPositions"]
        stability_level = payload["stabilityLevel"] if "stabilityLevel" in payload else 0.95

        reporter = TiledBrickMovedToAnyOfPositionsReporter(
            board_area,
            initial_position,
            valid_positions,
            stability_level,
            reporter_id,
            callback_function=lambda tile: self.send_message("OK", "brickMovedToPosition", {"id": reporter_id, "position": tile, "initialPosition": initial_position}))
        self.reporters[reporter_id] = reporter

        return "OK", {"id": reporter_id}

    def report_back_when_brick_moved_to_position(self, payload):
        """
        Reports back when object is found at the given position.

        areaId: Board area id
        position: Position for brick to be found
        validPositions: Positions to search for object in
        stabilityLevel: (Optional) Minimum board area stability level before searching for object
        id: (Optional) Reporter id
        """
        board_area = self.board_areas[payload["areaId"]]
        reporter_id = payload["id"] if "id" in payload else self.draw_reporter_id()
        position = payload["position"]
        valid_positions = payload["validPositions"]
        stability_level = payload["stabilityLevel"] if "stabilityLevel" in payload else 0.95

        reporter = TiledBrickMovedToPositionReporter(
            board_area,
            position,
            valid_positions,
            stability_level,
            reporter_id,
            callback_function=lambda tile: self.send_message("OK", "brickMovedToPosition", {"id": reporter_id, "position": tile}))
        self.reporters[reporter_id] = reporter

        return "OK", {"id": reporter_id}


    def request_brick_position(self, payload):
        """
        Returns object position from given positions.

        areaId: Board area id
        validPositions: Positions to search for object in
        """
        image = self.take_photo()

        if image is None:
            return "CAMERA_NOT_READY", {}

        globals.board_descriptor.snapshot = globals.board_recognizer.find_board(image, globals.board_descriptor)
        if globals.board_descriptor.is_recognized():
            board_area = self.board_areas[payload["areaId"]]
            valid_positions = payload["validPositions"]
            position = globals.brick_detector.find_brick_among_tiles(board_area, valid_positions)[0]
            if position is not None:
                return "OK", {"position": position}
            else:
                return "BRICK_NOT_FOUND", {}
        else:
            return "BOARD_NOT_RECOGNIZED", {}

    def initialize_image_marker(self, payload):
        """
        Initializes image marker with given parameters.

        markerId: Marker id
        imageBase64: Image as base 64 encoded PNG
        minMatches: (Optional)Minimum number of required matches
        """
        raw_image = base64.b64decode(payload["imageBase64"])
        raw_bytes = np.asarray(bytearray(raw_image), dtype=np.uint8)
        image = cv2.imdecode(raw_bytes, cv2.CV_LOAD_IMAGE_UNCHANGED)

        marker_id = payload["markerId"]
        min_matches = payload["minMatches"] if "minMatches" in payload else 8
        image_marker = ImageMarker(marker_id, image, min_matches=min_matches)
        self.markers[marker_id] = image_marker

        return "OK", {"id": marker_id}

    def initialize_haar_classifier_marker(self, payload):
        """
        Initializes haar classifier marker with given parameters.

        markerId: Marker id
        dataBase64: Base 64 encoded Haar Cascade Classifier data
        """
        cascade_data = base64.b64decode(payload["dataBase64"])
        marker_id = payload["markerId"]
        haar_classifier_marker = HaarClassifierMarker(marker_id, cascade_data)
        self.markers[marker_id] = haar_classifier_marker

        return "OK", {"id": marker_id}

    def initialize_shape_marker(self, payload):
        """
        Initializes a shape marker with given image and parameters.

        markerId: Marker id
        shape: (Optional)Shape
        imageBase64: (Optional)Image as base 64 encoded PNG
        minArea: (Optional)Minimum area in percent of destination image
        maxArea: (Optional)Maximum area in percent of destination image
        """
        marker_id = payload["markerId"]
        if "shape" in payload:
            contour = np.int32(payload["shape"]).reshape(-1, 1, 2)
            shape_marker = ShapeMarker(marker_id,
                                       contour=contour,
                                       min_area=payload["minArea"] if "minArea" in payload else 0.0025,
                                       max_area=payload["maxArea"] if "maxArea" in payload else 0.9)
        else:
            raw_image = base64.b64decode(payload["imageBase64"])
            raw_bytes = np.asarray(bytearray(raw_image), dtype=np.uint8)
            image = cv2.imdecode(raw_bytes, cv2.CV_LOAD_IMAGE_UNCHANGED)
            shape_marker = ShapeMarker(marker_id,
                                       marker_image=image,
                                       min_area=payload["minArea"] if "minArea" in payload else 0.0025,
                                       max_area=payload["maxArea"] if "maxArea" in payload else 0.9)

        self.markers[marker_id] = shape_marker

        return "OK", {"id": marker_id}

    def report_back_when_marker_found(self, payload):
        """
        Reports back when marker is found.

        areaId: Board area id
        markerId: Marker id
        stabilityLevel: (Optional) Minimum board area stability level before searching for marker
        id: (Optional) Reporter id
        """
        board_area = self.board_areas[payload["areaId"]]
        marker = self.markers[payload["markerId"]]
        reporter_id = payload["id"] if "id" in payload else self.draw_reporter_id()
        stability_level = payload["stability_level"] if "stability_level" in payload else 0.95

        reporter = FindMarkerReporter(
            board_area,
            marker,
            stability_level,
            reporter_id,
            callback_function=lambda (marker): self.send_message("OK", "markerFound", {"id": reporter_id,
                                                                                       "areaId": payload["areaId"],
                                                                                       "marker": filter_out_contour_from_marker_result(marker)}))
        self.reporters[reporter_id] = reporter

        return "OK", {"id": reporter_id}

    def request_markers(self, payload):
        """
        Searches for the specified markers in given area.

        areaId: Board area id
        markerIds: List of marker id's
        stabilityLevel: (Optional) Minimum board area stability level before searching for markers
        """
        board_area = self.board_areas[payload["areaId"]]
        markers = [self.markers[marker_id] for marker_id in payload["markerIds"]]
        stability_level = payload["stabilityLevel"] if "stabilityLevel" in payload else 0.95
        reporter_id = self.draw_reporter_id()

        reporter = FindMarkersReporter(
            board_area,
            markers,
            stability_level,
            reporter_id,
            callback_function=lambda (result): self.send_message("OK", "markersFound", {"id": reporter_id,
                                                                                        "areaId": payload["areaId"],
                                                                                        "markers": filter_out_contour_from_marker_result_list(result)}))
        self.reporters[reporter_id] = reporter

        return None

    def reset_reporters(self):
        """
        Stops and resets all reporters.
        """
        for (_, reporter) in self.reporters.iteritems():
            reporter.stop()

        return "OK", {}

    def reset_reporter(self, payload):
        """
        Stops and resets the reporter with given ID.

        id: Reporter ID.
        """
        reporter_id = payload["id"]
        self.reporters[reporter_id].stop()

        return "OK", {}

    def take_photo(self):
        """
        Returns the most recent photo from the camera.
        """
        return globals.camera.read()

    def notify_board_not_recognized(self, board_snapshot):
        """
        Notifies client that board has not been recognized for an amount of time. If corner information is given
        from board recognizer it returns a list of unrecognized corners [topLeft, topRight, bottomLeft, bottomRight].

        :param board_snapshot Board snapshot
        """
        if board_snapshot is not None and board_snapshot.missing_corners is not None:
            self.send_message("BOARD_NOT_RECOGNIZED", "recognizeBoard",
                              {"unrecognizedCorners": board_snapshot.missing_corners})
        else:
            self.send_message("BOARD_NOT_RECOGNIZED", "recognizeBoard", {})

        # Output debug image
        if globals.debug and board_snapshot is not None:
            cv2.imwrite("debug/board_not_recognized_{0}.png".format(time.time()), board_snapshot.camera_image)

    def notify_board_recognized(self):
        """
        Notifies client that board has again been recognized.
        """
        self.send_message("BOARD_RECOGNIZED", "recognizeBoard", {})

    def send_message(self, result, action, payload={}):
        """
        Sends a new message to the client.

        :param result Result code
        :param action Client action from which the message originates
        :param payload Payload
        """
        message = {"result": result,
                   "action": action,
                   "payload": payload}
        self.sendMessage(json.dumps(message, ensure_ascii=False, encoding='utf8'))

        print("Sent message: %s" % message)

    def handleConnected(self):
        print self.address, 'connected'

    def handleClose(self):
        self.reset_reporters()
        print self.address, 'closed'

    def draw_reporter_id(self):
        while True:
            reporter_id = randint(0, 100000)
            if reporter_id not in self.reporters:
                return reporter_id

    def reporter_run(self):
        board_recognized_time = time.time()

        while True:

            # Sleep a while
            time.sleep(0.01)

            try:
                # Read image from camera
                if globals.camera is None:
                    continue

                image = globals.camera.read()
                if image is None:
                    continue

                # Do all in a lock to force sequential execution of handleMessage above
                with self.busy_lock:

                    # Recognize board
                    if globals.board_descriptor is not None:
                        globals.board_descriptor.snapshot = globals.board_recognizer.find_board(image, globals.board_descriptor)

                        # Board not recognized
                        if not globals.board_descriptor.is_recognized():

                            # Notify client that board is not recognized
                            if board_recognized_time is not None and time.time() > board_recognized_time + globals.board_not_recognized_notify_delay:
                                self.notify_board_not_recognized(globals.board_descriptor.snapshot)
                                board_recognized_time = None

                            #cv2.imwrite("board.png", image)
                        else:

                            #cv2.imwrite("board.png", globals.board_descriptor.snapshot.board_image)

                            # Notify client that board is recognized
                            if board_recognized_time is None:
                                self.notify_board_recognized()

                            board_recognized_time = time.time()

                    # Update board areas
                    for (_, board_area) in self.board_areas.copy().iteritems():

                        # Reset area image in order to force extraction of new upon next request
                        board_area.reset_area_image()

                        # Update stability score
                        if globals.board_descriptor.is_recognized():
                            board_area.update_stability_score()

                    # Run all reporters
                    reporter_ids_to_remove = []

                    for (reporter_id, reporter) in self.reporters.copy().iteritems():

                        # Run reporter
                        reporter.run_iteration()

                        # Check if stopped
                        if reporter.stopped:
                            reporter_ids_to_remove.append(reporter_id)

                    # Remove stopped reporters
                    for reporter_id in reporter_ids_to_remove:
                        self.reporters.pop(reporter_id)

            except Exception, e:
                print("Exception in reporter loop: %s" % str(e))
                traceback.print_exc(file=sys.stdout)


def start_server():
    print("Starting server...")
    server = SimpleWebSocketServer('', 9001, Server)
    server.serveforever()
