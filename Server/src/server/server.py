import json
from random import randint
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from camera import Camera
from board.board_descriptor import BoardDescriptor
from board.board_recognizer import BoardRecognizer
from board.tile_brick_detector import TileBrickDetector
from reporters.tiled_brick_position_reporter import TiledBrickPositionReporter

class Server(WebSocket):
    """
    Server which communicates with the client library.
    """
    camera = None
    board_descriptor = BoardDescriptor()
    board_recognizer = BoardRecognizer()
    brick_detector = TileBrickDetector()

    reporters = {}

    def initialize_video(self):
        if self.camera is not None:
            self.camera.stop()
            self.camera = None

        self.camera = Camera()

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
        self.board_descriptor = BoardDescriptor()
        self.board_descriptor.board_size = [1280, 800]
        self.board_descriptor.tile_count = [32, 20]
        self.board_descriptor.border_percentage_size = [0.0, 0.0]
        self.board_descriptor.corner_marker = BoardDescriptor.BoardCornerMarker.DEFAULT

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
        self.board_descriptor.tile_count = [payload["tileCountX"], payload["tileCountY"]]
        self.board_descriptor.border_percentage_size = [
            payload["borderPctX"] if "borderPctX" in payload else 0.0,
            payload["borderPctY"] if "borderPctY" in payload else 0.0
        ]
        #self.board_descriptor.corner_marker = BoardDescriptor.BoardCornerMarker.DEFAULT
        return "OK", {}

    def report_back_when_tile_at_any_of_positions(self, payload):
        """
        Reports back when object is found in any of the given locations.

        validLocations: Locations to search for object in.
        id: (Optional) Reporter id.
        """
        id = payload["id"] if "id" in payload else self.draw_reporter_id()
        valid_locations = payload["validLocations"]

        reporter = TiledBrickPositionReporter(valid_locations,
                                              self.board_recognizer,
                                              self.board_descriptor,
                                              self.brick_detector,
                                              self.camera)
        self.reporters[id] = reporter
        reporter.start(id, lambda tile: self.send_message("OK", "tileFoundAtPosition", {"id": id, "tile": tile}))
        return "OK", {}

    def request_tiled_object_position(self, payload):
        """
        Returns object position from given locations.

        validLocations: Locations to search for object in.
        """
        self.board_descriptor.snapshot = self.board_recognizer.find_board(self.take_photo(), self.board_descriptor)
        if self.board_descriptor.is_recognized():
            valid_locations = payload["validLocations"]
            position = self.brick_detector.find_brick_among_tiles(self.board_descriptor, valid_locations)
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
        return self.camera.read()

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
        print self.address, 'closed'

    def draw_reporter_id(self):
        while True:
            id = randint(0, 100000)
            if not id in self.reporters:
                return id


def start_server():
    print("Starting server...")
    server = SimpleWebSocketServer('', 9001, Server)
    server.serveforever()
