import threading
import socket
import json
from message import format_message

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 63258
BUFFER_SIZE = 2048


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
        try:
            threading.Thread(target=self.receive).start()
            threading.Thread(target=self.send).start()
        except:
            print("Connection failed.")
            self.disconnect()

    def send_message(self, message: dict):
        self.socket.send(json.dumps(message).encode())

    def receive(self):
        while self.connected:
            data = self.socket.recv(BUFFER_SIZE)
            print("Message received: ", data.decode())
            self.handle_message(data)

    def handle_message(self, message: bytes):
        msg = json.loads(message.decode())
        if msg["protocol"] == "clear":
            if msg.get("service"):
                if msg["service"].get("action") == "connect":
                    print("Connected to server.")
                elif msg["service"].get("action") == "disconnect":
                    self.disconnect()
        else:
            print("Message not handled.")

    def send(self):
        while self.connected:
            recipient = input("Send message to (q to quit, l to list): ")
            if recipient == "q":
                break
            elif recipient == "l":
                print("Recipients: ", self.recipients)
                continue
            elif not recipient:
                continue
            elif recipient not in self.recipients:
                print("Recipient not found. Creating new recipient.")
                # TODO: Key exchange between clients and storage
                self.recipients[recipient] = {
                    "identity_key": "identity_key",
                    "master_secret": "master_secret",
                    "message_key": "message_key"
                }

            text = input("Message: ")
            if recipient and text:
                payload = {
                    "sender": self.id,
                    "recipient": recipient,
                    "data": text
                }
                print("Payload sent: ", payload)
                self.send_message(payload)
        self.disconnect()

    def disconnect(self):
        self.send_message({
            "sender": self.id,
            "protocol": "clear",
            "service": {
                "action": "disconnect"
            }
        })
        self.connected = False
        self.socket.recv(BUFFER_SIZE)
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print('Client disconnected.')


client_id = input("Set the client id: ")
Client(DEFAULT_HOST, DEFAULT_PORT, client_id)
