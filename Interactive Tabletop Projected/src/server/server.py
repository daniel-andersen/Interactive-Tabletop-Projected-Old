from board.board_descriptor import BoardDescriptor
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket


class Server(WebSocket):
    """
    Server which communicates with the client library.
    """
    board_descriptor = BoardDescriptor()

    def __init__(self, server, sock, address):
        super(Server, self).__init__(server, sock, address)
        self.reset()

    def reset(self):
        self.board_descriptor = BoardDescriptor()

    def handleMessage(self):
        print("Got message: %s" % self.data)
        self.sendMessage(self.data)

    def handleConnected(self):
        print self.address, 'connected'

    def handleClose(self):
        print self.address, 'closed'


def start_server():
    print("Starting server...")
    server = SimpleWebSocketServer('', 9001, Server)
    server.serveforever()
