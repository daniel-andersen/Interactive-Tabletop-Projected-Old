import os
import json
import globals
from random import randint
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from board.board_descriptor import BoardDescriptor
from reporters.tiled_brick_position_reporter import TiledBrickPositionReporter

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

    def initialize_video(self):
        if globals.camera is not None:
            globals.camera.stop()
            globals.camera = None

        globals.camera = Camera()
        globals.camera.start()

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
        if action == "reset":
            return self.reset()
        if action == "resetReporters":
            return self.reset_reporters()
        if action == "initializeTiledBoard":
            return self.initialize_tiled_board(payload)
        if action == "reportBackWhenTileAtAnyOfPositions":
            return self.report_back_when_tile_at_any_of_positions(payload)
        if action == "requestTiledObjectPosition":
            return self.request_tiled_object_position(payload)

    def reset(self):
        """
        Resets the board.
        """
        globals.board_descriptor = BoardDescriptor()
        globals.board_descriptor.board_size = [1280, 800]
        globals.board_descriptor.tile_count = [32, 20]
        globals.board_descriptor.border_percentage_size = [0.0, 0.0]
        globals.board_descriptor.corner_marker = BoardDescriptor.BoardCornerMarker.DEFAULT

        self.reset_reporters()

        self.initialize_video()

        return "OK", {}

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
        #globals.board_descriptor.corner_marker = BoardDescriptor.BoardCornerMarker.DEFAULT
        return "OK", {}

    def report_back_when_tile_at_any_of_positions(self, payload):
        """
        Reports back when object is found in any of the given locations.

        validLocations: Locations to search for object in.
        stable_time: (Optional) Amount of time to wait for image to stabilize
        id: (Optional) Reporter id.
        """
        id = payload["id"] if "id" in payload else self.draw_reporter_id()
        valid_locations = payload["validLocations"]
        stable_count = payload["stableTime"] if "stableTime" in payload else 2.0

        reporter = TiledBrickPositionReporter(valid_locations, stable_count)
        self.reporters[id] = reporter
        reporter.start(id, lambda tile: self.send_message("OK", "tileFoundAtPosition", {"id": id, "tile": tile}))
        return "OK", {"id": id}

    def request_tiled_object_position(self, payload):
        """
        Returns object position from given locations.

        validLocations: Locations to search for object in.
        """
        image = self.take_photo()

        if image is None:
            return "CAMERA_NOT_READY"

        globals.board_descriptor.snapshot = globals.board_recognizer.find_board(image, globals.board_descriptor)
        if globals.board_descriptor.is_recognized():
            valid_locations = payload["validLocations"]
            position = globals.brick_detector.find_brick_among_tiles(globals.board_descriptor, valid_locations)[0]
            if position is not None:
                return "OK", {"position": position}
            else:
                return "BRICK_NOT_FOUND"
        else:
            return "BOARD_NOT_RECOGNIZED"

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

    def take_photo(self):
        """
        Returns the most recent photo from the camera.
        """
        return globals.camera.read()

    def reset_reporters(self):
        """
        Stops and resets all reporters.
        """
        for (_, reporter) in self.reporters.iteritems():
            reporter.stop()

        self.reporters = {}

    def handleConnected(self):
        print self.address, 'connected'

    def handleClose(self):
        self.reset_reporters()
        print self.address, 'closed'

    def draw_reporter_id(self):
        while True:
            id = randint(0, 100000)
            if id not in self.reporters:
                return id


def start_server():
    print("Starting server...")
    server = SimpleWebSocketServer('', 9001, Server)
    server.serveforever()
