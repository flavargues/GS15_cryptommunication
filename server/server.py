import socket
import uuid
import logging
import threading
import sys
import time
from utils.constants import HOST, INITIAL_PORT, BUFSIZE


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

class Server():
    def __init__(self) -> None:
        self.clients = set()
        entrypoint_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        entrypoint_socket.bind((HOST, INITIAL_PORT))
        self.entrypoint_socket = entrypoint_socket

    def run(self):
        self.entrypoint_socket.listen()
        logger.info(f"Listening on {HOST}:{INITIAL_PORT}.")
        try:
            while True:
                (conn, addr) = self.entrypoint_socket.accept()
                logger.debug(f"Connection from {addr}.")
                new_client = ClientThread(uuid.uuid1(), conn, self.clients)
                new_client.start()
        except KeyboardInterrupt:
            logger.info("Stopping Server.")
        finally:
            self.entrypoint_socket.shutdown(socket.SHUT_RDWR)
            self.entrypoint_socket.close()

class ClientThread(threading.Thread):
    def __init__(self, uuid, conn: socket.socket, friends: set) -> None:
        super().__init__()
        self.uuid = uuid
        self.conn = conn
        self.friends = friends
        self.friends.add(self)
        logger.info(f"[+] New client thread {self.uuid}.")

    def sendmsg(self, data, ancillary_data=[], flags=0):
        self.conn.sendmsg([data], ancillary_data, flags)
        logger.info(f"Sent msg={data}, anc={ancillary_data}; flags={flags}.")

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
                friend.sendmsg(data)
            
            # if (-2, -1, "") in dataancdata:
            #     go = False

        logger.info(f"[-] Del client thread {self.uuid}.")

s = Server().run()
