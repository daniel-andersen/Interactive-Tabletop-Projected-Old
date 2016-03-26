import cv2
import json
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from board.board_descriptor import BoardDescriptor
from board.board_recognizer import BoardRecognizer
from board.tile_brick_detector import TileBrickDetector
from util import enum


class Server(WebSocket):
    """
    Server which communicates with the client library.
    """
    video_capture = None
    board_descriptor = BoardDescriptor()
    board_recognizer = BoardRecognizer()
    brick_detector = TileBrickDetector()

    def initialize_video(self):
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None

        self.video_capture = cv2.VideoCapture(0)

    def handleMessage(self):
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
        if action == "initializeTiledBoard":
            return self.initialize_tiled_board(payload)
        if action == "requestTiledObjectPosition":
            return self.request_tiled_object_position(payload)

    def reset(self):
        self.board_descriptor = BoardDescriptor()
        self.board_descriptor.board_size = [1280, 800]
        self.board_descriptor.tile_count = [32, 20]
        self.board_descriptor.border_percentage_size = [0.0, 0.0]
        self.board_descriptor.corner_marker = BoardDescriptor.BoardCornerMarker.DEFAULT

        self.initialize_video()

        return "OK", {}

    def initialize_tiled_board(self, payload):
        self.board_descriptor.tile_count = [payload["tileCountX"], payload["tileCountY"]]
        self.board_descriptor.border_percentage_size = [payload["borderPctX"], payload["borderPctY"]]
        #self.board_descriptor.corner_marker = BoardDescriptor.BoardCornerMarker.DEFAULT
        return "OK", {}

    def request_tiled_object_position(self, payload):
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
        message = {"result": result,
                   "action": action,
                   "payload": payload}
        self.sendMessage(json.dumps(message, ensure_ascii=False, encoding='utf8'))

    def take_photo(self):
        image = self.video_capture.read()
        image = cv2.resize(image, (640, 480), interpolation = cv2.INTER_CUBIC)
        return image

    def handleConnected(self):
        print self.address, 'connected'

    def handleClose(self):
        print self.address, 'closed'


def start_server():
    print("Starting server...")
    server = SimpleWebSocketServer('', 9001, Server)
    server.serveforever()
