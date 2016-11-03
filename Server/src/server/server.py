from __future__ import with_statement

import json
import sys
import time
import traceback
import base64
import cv2
import numpy as np
from threading import Thread
from random import randint

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

from board.board_areas.board_area import BoardArea
from board.board_areas.tiled_board_area import TiledBoardArea
from board.board_descriptor import BoardDescriptor
from board.board_recognizer import BoardRecognizer
from board.markers.aruco_marker import ArUcoMarker
from board.markers.haar_classifier_marker import HaarClassifierMarker
from board.markers.image_marker import ImageMarker
from board.markers.marker_util import *
from board.markers.shape_marker import ShapeMarker
from server import globals
from server.reporters.find_aruco_markers_reporter import FindArUcoMarkersReporter
from server.reporters.find_marker_reporter import FindMarkerReporter
from server.reporters.find_markers_reporter import FindMarkersReporter
from server.reporters.find_contours_reporter import FindContoursReporter
from server.reporters.marker_tracker import MarkerTracker
from server.reporters.tiled_brick_moved_reporters import TiledBrickMovedToAnyOfPositionsReporter
from server.reporters.tiled_brick_moved_reporters import TiledBrickMovedToPositionReporter
from server.reporters.tiled_brick_position_reporter import TiledBrickPositionReporter
from server.reporters.tiled_brick_positions_reporter import TiledBrickPositionsReporter
from util import misc_util

if misc_util.module_exists("picamera"):
    print("Using Raspberry Pi camera")
    from server.camera_pi import Camera
else:
    print("Using desktop camera")
    from server.camera_desktop import Camera


class Server(WebSocket):
    """
    Server which communicates with the client library.
    """
    reporter_thread = None

    def handleMessage(self):
        """
        Handles incoming message.
        """
        try:
            print("Got message: %s" % self.data)
            json_dict = json.loads(self.data)

            if "action" in json_dict:
                action = json_dict["action"]

                result = self.handle_action(action, json_dict["payload"])

                if result is not None:
                    self.send_message(result=result[0], action=action, payload=result[1], request_id=result[2])

        except Exception as e:
            print("Exception in handleMessage: %s" % str(e))
            traceback.print_exc(file=sys.stdout)

    def handle_action(self, action, payload):
        if action == "enableDebug":
            return self.enable_debug(payload)
        if action == "reset":
            return self.reset(payload)
        if action == "resetReporters":
            return self.reset_reporters(payload)
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
            return self.remove_board_areas(payload)
        if action == "removeMarker":
            return self.remove_marker(payload)
        if action == "removeMarkers":
            return self.remove_markers(payload)
        if action == "reportBackWhenBrickFoundAtAnyOfPositions":
            return self.report_back_when_brick_found_at_any_of_positions(payload)
        if action == "reportBackWhenBrickMovedToAnyOfPositions":
            return self.report_back_when_brick_moved_to_any_of_positions(payload)
        if action == "reportBackWhenBrickMovedToPosition":
            return self.report_back_when_brick_moved_to_position(payload)
        if action == "requestBrickPosition":
            return self.request_brick_position(payload)
        if action == "requestBrickPositions":
            return self.request_brick_positions(payload)
        if action == "initializeShapeMarker":
            return self.initialize_shape_marker(payload)
        if action == "initializeImageMarker":
            return self.initialize_image_marker(payload)
        if action == "initializeArUcoMarker":
            return self.initialize_aruco_marker(payload)
        if action == "initializeHaarClassifierMarker":
            return self.initialize_haar_classifier_marker(payload)
        if action == "requestMarkers":
            return self.request_markers(payload)
        if action == "reportBackWhenMarkerFound":
            return self.report_back_when_marker_found(payload)
        if action == "startTrackingMarker":
            return self.start_tracking_marker(payload)
        if action == "requestArUcoMarkers":
            return self.request_aruco_markers(payload)
        if action == "requestContours":
            return self.request_contours(payload)

    def initialize_video(self, resolution):
        with globals.get_state().camera_lock:
            if globals.get_state().get_camera() is not None:
                return
            globals.get_state().set_camera(Camera())
            globals.get_state().get_camera().start(resolution)

    def initialize_reporter_thread(self):
        if self.reporter_thread is None:
            self.reporter_thread = Thread(target=self.server_lifecycle_thread_runner, args=())
            self.reporter_thread.daemon = True
            self.reporter_thread.start()

    def reset(self, payload):
        """
        Resets the board.

        requestId: (Optional) Request ID
        cameraResolution: (Optional) Camera resolution in [width, height]. Default: [640, 480].
        """
        resolution = payload["resolution"] if "resolution" in payload else [640, 480]

        globals.get_state().set_board_descriptor(None)

        self.initialize_reporter_thread()
        self.reset_reporters({})
        self.remove_board_areas({})
        self.remove_markers({})

        self.initialize_video(resolution)

        return "OK", {}, self.request_id_from_payload(payload)

    def initialize_board_descriptor(self, board_descriptor=None):
        """
        Resets the board descriptor with standard values.
        """
        with globals.get_state().board_descriptor_lock:
            board_descriptor = board_descriptor if board_descriptor is not None else globals.get_state().get_board_descriptor()
            if board_descriptor is not None:
                board_descriptor.board_size = [1280, 800]
                board_descriptor.border_percentage_size = [0.0, 0.0]

    def enable_debug(self, payload):
        """
        Enables debug output.

        requestId: (Optional) Request ID
        """
        globals.get_state().debug = True

        return "OK", {}, self.request_id_from_payload(payload)

    def take_screenshot(self, payload):
        """
        Take a screenshot and saves it to disk.

        requestId: (Optional) Request ID
        filename: (Optional) Screenshot filename
        """
        with globals.get_state().camera_lock:
            camera = globals.get_state().get_camera()
            if camera is not None:
                image = camera.read()
                if image is not None:
                    filename = payload["filename"] if "filename" in payload else\
                        "debug/board_{0}.png".format(time.strftime("%Y-%m-%d-%H%M%S"))
                    cv2.imwrite(filename, image)
                    return "OK", {}, self.request_id_from_payload(payload)

        return "CAMERA_NOT_READY", {}, self.request_id_from_payload(payload)

    def initialize_board(self, payload):
        """
        Initializes board with given parameters.

        requestId: (Optional) Request ID
        borderPercentage: (Optional) Border [width, height] in percentage of board size.
        cornerMarker: (Optional) Corner marker
        """
        with globals.get_state().board_descriptor_lock:
            board_recognizer = BoardRecognizer()

            board_descriptor = BoardDescriptor()
            self.initialize_board_descriptor(board_descriptor)
            board_descriptor.border_percentage_size = [
                payload["borderPercentage"][0] if "borderPercentage" in payload else 0.0,
                payload["borderPercentage"][1] if "borderPercentage" in payload else 0.0
            ]
            board_descriptor.corner_marker = create_marker_from_name(payload["cornerMarker"], marker_id=-1) if "cornerMarker" in payload else DefaultMarker(marker_id=-1)

            globals.get_state().set_board_recognizer(board_recognizer)
            globals.get_state().set_board_descriptor(board_descriptor)

        return "OK", {}, self.request_id_from_payload(payload)

    def initialize_board_area(self, payload):
        """
        Initializes board area with given parameters.

        requestId: (Optional) Request ID
        id: (Optional) Area id
        x1: X1 in percentage of board size.
        y1: Y1 in percentage of board size.
        x2: X2 in percentage of board size.
        y2: Y2 in percentage of board size.
        """
        with globals.get_state().board_descriptor_lock, globals.get_state().board_areas_lock:
            board_descriptor = globals.get_state().get_board_descriptor()
            board_areas = globals.get_state().get_board_areas()

            board_area = BoardArea(
                payload["id"] if "id" in payload else None,
                [payload["x1"], payload["y1"], payload["x2"], payload["y2"]],
                board_descriptor
            )
            board_areas[board_area.area_id] = board_area

            return "OK", {"id": board_area.area_id}, self.request_id_from_payload(payload)

    def initialize_tiled_board_area(self, payload):
        """
        Initializes tiled board area with given parameters.

        requestId: (Optional) Request ID
        id: (Optional) Area id
        tileCountX: Number of horizontal tiles.
        tileCountY: Number of vertical tiles.
        x1: X1 in percentage of board size.
        y1: Y1 in percentage of board size.
        x2: X2 in percentage of board size.
        y2: Y2 in percentage of board size.
        """
        with globals.get_state().board_descriptor_lock, globals.get_state().board_areas_lock:
            board_descriptor = globals.get_state().get_board_descriptor()
            board_areas = globals.get_state().get_board_areas()

            board_area = TiledBoardArea(
                payload["id"] if "id" in payload else None,
                [payload["tileCountX"], payload["tileCountY"]],
                [payload["x1"], payload["y1"], payload["x2"], payload["y2"]],
                board_descriptor
            )
            board_areas[board_area.area_id] = board_area

            return "OK", {"id": board_area.area_id}, self.request_id_from_payload(payload)

    def remove_board_areas(self, payload):
        """
        Removes all board areas.

        requestId: (Optional) Request ID
        """
        with globals.get_state().board_areas_lock:
            globals.get_state().set_board_areas({})

        return "OK", {}, self.request_id_from_payload(payload)

    def remove_board_area(self, payload):
        """
        Removes the given board area.

        requestId: (Optional) Request ID
        id: Area ID.
        """
        area_id = payload["id"]

        with globals.get_state().board_areas_lock:
            globals.get_state().remove_board_area(area_id)

        return "OK", {}, self.request_id_from_payload(payload)

    def remove_markers(self, payload):
        """
        Removes all markers.

        requestId: (Optional) Request ID
        """
        with globals.get_state().markers_lock:
            globals.get_state().set_markers({})

        return "OK", {}, self.request_id_from_payload(payload)

    def remove_marker(self, payload):
        """
        Removes the given marker.

        requestId: (Optional) Request ID
        id: Marker ID.
        """
        marker_id = payload["id"]

        with globals.get_state().markers_lock:
            globals.get_state().remove_marker(marker_id)

        return "OK", {}, self.request_id_from_payload(payload)

    def report_back_when_brick_found_at_any_of_positions(self, payload):
        """
        Reports back when brick is found in any of the given positions.

        requestId: (Optional) Request ID
        areaId: Tiled board area id
        validPositions: Positions to search for object in.
        stabilityLevel: (Optional) Minimum board area stability level before searching for object
        id: (Optional) Reporter id.
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        reporter_id = payload["id"] if "id" in payload else self.random_id()
        valid_positions = payload["validPositions"]
        stability_evel = payload["stabilityLevel"] if "stabilityLevel" in payload else 0.98

        reporter = TiledBrickPositionReporter(
            board_area,
            valid_positions,
            stability_evel,
            reporter_id,
            callback_function=lambda tile: self.send_message(result="UPDATE",
                                                             action="brickFoundAtPosition",
                                                             payload={"id": reporter_id, "position": tile},
                                                             request_id=self.request_id_from_payload(payload)))
        self.add_reporter(reporter_id, reporter)
        reporter.start()

        return "OK", {"id": reporter_id}, None

    def report_back_when_brick_moved_to_any_of_positions(self, payload):
        """
        Reports back when brick is found in any of the given positions other than the initial position.

        requestId: (Optional) Request ID
        areaId: Tiled board area id
        initialPosition: Initial position.
        validPositions: Positions to search for object in.
        stabilityLevel: (Optional) Minimum board area stability level before searching for object
        id: (Optional) Reporter id.
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        reporter_id = payload["id"] if "id" in payload else self.random_id()
        initial_position = payload["initialPosition"]
        valid_positions = payload["validPositions"]
        stability_level = payload["stabilityLevel"] if "stabilityLevel" in payload else 0.98

        reporter = TiledBrickMovedToAnyOfPositionsReporter(
            board_area,
            initial_position,
            valid_positions,
            stability_level,
            reporter_id,
            callback_function=lambda tile: self.send_message(result="UPDATE",
                                                             action="brickMovedToPosition",
                                                             payload={"id": reporter_id, "position": tile, "initialPosition": initial_position},
                                                             request_id=self.request_id_from_payload(payload)))
        self.add_reporter(reporter_id, reporter)
        reporter.start()

        return "OK", {"id": reporter_id}, None

    def report_back_when_brick_moved_to_position(self, payload):
        """
        Reports back when brick has moved to the given position.

        requestId: (Optional) Request ID
        areaId: Tiled board area id
        position: Position for brick to be found
        validPositions: Positions to search for object in
        stabilityLevel: (Optional) Minimum board area stability level before searching for object
        id: (Optional) Reporter id
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        reporter_id = payload["id"] if "id" in payload else self.random_id()
        position = payload["position"]
        valid_positions = payload["validPositions"]
        stability_level = payload["stabilityLevel"] if "stabilityLevel" in payload else 0.98

        reporter = TiledBrickMovedToPositionReporter(
            board_area,
            position,
            valid_positions,
            stability_level,
            reporter_id,
            callback_function=lambda tile: self.send_message(result="UPDATE",
                                                             action="brickMovedToPosition",
                                                             payload={"id": reporter_id, "position": tile},
                                                             request_id=self.request_id_from_payload(payload)))
        self.add_reporter(reporter_id, reporter)
        reporter.start()

        return "OK", {"id": reporter_id}, None


    def request_brick_position(self, payload):
        """
        Reports back with brick position.

        requestId: (Optional) Request ID
        areaId: Tiled board area id
        validPositions: Positions to search for object in
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        valid_positions = payload["validPositions"]
        reporter_id = payload["id"] if "id" in payload else self.random_id()

        reporter = TiledBrickPositionReporter(
            board_area,
            valid_positions,
            stability_level=0.0,
            reporter_id=reporter_id,
            callback_function=lambda position: self.send_message(result="UPDATE",
                                                                 action="brickFound",
                                                                 payload={"id": reporter_id,
                                                                          "areaId": payload["areaId"],
                                                                          "position": position},
                                                                 request_id=self.request_id_from_payload(payload)))
        self.add_reporter(reporter_id, reporter)
        reporter.start()

        return "OK", {"id": reporter_id}, None

    def request_brick_positions(self, payload):
        """
        Reports back with brick positions.

        requestId: (Optional) Request ID
        areaId: Tiled board area id
        validPositions: Positions to search for bricks in
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        valid_positions = payload["validPositions"]
        reporter_id = payload["id"] if "id" in payload else self.random_id()

        reporter = TiledBrickPositionsReporter(
            board_area,
            valid_positions,
            stability_level=0.0,
            reporter_id=reporter_id,
            callback_function=lambda positions: self.send_message(result="UPDATE",
                                                                  action="bricksFound",
                                                                  payload={"id": reporter_id,
                                                                           "areaId": payload["areaId"],
                                                                           "positions": positions},
                                                                  request_id=self.request_id_from_payload(payload)))
        self.add_reporter(reporter_id, reporter)
        reporter.start()

        return "OK", {"id": reporter_id}, None

    def initialize_image_marker(self, payload):
        """
        Initializes image marker with given parameters.

        requestId: (Optional) Request ID
        markerId: Marker id
        imageBase64: Image as base 64 encoded PNG
        minMatches: (Optional)Minimum number of required matches
        """
        raw_image = base64.b64decode(payload["imageBase64"])
        raw_bytes = np.asarray(bytearray(raw_image), dtype=np.uint8)
        image = cv2.imdecode(raw_bytes, cv2.IMREAD_UNCHANGED)
        marker_id = payload["markerId"]
        min_matches = payload["minMatches"] if "minMatches" in payload else 8

        image_marker = ImageMarker(marker_id, image, min_matches=min_matches)
        globals.get_state().set_marker(marker_id, image_marker)

        return "OK", {"id": marker_id}, self.request_id_from_payload(payload)

    def initialize_aruco_marker(self, payload):
        """
        Initializes ArUco marker with given parameters.

        requestId: (Optional) Request ID
        markerId: Marker id
        arUcoMarkerId: ArUco marker id
        markerSize: Marker size. Can be any of 4, 5, 6 and 7.
        dictionarySize: (Optional) Maximum number of markers in dictionary. Can be any of 100, 250, 1000.
        """
        marker_id = payload["markerId"]
        aruco_marker_id = payload["arUcoMarkerId"]
        marker_size = payload["markerSize"] if "markerSize" in payload else 6
        dictionary_size = payload["dictionarySize"] if "dictionarySize" in payload else 100

        aruco_marker = ArUcoMarker(marker_id, aruco_marker_id, marker_size, dictionary_size)
        globals.get_state().set_marker(marker_id, aruco_marker)

        return "OK", {"id": marker_id}, self.request_id_from_payload(payload)

    def initialize_haar_classifier_marker(self, payload):
        """
        Initializes haar classifier marker with given parameters.

        requestId: (Optional) Request ID
        markerId: Marker id
        dataBase64: Base 64 encoded Haar Cascade Classifier data
        """
        cascade_data = base64.b64decode(payload["dataBase64"])
        marker_id = payload["markerId"]

        haar_classifier_marker = HaarClassifierMarker(marker_id, cascade_data)
        globals.get_state().set_marker(marker_id, haar_classifier_marker)

        return "OK", {"id": marker_id}, self.request_id_from_payload(payload)

    def initialize_shape_marker(self, payload):
        """
        Initializes a shape marker with given image and parameters.

        requestId: (Optional) Request ID
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
            image = cv2.imdecode(raw_bytes, cv2.IMREAD_UNCHANGED)
            shape_marker = ShapeMarker(marker_id,
                                       marker_image=image,
                                       min_area=payload["minArea"] if "minArea" in payload else 0.0025,
                                       max_area=payload["maxArea"] if "maxArea" in payload else 0.9)

        globals.get_state().set_marker(marker_id, shape_marker)

        return "OK", {"id": marker_id}, self.request_id_from_payload(payload)

    def report_back_when_marker_found(self, payload):
        """
        Reports back when marker is found.

        requestId: (Optional) Request ID
        areaId: Board area id
        markerId: Marker id
        stabilityLevel: (Optional) Minimum board area stability level before searching for marker
        id: (Optional) Reporter id
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        marker = globals.get_state().get_marker(payload["markerId"])
        reporter_id = payload["id"] if "id" in payload else self.random_id()
        stability_level = payload["stability_level"] if "stability_level" in payload else 0.98

        reporter = FindMarkerReporter(
            board_area,
            marker,
            stability_level,
            reporter_id,
            callback_function=lambda marker: self.send_message(result="UPDATE",
                                                               action="markerFound",
                                                               payload={"id": reporter_id,
                                                                        "areaId": payload["areaId"],
                                                                        "marker": marker_result_to_server_output(marker)},
                                                               request_id=self.request_id_from_payload(payload)))
        self.add_reporter(reporter_id, reporter)
        reporter.start()

        return "OK", {"id": reporter_id}, None

    def request_markers(self, payload):
        """
        Searches for the specified markers in given area.

        requestId: (Optional) Request ID
        areaId: Board area id
        markerIds: List of marker id's
        stabilityLevel: (Optional) Minimum board area stability level before searching for markers
        id: (Optional) Reporter id
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        markers = [globals.get_state().get_marker(marker_id) for marker_id in payload["markerIds"]]
        reporter_id = payload["id"] if "id" in payload else self.random_id()
        stability_level = payload["stabilityLevel"] if "stabilityLevel" in payload else 0.0

        reporter = FindMarkersReporter(
            board_area,
            markers,
            stability_level,
            reporter_id,
            callback_function=lambda result: self.send_message(result="UPDATE",
                                                               action="markersFound",
                                                               payload={"id": reporter_id,
                                                                        "areaId": payload["areaId"],
                                                                        "markers": marker_result_list_to_server_output(result)},
                                                               request_id=self.request_id_from_payload(payload)))
        self.add_reporter(reporter_id, reporter)
        reporter.start()

        return "OK", {"id": reporter_id}, None

    def request_aruco_markers(self, payload):
        """
        Returns all ArUco markers in image.

        requestId: (Optional) Request ID
        areaId: Board area id
        markerSize: Marker size
        id: (Optional) Reporter id
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        reporter_id = payload["id"] if "id" in payload else self.random_id()
        marker_size = payload["markerSize"]

        reporter = FindArUcoMarkersReporter(
            board_area,
            marker_size,
            reporter_id,
            callback_function=lambda result: self.send_message(result="UPDATE",
                                                               action="markersFound",
                                                               payload={"id": reporter_id,
                                                                        "areaId": payload["areaId"],
                                                                        "markers": marker_result_list_to_server_output(result)},
                                                               request_id=self.request_id_from_payload(payload)))
        self.add_reporter(reporter_id, reporter)
        reporter.start()

        return "OK", {"id": reporter_id}, None

    def start_tracking_marker(self, payload):
        """
        Starts tracking marker.

        requestId: (Optional) Request ID
        areaId: Board area id
        markerId: Marker id
        id: (Optional) Reporter id
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        marker = globals.get_state().get_marker(payload["markerId"])
        reporter_id = payload["id"] if "id" in payload else self.random_id()

        reporter = MarkerTracker(
            board_area,
            marker,
            reporter_id,
            callback_function=lambda marker: self.send_message(result="UPDATE",
                                                               action="markerTracked",
                                                               payload={"id": reporter_id,
                                                                        "areaId": payload["areaId"],
                                                                        "marker": marker_result_to_server_output(marker)},
                                                               request_id=self.request_id_from_payload(payload)))
        self.add_reporter(reporter_id, reporter)
        reporter.start()

        return "OK", {"id": reporter_id}, None

    def request_contours(self, payload):
        """
        Searches for contours in the given area.

        requestId: (Optional) Request ID
        areaId: Board area id
        approximation: Contour approximation constant
        removeConvexHulls: (Options)Specifies whether to remove convex hulls or not
        stabilityLevel: (Optional) Minimum board area stability level before searching for markers
        id: (Optional) Reporter id
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        approximation = payload["approximation"] if "approximation" in payload else 0.02
        remove_contex_hulls = payload["removeConvexHulls"] if "removeConvexHulls" in payload else False
        reporter_id = payload["id"] if "id" in payload else self.random_id()
        stability_level = payload["stabilityLevel"] if "stabilityLevel" in payload else 0.0

        reporter = FindContoursReporter(
            board_area,
            approximation,
            remove_contex_hulls,
            stability_level,
            reporter_id,
            callback_function=lambda contours, hierarchy: self.send_message(result="UPDATE",
                                                                            action="contoursFound",
                                                                            payload={"id": reporter_id,
                                                                                     "areaId": payload["areaId"],
                                                                                     "contours": contours,
                                                                                     "hierarchy": hierarchy},
                                                                            request_id=self.request_id_from_payload(payload)))
        self.add_reporter(reporter_id, reporter)
        reporter.start()

        return "OK", {"id": reporter_id}, None

    def reset_reporters(self, payload):
        """
        Stops and resets all reporters.

        requestId: (Optional) Request ID
        """
        with globals.get_state().reporters_lock:
            reporters = globals.get_state().get_reporters()
            for (_, reporter) in reporters.items():
                reporter.stop()

        return "OK", {}, self.request_id_from_payload(payload)

    def reset_reporter(self, payload):
        """
        Stops and resets the reporter with given ID.

        requestId: (Optional) Request ID
        id: Reporter ID.
        """
        reporter_id = payload["id"]
        self.stop_reporter(reporter_id)

        return "OK", {}, self.request_id_from_payload(payload)

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

    def notify_board_recognized(self):
        """
        Notifies client that board has again been recognized.
        """
        self.send_message("BOARD_RECOGNIZED", "recognizeBoard", {})

    def send_message(self, result, action, payload={}, request_id=None):
        """
        Sends a new message to the client.

        :param result Result code
        :param action Client action from which the message originates
        :param payload Payload
        :param request_id: Request ID. If none given, random ID is generated
        """
        message = {"result": result,
                   "action": action,
                   "payload": payload,
                   "requestId": request_id if request_id is not None else self.random_id()}
        self.sendMessage(json.dumps(message, ensure_ascii=False))

        print("Sent message: %s" % message)

    def handleConnected(self):
        print(self.address, "connected")

    def handleClose(self):
        self.reset_reporters({})
        print(self.address, "closed")

    def random_id(self):
        with globals.get_state().reporters_lock:
            reporters = globals.get_state().get_reporters()
            while True:
                reporter_id = randint(0, 100000)
                if reporter_id not in reporters:
                    return reporter_id

    def add_reporter(self, reporter_id, reporter):
        """
        Adds a reporter to the lifecycle handling.

        :param reporter_id: Reporter ID
        :param reporter: Reporter
        """
        with globals.get_state().reporters_lock:
            globals.get_state().set_reporter(reporter_id, reporter)

    def stop_reporter(self, reporter_id):
        """
        Stops the reporter with given ID.
        :param reporter_id: Reporter ID
        """
        with globals.get_state().reporters_lock:
            reporter = globals.get_state().get_reporter(reporter_id)
            reporter.stop()

    def server_lifecycle_thread_runner(self):
        """
        Thread responsible for handling lifecycle of server, including reporter and board detection lifecycle.
        """

        board_recognized_time = time.time()
        board_recognized_notification = 0  # 0: no notifications sent, 1: board not recognized-notification sent, 2: board recognized-notification sent

        while True:

            try:

                # Sleep a while
                time.sleep(0.01)

                # Read image from camera
                with globals.get_state().camera_lock:
                    camera = globals.get_state().get_camera()
                    if camera is None:
                        continue

                    image = camera.read()
                    if image is None:
                        continue

                # Recognize board
                with globals.get_state().board_descriptor_lock, globals.get_state().board_recognizer_lock:

                    board_descriptor = globals.get_state().get_board_descriptor()
                    board_recognizer = globals.get_state().get_board_recognizer()

                    if board_descriptor is not None:
                        snapshot = board_recognizer.find_board(image, board_descriptor)
                        board_descriptor.set_snapshot(snapshot)

                        # Board not recognized
                        if not board_descriptor.is_recognized():

                            #cv2.imwrite("board.png", image)

                            # Notify client that board is not recognized
                            if board_recognized_notification is not 1 and time.time() > board_recognized_time + globals.get_state().board_not_recognized_notify_delay:
                                self.notify_board_not_recognized(board_descriptor.get_snapshot())
                                board_recognized_notification = 1

                        else:

                            #cv2.imwrite("board.png", globals.board_descriptor.get_snapshot().board_image())

                            # Notify client that board is recognized
                            if board_recognized_notification is not 2:
                                self.notify_board_recognized()
                                board_recognized_notification = 2

                            board_recognized_time = time.time()

                    # Update board areas
                    if board_descriptor is not None and board_descriptor.is_recognized():
                        board_areas = globals.get_state().get_board_areas()
                        for (_, board_area) in board_areas.items():
                            board_area.update_stability_score()

                # Remove all stopped reporters
                with globals.get_state().reporters_lock:

                    # Find stopped reporters
                    reporters = globals.get_state().get_reporters()
                    reporter_ids_to_remove = [reporter_id for (reporter_id, reporter) in reporters.items() if reporter.stopped]

                    # Remove stopped reporters
                    for reporter_id in reporter_ids_to_remove:
                        globals.get_state().remove_reporter(reporter_id)

            except Exception as e:
                print("Exception in reporter loop: %s" % str(e))
                traceback.print_exc(file=sys.stdout)

    def request_id_from_payload(self, payload):
        """
        Returns payload from request. If no payload given, a random ID is generated.

        :param payload: Payload
        :return: Request ID from payload, or random if none given
        """
        return payload["requestId"] if "requestId" in payload else self.random_id()


def start_server():
    print("Starting server...")
    server = SimpleWebSocketServer('', 9001, Server)
    server.serveforever()
