import socket
import threading
import json
import logging
import sys

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 63258
BUFFER_SIZE = 2048


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


class Server:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT) -> None:
        self.clients = {}
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        logger.info(f"Binding on {DEFAULT_HOST}:{DEFAULT_PORT}.")

    def run(self):
        self.socket.listen()
        logger.debug("Listening...")

        while True:
            (client_socket, address) = self.socket.accept()
            logger.debug(f"Connection from {address}.")

            try:
                client_thread = threading.Thread(
                    target=self.handle_connection, args=(client_socket,))
                client_thread.start()
            except:
                logger.debug("Error: unable to start thread")

    def handle_connection(self, client_socket: socket):
        client_id = self.connect(client_socket)
        if not client_id:
            payload = json.dumps({
                "protocol": "clear",
                "service": {
                    "action": "disconnect"
                }
            }).encode()
            client_socket.send(payload)
            client_socket.recv(BUFFER_SIZE)
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()

        # Loop until the client disconnects
        while client_id in self.clients:
            message = client_socket.recv(BUFFER_SIZE)
            self.handle_message(client_id, message)

    def handle_message(self, client_id: str, message: bytes):
        msg = json.loads(message.decode())
        print("Message received: ", msg)
        logger.debug("Message received: ", msg)

        if msg.get("protocol") == "clear" and msg.get("service") and msg["service"].get("action") == "disconnect":
            return self.disconnect(client_id)

        self.transfer_message(msg)

    def transfer_message(self, message: dict):
        recipient_id = message["recipient"]
        encoded_message = json.dumps(message).encode()

        # Check if the recipient is online
        if recipient_id in self.clients:
            return self.clients[recipient_id].send(encoded_message)

        logger.debug("Recipient is offline, dropping message")
        return

    def connect(self, client_socket: socket):
        message = client_socket.recv(BUFFER_SIZE)
        msg = json.loads(message.decode())
        sender_id = msg["sender"]

        if not sender_id or sender_id in self.clients:
            return

        # add new connection to the list of clients
        self.clients[sender_id] = client_socket
        self.clients[sender_id].send(message)
        logger.debug(f"Client {sender_id} connected to the server")
        return sender_id

    def disconnect(self, client_id: str):
        # close client socket connection
        payload = json.dumps({
            "protocol": "clear",
            "service": {
                "action": "disconnect"
            }
        }).encode()
        self.clients[client_id].send(payload)
        self.clients[client_id].recv(BUFFER_SIZE)
        self.clients[client_id].shutdown(socket.SHUT_RDWR)
        self.clients[client_id].close()
        self.clients.pop(client_id)
        logger.debug(f"Client {client_id} disconnected")
        return


s = Server().run()
