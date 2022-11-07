import logging
import socket
import sys
from utils.constants import HOST, INITIAL_PORT, BUFSIZE

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

class Client():
    def __init__(self, host="", port=0) -> None:
        if not host:
            self.host = HOST
        if not port:
            self.port = INITIAL_PORT
        logger.info(f"Client ready for host={host}, port={port}.")
        
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
