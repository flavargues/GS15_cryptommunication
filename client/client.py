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
        self.send_message({
            "action": "connect",
            "id": self.id
        })
        data = self.socket.recv(BUFFER_SIZE)
        msg = format_message(data)
        if msg["status"] == "success":
            threading.Thread(target=self.receive).start()
            threading.Thread(target=self.send).start()
        else:
            print("Connection failed: ", msg)
            self.disconnect()

    def send_message(self, message: dict):
        self.socket.send(json.dumps(message).encode())

    def receive(self):
        while self.connected:
            data = self.socket.recv(BUFFER_SIZE)
            if not data:
                break
            self.handle_message(data)

    def handle_message(self, message):
        msg = format_message(message=message)
        print("Message received: ", msg)

        if msg["action"] == "disconnect":
            self.disconnect()

        elif msg["action"] == "message":
            print(msg)

    def send(self):
        while self.connected:
            entry = input("Send message (ex: user,text): ")
            if entry == "quit" or entry == "exit" or entry == "q":
                break
            elif entry:
                user, text = entry.split(",")
                payload = '{"action":"message","recipient": "' + \
                    user + '", "data": "' + text + '"}'
                print("Payload sent: " + payload)
                self.socket.send(payload.encode())
        self.disconnect()

    def disconnect(self):
        self.send_message({
            "action": "disconnect"
        })
        self.socket.recv(BUFFER_SIZE)
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.connected = False
        print('Client disconnected.')


client_id = input("Set the client id: ")
Client(DEFAULT_HOST, DEFAULT_PORT, client_id)
