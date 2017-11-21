"""IP Physical Layer
"""
from __future__ import absolute_import
import socket
import queue
import threading
from .protocol import PhysicalLayer


class Ip(PhysicalLayer):
    """IP Physical Layer"""

    def __init__(self, addr):
        """Create an IP Physical Layer.
        :addr tuple: Address tuple (host, port)
        """
        self.addr = addr
        self.connection = None
        self.connected = False
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.read_port)

    def connect(self):
        """Connect to `self.addr`
        """
        self.connection = socket.create_connection(self.addr)
        self.connected = True
        self.thread.start()

    def disconnect(self):
        """Disconnects
        """
        if self.connection:
            self.connection.close()
        self.connected = False

    def read_port(self):
        """Read bytes from socket
        """
        while self.connected:
            response = self.connection.recv(16)
            if not response:
                continue
            for byte_resp in response:
                self.queue.put(byte_resp)

    def send_byte(self, byte):
        """Send a byte"""
        assert isinstance(self.connection, socket.socket)
        self.connection.send(byte)

    def get_byte(self, timeout=60):
        """Read a byte"""
        return self.queue.get(True, timeout=timeout)
