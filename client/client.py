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


# client socket class
class Client:
    def __init__(self, host: str, port: int, id: str) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.connected = True
        self.id = id
        self.recipients = {}
        # send connection request to server and receive server's prime and generator
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
        # send my public keys to server
        self.send_message({
            "sender": self.id,
            "protocol": "clear",
            "service": {
                "action": "set_keys",
                "keys": self.x3dh.get_my_public_keys()
            }
        })
        try:
            print("Starting listening in new thread...")
            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()
            # send messages in main thread
            self.send()
            receive_thread.join()
            self.disconnect()
        except:
            pass

    def send(self):
        while self.connected:
            recipient = input("Send message to (q to quit, l to list): ")
            # client wants to quit
            if recipient == "q":
                self.connected = False
                break
            # list all recipients in client's database
            elif recipient == "l":
                print("Recipients: ", self.x3dh.get_recipients())
                continue
            elif not recipient:
                continue
            # add new recipient to client's database if not exists
            elif not self.x3dh.have_recipient(recipient):
                print("Recipient not found. Creating new recipient, please wait...")
                self.add_recipient(recipient)

            # send message to recipient if recipient exists
            if self.x3dh.have_recipient(recipient):
                text = input("Message: ")
                if recipient and text:
                    payload = self.x3dh.encrypt(recipient, text.encode())
                    self.send_message(payload)

        return

    def receive(self):
        # set timeout for socket in order to check if client wants to quit
        self.socket.settimeout(1.0)
        while self.connected:
            try:
                data = self.receive_message()
                self.handle_message(data)
            except socket.timeout:
                pass

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

    def handle_message(self, message: str):
        msg = json.loads(message)
        # if protocol is clear, handle service actions : get_keys
        if msg["protocol"] == "clear":
            if msg.get("service"):
                if msg["service"].get("action") == "get_keys":
                    # self.x3dh.set_public_keys(
                    #     msg["recipient"], msg["service"]["keys"], 1024)
                    print("Recipient added: ", msg["recipient"])
        # if protocol is x3dh, decrypt message and if new recipient, add to client's database
        elif msg["protocol"] == "x3dh":
            self.add_recipient(msg["sender"])
            decrypted_msg = self.x3dh.decrypt(message.encode())
            print("Text received from ", msg["sender"], ": ")
            print(decrypted_msg.decode())

    def add_recipient(self, recipient: str):
        # key exchange between clients and storage
        if not self.x3dh.have_recipient(recipient):
            # ask server for recipient's public keys
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

    def disconnect(self):
        # send disconnect request to server
        self.send_message({
            "sender": self.id,
            "protocol": "clear",
            "service": {
                "action": "disconnect"
            }
        })
        # close socket
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print('Client disconnected.')
        return


client_id = input("Set the client id: ")
Client(DEFAULT_HOST, DEFAULT_PORT, client_id)
