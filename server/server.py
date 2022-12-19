import socket
import threading
import json
import logging
import sys

from message import format_message


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 63258
BUFFER_SIZE = 2048


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


class Server:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT) -> None:
        self.clients: any = {}
        self.messages = {}
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        logger.info(f"Binding on {DEFAULT_HOST}:{DEFAULT_PORT}.")

    def run(self):
        self.socket.listen()
        # self.socket.timeout = 1
        logger.info(f"Listening...")

        while True:
            (client_socket, address) = self.socket.accept()
            logger.debug(f"Connection from {address}.")

            # Start thread for the new client connection
            try:
                client_thread = threading.Thread(
                    target=self.handle_connection, args=(client_socket,))
                client_thread.start()
            except Exception as e:
                logger.error(f"Error while starting thread: {e}")
                client_thread.quit()

    def handle_connection(self, client_socket: socket):
        client_id = self.connect(client_socket)
        if not client_id:
            return

        print("Checking for messages...")
        new_messages = self.check_for_messages(client_id)
        if new_messages:
            for message in new_messages:
                client_socket.send(message)

        # Loop until the client disconnects
        while client_id in self.clients:
            message = client_socket.recv(BUFFER_SIZE)
            self.handle_message(client_id, message)

    def handle_message(self, client_id, message):
        msg = format_message(message=message)
        print("Message received: ", msg)

        if msg["action"] == "disconnect":
            self.disconnect(client_id)

        elif msg["action"] == "message":
            self.transfer_message(client_id, msg)

    def check_for_messages(self, client_id) -> list:
        if self.messages.get(client_id):
            return self.messages.pop(client_id)

    def send_message(self, client_id: str, message: dict):
        encoded_message = json.dumps(message).encode()
        self.clients[client_id].send(encoded_message)

    def transfer_message(self, client_id: str, message: dict):
        message["sender"] = client_id
        recipient_id = message["recipient"]
        encoded_message = json.dumps(message).encode()
        # Check if the recipient is online
        if recipient_id in self.clients:
            return self.clients[recipient_id].send(encoded_message)
        else:
            self.store_message(recipient_id, encoded_message)

    def store_message(self, client_id: str, encoded_message: bytes):
        # encoded_message = json.dumps(message).encode()
        if not self.messages.get(client_id):
            self.messages[client_id] = [encoded_message]
        else:
            self.messages[client_id].append(encoded_message)

    def connect(self, client_socket: socket):
        message = client_socket.recv(BUFFER_SIZE)
        msg = format_message(message=message)
        client_id = msg["client_id"]
        if not client_id:
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
            return
        # open connection if client is already connected
        if client_id in self.clients:
            encoded_message = json.dumps({
                "action": "connect",
                "status": "failed"
            }).encode()
            client_socket.send(encoded_message)
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
            return
        # add new connection to the list of clients
        self.clients[client_id] = client_socket
        self.send_message(client_id, {
            "action": "connect",
            "status": "success"}
        )
        print(f"Client {client_id} connected")
        return client_id

    def disconnect(self, client_id: str):
        # close client socket connection
        self.send_message(client_id, {
            "action": "disconnect",
            "status": "success"}
        )
        self.clients[client_id].shutdown(socket.SHUT_RDWR)
        self.clients[client_id].close()
        self.clients.pop(client_id)
        print(f"Client {client_id} disconnected")
        return


s = Server().run()
