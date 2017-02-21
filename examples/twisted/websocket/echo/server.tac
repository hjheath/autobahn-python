from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory, listenWS
from twisted.application import service
from autobahn.websocket.types import ConnectionDeny


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        self.sendClose(code=1000, reason=unicode('chin up'))

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


class WebsocketsService(service.Service):
    """Defines the websockets service so the app can be run with twistd."""

    def __init__(self):
        self._port = None

    def startService(self):
        """Start the service."""
        self._port = listenWS(self._get_factory())

    def stopService(self):
        """Stop the service."""
        self._port.stopListening()

    @staticmethod
    def _get_factory():
        """Construct a WebsocketsServiceFactory object."""
        url = "ws://127.0.0.1"
        factory = WebSocketServerFactory(url)
        factory.protocol = MyServerProtocol
        # Turn off port checking as the ELB handles it and we need to accept
        # traffic from both the ELB and directly from clients.
        factory.externalPort = None
        return factory

# See http://twistedmatrix.com/documents/current/core/howto/application.html
# to explain this esoteric way of starting the server.
application = service.Application("Websockets")
websockets_service = WebsocketsService()
websockets_service.setServiceParent(application)