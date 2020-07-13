"""IP Physical Layer
"""
from __future__ import absolute_import
import logging
import socket
import time
import six
if six.PY2:
    import Queue as queue
else:
    import queue
import threading
import binascii
from .protocol import PhysicalLayer


logger = logging.getLogger(__name__)


class Ip(PhysicalLayer):
    """IP Physical Layer"""

    def __init__(self, addr):
        """Create an IP Physical Layer.
        :addr tuple: Address tuple (host, port)
        """
        self.addr = addr
        self.connection = None
        self.connected = False
        self.alive = threading.Event()
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.read_port)
        logger.debug("New IP with addr %s", addr)

    def connect(self):
        """Connect to `self.addr`
        """
        self.connection = socket.create_connection(self.addr)
        self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.connected = True
        self.alive.set()
        self.thread.start()
        logger.debug("Connection with %s created", self.addr)
        time.sleep(5)

    def disconnect(self):
        """Disconnects
        """
        self.alive.clear()
        self.thread.join(5)
        logger.debug("Thread joined..")
        if self.connection:
            self.connection.close()
        self.connected = False
        logger.debug("Disconnected from %s", self.addr)

    def read_port(self):
        """Read bytes from socket
        """
        logger.debug("Start reading port for %s", self.addr)
        self.connection.settimeout(10.0)
        while self.alive.is_set():
            try:
                response = self.connection.recv(16)
            except socket.timeout as e:
                continue
            except Exception as e:
                continue
            if not response:
                continue
            logger.debug(
                "<= Reading %s from %s",
                binascii.hexlify(response),
                self.addr
            )
            for byte_resp in response:
                self.queue.put(byte_resp)
        logger.debug("Stopping reading port for %s", self.addr)
        self.queue.put(None)

    def send_byte(self, byte):
        """Send a byte"""
        assert isinstance(self.connection, socket.socket)
        logger.debug("=> Sending %02x to %s", byte, self.addr)
        self.connection.send(bytes([byte]))

    def send_bytes(self, bts):
        assert isinstance(self.connection, socket.socket)
        logger.debug("=> Sending %s to %s", binascii.hexlify(bts), self.addr)
        self.connection.send(bts)

    def get_byte(self, timeout=60):
        """Read a byte"""
        logger.debug("Getting byte. waiting {}".format(timeout))
        return self.queue.get(True, timeout=timeout)
