import socket
import threading
import json
from prime_generator import generate_prime, get_generator

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 63258
BUFFER_SIZE = 4096


class Server:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT) -> None:
        self.clients = {}
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        print(f"Binding on {DEFAULT_HOST}:{DEFAULT_PORT}.")

        # generate prime and generator for the clients
        self.prime = generate_prime(1024, 10)
        self.generator = get_generator(self.prime)

    # run server and listen for new clients
    def run(self):
        self.socket.listen()
        print("Listening...")
        self.listening = True
        listen_thread = threading.Thread(target=self.listen_for_new_clients)
        listen_thread.start()

        while self.listening:
            entry = input("Enter command: ")
            if entry == "q":
                break
            elif entry == "l":
                print(self.clients.keys())
            elif not entry:
                continue

        self.listening = False
        listen_thread.join()
        self.socket.close()

    # handle new client connection
    def listen_for_new_clients(self):
        self.socket.settimeout(0.2)
        while self.listening:
            try:
                client_socket, address = self.socket.accept()
                client_thread = threading.Thread(
                    target=self.listen_for_message, args=(client_socket,))
                client_thread.start()
            except socket.timeout:
                pass

    # function to handle client connection in a new thread
    def listen_for_message(self, client_socket: socket.socket):
        client_id: str = self.connect(client_socket)
        if not client_id:
            return

        while self.listening and self.clients[client_id]["socket"]:
            message = self.receive_message(client_id)
            self.handle_message(client_id, message)

    # pretty print each message sent for debug purposes
    def send_message(self, client, message):
        if type(client) is str:
            client = self.clients[client]["socket"]

        if type(message) is dict:
            client.send(
                json.dumps(message).encode())
            print(f"Message sent to {client}: ", message)
        elif type(message) is bytes:
            client.send(message)
            print(f"Message sent to {client}: ", message.decode())

    # pretty print each message received for debug purposes
    def receive_message(self, client):
        if type(client) is str:
            client = self.clients[client]["socket"]
        elif type(client) is not socket.socket:
            return ""
        data = client.recv(BUFFER_SIZE).decode()
        print(f"Message received from {client}: ", data)
        return data

    # handle message from client
    def handle_message(self, client_id: str, message: str):
        msg = json.loads(message)

        # check if message is a service message
        if msg.get("protocol") == "clear":
            if msg.get("service"):
                # check if message is a disconnect message
                if msg["service"].get("action") == "disconnect":
                    self.clients[client_id]["socket"] = None
                    return
                # check if message is a key exchange message
                elif msg["service"].get("action") == "set_keys":
                    self.clients[client_id]["keys"] = msg["service"]["keys"]
                    return
                # check if message is a key request message
                elif msg["service"].get("action") == "get_keys":
                    payload = {
                        "recipient": msg["recipient"],
                        "protocol": "clear",
                        "service": {
                            "action": "get_keys",
                            "keys": self.clients[msg["recipient"]]["keys"]
                        }
                    }
                    self.send_message(client_id, payload)
                    return
        # else transfer message to recipient
        self.transfer_message(msg)

    # transfer message to recipient
    def transfer_message(self, message: dict) -> None:
        recipient_id: str = message["recipient"]
        encoded_message: bytes = json.dumps(message).encode()

        # Check if the recipient is online
        if self.client_is_online(recipient_id):
            print("Recipient is online, sending message")
            self.send_message(recipient_id, encoded_message)
        else:
            print("Recipient is offline, saving message")
            self.store_message(recipient_id, encoded_message)

    # check if client socket is connected
    def client_is_online(self, client_id: str) -> bool:
        return client_id in self.clients and self.clients[client_id]["socket"]

    # store message for offline recipient
    def store_message(self, client_id: str, encoded_message: bytes) -> None:
        if not self.clients.get(client_id):
            self.clients[client_id] = {
                "socket": None,
                "keys": None,
                "messages": []
            }
        self.clients[client_id]["messages"].append(encoded_message)

    # check if client has any messages
    def check_for_messages(self, client_id) -> None:
        if self.clients[client_id].get("messages"):
            for msg in self.clients[client_id]["messages"]:
                self.send_message(client_id, msg)

    # connect client to server and send p and g
    def connect(self, client_socket: socket.socket) -> str:
        message = self.receive_message(client_socket)
        msg = json.loads(message)
        sender_id = msg["sender"]

        if self.client_is_online(sender_id):
            self.disconnect(client_socket)

        self.clients[sender_id] = {
            "socket": client_socket
        }
        payload = {
            "protocol": "clear",
            "service": {
                "action": "send_p_g",
                "prime": self.prime,
                "generator": self.generator
            }
        }
        self.send_message(sender_id, payload)

        print(f"Checking for pending messages for {sender_id}")
        self.check_for_messages(sender_id)

        print(f"Client {sender_id} connected to the server")
        return sender_id

    # disconnect client from server
    def disconnect(self, client_socket: socket.socket):
        # close client socket connection
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        print(f"Client {client_socket} disconnected")
        return


s = Server().run()
