"""IP Physical Layer
"""
from __future__ import absolute_import
import socket
from .protocol import PhysicalLayer


class Ip(PhysicalLayer):
    """IP Physical Layer"""

    def __init__(self, addr):
        """Create an IP Physical Layer.
        :addr tuple: Address tuple (host, port)
        """
        self.addr = addr
        self.connection = None

    def connect(self):
        """Connect to `self.addr`
        """
        self.connection = socket.create_connection(self.addr)
    
    def disconnect(self):
        """Disconnects
        """
        if self.connection:
            self.connection.close()
    
    def send_byte(self, byte):
        """Send a byte"""
        assert isinstance(self.connection, socket.socket)
        self.connection.send(byte)
    
    def get_byte(self, timeout):
        """Read a byte"""
        assert isinstance(self.connection, socket.socket)
        self.connection.recv(1)
