import socket
import uuid
import logging
import threading
import sys
import time

HOST = "127.0.0.1"
INITIAL_PORT = 63258

BUFSIZE = 2048

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

class Server():
    def __init__(self) -> None:
        self.clients = set()
        entrypoint_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        entrypoint_socket.bind((HOST, INITIAL_PORT))
        entrypoint_socket.listen()
        self.entrypoint_socket = entrypoint_socket
        logger.info(f"Listening on {HOST}:{INITIAL_PORT}.")

    def run(self):
        try:
            while True:
                (conn, addr) = self.entrypoint_socket.accept()
                logger.debug(f"Connection from {addr}.")
                new_client = ClientThread(uuid.uuid1(), conn, self.clients)
                new_client.start()
                self.clients.add(new_client)
        except KeyboardInterrupt:
            logger.info("Stopping Server.")
        finally:
            self.entrypoint_socket.close()

class ClientThread(threading.Thread):
    def __init__(self, uuid, connection, friends) -> None:
        super().__init__()
        self.uuid = uuid
        self.conn: socket.socket = connection
        self.friends = friends
        logger.info(f"[+] New client thread {self.uuid}.")

    def send(self, data):
        self.conn.sendmsg(data)
        logger.info(f"Sent msg={data}.")

    def run(self):
        go = True
        while go:
            data = self.conn.recvmsg(BUFSIZE)
            print(data)
            if not data:
                time.sleep(1)
                continue
            logger.info(f"Received msg data={data}.")
            for friend in self.friends - {self}:
                friend.send(data)
            
            # if (-2, -1, "") in dataancdata:
            #     go = False

        logger.info(f"[-] Del client thread {self.uuid}.")

s = Server().run()
