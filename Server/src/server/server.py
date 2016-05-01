import os
import json
import time
import cv2
import globals
from random import randint
from threading import Thread
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from board.board_descriptor import BoardDescriptor
from reporters.tiled_brick_position_reporter import TiledBrickPositionReporter
from reporters.tiled_brick_moved_reporters import TiledBrickMovedToAnyOfPositionsReporter
from reporters.tiled_brick_moved_reporters import TiledBrickMovedToPositionReporter

if os.uname()[4][:3] == 'arm':
    print("Using Raspberry Pi camera")
    from camera import Camera
else:
    print("Using desktop camera")
    from camera_desktop import Camera


class Server(WebSocket):
    """
    Server which communicates with the client library.
    """
    reporters = {}
    reporter_thread = None

    def initialize_video(self, resolution):
        if globals.camera is not None:
            globals.camera.stop()
            globals.camera = None

        globals.camera = Camera()
        globals.camera.start(resolution)

    def initialize_reporter_thread(self):
        if self.reporter_thread is None:
            self.reporter_thread = Thread(target=self.reporter_run, args=())
            self.reporter_thread.daemon = True
            self.reporter_thread.start()

    def handleMessage(self):
        """
        Handles incoming message.
        """
        print("Got message: %s" % self.data)
        json_dict = json.loads(self.data)

        if "action" in json_dict:
            action = json_dict["action"]
            result = self.handle_action(action, json_dict["payload"])
            if result is not None:
                self.send_message(result[0], action, result[1])

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
        if action == "initializeTiledBoard":
            return self.initialize_tiled_board(payload)
        if action == "reportBackWhenBrickFoundAtAnyOfPositions":
            return self.report_back_when_brick_found_at_any_of_positions(payload)
        if action == "reportBackWhenBrickMovedToAnyOfPositions":
            return self.report_back_when_brick_moved_to_any_of_positions(payload)
        if action == "reportBackWhenBrickMovedToPosition":
            return self.report_back_when_brick_moved_to_position(payload)
        if action == "requestBrickPosition":
            return self.request_brick_position(payload)

    def reset(self, payload):
        """
        Resets the board.

        cameraResolution: (Optional) Camera resolution in [width, height]. Default: [640, 480].
        """
        resolution = payload["resolution"] if "resolution" in payload else [640, 480]

        globals.board_descriptor = BoardDescriptor()
        globals.board_descriptor.board_size = [1280, 800]
        globals.board_descriptor.tile_count = [32, 20]
        globals.board_descriptor.border_percentage_size = [0.0, 0.0]

        self.initialize_reporter_thread()
        self.reset_reporters()

        self.initialize_video(resolution)

        return "OK", {}

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

    def initialize_tiled_board(self, payload):
        """
        Initializes tiled board with given parameters.

        tileCountX: Number of horizontal tiles.
        tileCountY: Number of vertical tiles.
        borderPctX: (Optional) Border width in percentage of board size.
        borderPctY: (Optional) Border height in percentage of board size.
        cornerMarker: (Optional) Corner marker
        """
        globals.board_descriptor.tile_count = [payload["tileCountX"], payload["tileCountY"]]
        globals.board_descriptor.border_percentage_size = [
            payload["borderPctX"] if "borderPctX" in payload else 0.0,
            payload["borderPctY"] if "borderPctY" in payload else 0.0
        ]
        return "OK", {}

    def report_back_when_brick_found_at_any_of_positions(self, payload):
        """
        Reports back when object is found in any of the given positions.

        validPositions: Positions to search for object in.
        stableTime: (Optional) Amount of time to wait for image to stabilize
        id: (Optional) Reporter id.
        """
        reporter_id = payload["id"] if "id" in payload else self.draw_reporter_id()
        valid_positions = payload["validPositions"]
        stable_time = payload["stableTime"] if "stableTime" in payload else 1.5

        reporter = TiledBrickPositionReporter(
            valid_positions,
            stable_time,
            reporter_id,
            callback_function=lambda tile: self.send_message("OK", "brickFoundAtPosition", {"id": reporter_id, "position": tile})
        )
        self.reporters[reporter_id] = reporter

        return "OK", {"id": reporter_id}

    def report_back_when_brick_moved_to_any_of_positions(self, payload):
        """
        Reports back when object is found in any of the given positions other than the initial position.

        initialPosition: Initial position.
        validPositions: Positions to search for object in.
        stable_time: (Optional) Amount of time to wait for image to stabilize
        id: (Optional) Reporter id.
        """
        reporter_id = payload["id"] if "id" in payload else self.draw_reporter_id()
        initial_position = payload["initialPosition"]
        valid_positions = payload["validPositions"]
        stable_time = payload["stableTime"] if "stableTime" in payload else 1.5

        reporter = TiledBrickMovedToAnyOfPositionsReporter(
            initial_position,
            valid_positions,
            stable_time,
            reporter_id,
            callback_function=lambda tile: self.send_message("OK", "brickMovedToPosition", {"id": reporter_id, "position": tile, "initialPosition": initial_position}))
        self.reporters[reporter_id] = reporter

        return "OK", {"id": reporter_id}

    def report_back_when_brick_moved_to_position(self, payload):
        """
        Reports back when object is found at the given position.

        position: Position for brick to be found.
        validPositions: Positions to search for object in.
        stable_time: (Optional) Amount of time to wait for image to stabilize
        id: (Optional) Reporter id.
        """
        reporter_id = payload["id"] if "id" in payload else self.draw_reporter_id()
        position = payload["position"]
        valid_positions = payload["validPositions"]
        stable_time = payload["stableTime"] if "stableTime" in payload else 1.5

        reporter = TiledBrickMovedToPositionReporter(
            position,
            valid_positions,
            stable_time,
            reporter_id,
            callback_function=lambda tile: self.send_message("OK", "brickMovedToPosition", {"id": reporter_id, "position": tile}))
        self.reporters[reporter_id] = reporter

        return "OK", {"id": reporter_id}


    def request_brick_position(self, payload):
        """
        Returns object position from given positions.

        validPositions: Positions to search for object in.
        """
        image = self.take_photo()

        if image is None:
            return "CAMERA_NOT_READY", {}

        globals.board_descriptor.snapshot = globals.board_recognizer.find_board(image, globals.board_descriptor)
        if globals.board_descriptor.is_recognized():
            valid_positions = payload["validPositions"]
            position = globals.brick_detector.find_brick_among_tiles(globals.board_descriptor, valid_positions)[0]
            if position is not None:
                return "OK", {"position": position}
            else:
                return "BRICK_NOT_FOUND", {}
        else:
            return "BOARD_NOT_RECOGNIZED", {}

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
        counter = 0

        while True:

            # Sleep a while
            time.sleep(0.1)

            # Read image from camera
            if globals.camera is None:
                continue

            image = globals.camera.read()
            if image is None:
                continue

            # Recognize board
            if globals.board_descriptor is not None:
                globals.board_descriptor.snapshot = globals.board_recognizer.find_board(image, globals.board_descriptor)
                if not globals.board_descriptor.is_recognized():
                    counter += 1
                    cv2.imwrite("debug/board_not_recognized_{0}.png".format(counter), image)

            # Run all reporters
            reporter_ids_to_remove = []

            for (reporter_id, reporter) in self.reporters.copy().iteritems():

                # Run reporter
                reporter.run_iteration()

                # Check if stopped
                if reporter.stopped:
                    reporter_ids_to_remove.append(reporter_id)

                # Sleep a while
                time.sleep(0.05)

            # Remove stopped reporters
            for reporter_id in reporter_ids_to_remove:
                self.reporters.pop(reporter_id)


def start_server():
    print("Starting server...")
    server = SimpleWebSocketServer('', 9001, Server)
    server.serveforever()
