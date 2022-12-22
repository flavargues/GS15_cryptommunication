import threading
import socket
import json
import logging
import sys
from crypto.DiffieHellman import ExtendedTripleDiffieHellman

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 63258
BUFFER_SIZE = 4096

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, host: str, port: int, id: str) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.connected = True
        self.id = id
        self.recipients = {}
        self.send_message({
            "sender": self.id,
            "protocol": "clear",
            "service": {
                "action": "connect"
            }
        })
        message = json.loads(self.receive_message())
        logger.info(f"Connected to {host}:{port} with client ID: {self.id}.")
        self.x3dh: ExtendedTripleDiffieHellman = ExtendedTripleDiffieHellman(
            self.id,
            1024,
            message["service"]["prime"],
            message["service"]["generator"]
        )
        self.send_message({
            "sender": self.id,
            "protocol": "clear",
            "service": {
                "action": "set_keys",
                "keys": self.x3dh.get_my_public_keys()
            }
        })
        self.socket.settimeout(1.0)
        try:
            print("Starting listening in new thread...")
            threading.Thread(target=self.receive).start()
            self.send()
        except:
            print("Connection failed.")
            self.disconnect()

    def send_message(self, message):
        if type(message) is dict:
            self.socket.send(json.dumps(message).encode())
            print("Message sent: ", message)
        elif type(message) is bytes:
            self.socket.send(message)
            print("Message sent: ", message.decode())

    def receive_message(self) -> str:
        data = self.socket.recv(BUFFER_SIZE).decode()
        print("Message received: ", data)
        return data

    def receive(self):
        while self.connected:
            try:
                data = self.receive_message()
                self.handle_message(data)
            except socket.timeout:
                pass

    def handle_message(self, message: str):
        msg = json.loads(message)
        if msg["protocol"] == "clear":
            if msg.get("service"):
                if msg["service"].get("action") == "connect":
                    print("Connected to server.")
                # elif msg["service"].get("action") == "disconnect":
                #     self.disconnect()
                elif msg["service"].get("action") == "get_keys":
                    self.x3dh.set_public_keys(
                        msg["recipient"], msg["service"]["keys"], 1024)
                    print(self.x3dh.recipients[msg["recipient"]])
        elif msg["protocol"] == "x3dh":
            self.add_recipient(msg["sender"])
            decrypted_msg = self.x3dh.decrypt(message.encode())
            print(decrypted_msg.decode())

    def add_recipient(self, recipient: str):
        # Key exchange between clients and storage
        if not self.x3dh.have_recipient(recipient):
            self.send_message({
                "recipient": recipient,
                "protocol": "clear",
                "service": {
                    "action": "get_keys",
                }
            })
            msg = json.loads(self.receive_message())
            self.x3dh.set_public_keys(
                msg["recipient"], msg["service"]["keys"], 1024)
            return True

    def send(self):
        while self.connected:
            recipient = input("Send message to (q to quit, l to list): ")
            if recipient == "q":
                break
            elif recipient == "l":
                print("Recipients: ", self.x3dh.get_recipients())
                continue
            elif not recipient:
                continue
            elif not self.x3dh.have_recipient(recipient):
                print("Recipient not found. Creating new recipient.")

            if self.add_recipient(recipient):
                text = input("Message: ")
                if recipient and text:
                    payload = self.x3dh.encrypt(recipient, text.encode())
                    self.send_message(payload)

        return self.disconnect()

    def disconnect(self):
        self.send_message({
            "sender": self.id,
            "protocol": "clear",
            "service": {
                "action": "disconnect"
            }
        })
        self.socket.shutdown(socket.SHUT_RDWR)
        self.connected = False
        self.socket.close()
        print('Client disconnected.')
        return


client_id = input("Set the client id: ")
Client(DEFAULT_HOST, DEFAULT_PORT, client_id)
