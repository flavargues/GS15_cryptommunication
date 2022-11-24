import logging
import socket
import sys

HOST = "127.0.0.1"
INITIAL_PORT = 63258

BUFSIZE = 2048

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

class Client():
    def __init__(self, host="", port=0) -> None:
        if not host:
            self.host = host or HOST
        if not port:
            self.port = port or INITIAL_PORT
        self.gen_identity_keys()
        
        logger.info(f"Client ready for host={self.host}, port={self.port}.")
        
    def connect(self):
        logger.debug(f"Initiating connection to {self.host}:{self.port}.")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def sendmsg(self, data, ancillary_data=[], flags=0):
        self.socket.sendmsg([data], ancillary_data, flags)

    def recvmsg(self):
        ret = self.socket.recvmsg(BUFSIZE)
        print(ret)
        return(ret)

    def __del__(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        