import socket
import uuid
import logging
import threading

HOST = "127.0.0.1"
INITIAL_PORT = 63256

BUFSIZE = 2048

logger = logging.getLogger(__name__)

class Server():
    def __init__(self) -> None:
        self.clients = set()
        entrypoint_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        entrypoint_socket.bind((HOST, INITIAL_PORT))
        entrypoint_socket.listen()
        self.entrypoint_socket = entrypoint_socket
        logger.info(f"Listening on {HOST}:{INITIAL_PORT}.")

    def uuid_generator(self):
        generator = uuid
        while True:
            yield generator.uuid4()

    def run(self):
        while True:
            (conn, addr) = self.entrypoint_socket.accept()
            logger.debug(f"Connection from {addr}.")
            new_client = ClientThread(self.uuid_generator(), conn, self.clients)
            new_client.start()
            self.clients.add(new_client)

class ClientThread(threading.Thread):
    def __init__(self, uuid, connection, friends) -> None:
        self.uuid = uuid
        self.conn: socket.socket = connection
        self.friends = friends
        logger.info(f"[+] New client thread {self.uuid}.")

    def send(self, data_tuple):
        self.conn.sendmsg(*data_tuple)
        logger.info(f"Sent msg={data_tuple}.")

    def run(self):
        go = True
        while go:
            (data, ancdata, msg_flags, address) = self.conn.recvmsg(BUFSIZE)
            logger.info(f"Received msg data={data}, ancdata={ancdata}, msg_flags={msg_flags}, address={address}.")
            self.friends.send((data, ancdata, msg_flags, address))
            
            if (-2, -1, "") in ancdata:
                go = False

        logger.info(f"[-] Del client thread {self.uuid}.")