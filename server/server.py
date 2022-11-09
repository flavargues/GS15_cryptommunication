import socket
import uuid
import logging
import threading
import sys
import time

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 63258

BUFSIZE = 2048


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


class Server:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT) -> None:
        self.clients:set = set()

        self.entrypoint_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.entrypoint_socket.bind((host, port))
        logger.info(f"Binding on {DEFAULT_HOST}:{DEFAULT_PORT}.")

    def run(self):
        self.entrypoint_socket.listen()
        logger.info(f"Listening...")
        try:
            while True:
                #Entry
                (conn, addr) = self.entrypoint_socket.accept()
                conn.setblocking(0)
                logger.debug(f"Connection from {addr}.")
                self.clients.add(ClientConnection(uuid.uuid1(), conn, self.clients))
                # TODO hostile challenge, identification & authorization

                #Communicate
                
                self.wake_clients()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping Server...")
        finally:
            self.__del__()

    def wake_clients(self):
        for client in self.clients:
            client.wake()

    def __del__(self):
        for client in self.clients:
            client.shutdown()
        self.entrypoint_socket.shutdown(socket.SHUT_RDWR)
        self.entrypoint_socket.close()
        logger.info(f"Server stopped.")


class ClientConnection:
    def __init__(self, uuid, conn: socket.socket, friends: set) -> None:
        self.uuid = uuid
        self.conn = conn
        self.friends = friends
        self.friends.add(self)
        logger.info(f"[+] New client {self.uuid}.")

    def __hash__(self) -> int:
        return int(self.uuid)

    def sendmsg(self, data, ancillary_data=[], flags=0):
        self.conn.sendmsg([data], ancillary_data, flags)
        logger.info(f"Sent msg={data}, anc={ancillary_data}; flags={flags}.")

    def wake(self):
        logger.debug(f"ClientConnection {self} woken up.")
        data = self.conn.recvmsg(BUFSIZE)
        if not data:
            return
        logger.info(f"Received msg data={data}.")

        logger.debug(f"Begin multicast.")
        for friend in self.friends - {self}:
            friend.sendmsg(data)
            logger.debug(f"Sent data to {friend}.")
        logger.debug(f"Multicast done.")

    def deconnect(self):
        # Graceful deconnect
        pass

    def shutdown(self):
        self.conn.detach()
        # TODO send stop and gracefully detach
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()
        logger.info(f"[-] Del client {self.uuid}.")


s = Server().run()
