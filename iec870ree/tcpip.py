from .protocol import PhysicalLayer
import threading
import queue
import time
import logging
import socket

logger = logging.getLogger('iec870ree.tcpip')

class TcpIp(PhysicalLayer):

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connected = False
        self.queue = queue.Queue()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((self.ip, self.port))
        self.socket.settimeout(1.0)
        self.dthread = threading.Thread(target=self.read_port,
                                        args=(self.queue,))
        self.connected = True
        self.dthread.start()
        

    def disconnect(self):
        if not self.connected:
            return
        else:
            self.socket.close()
            self.connected = False

    def send_byte(self, bt):
        self.socket.send(bytes([bt]))

    def send_bytes(self, bt):
        self.socket.send(bt)

    def get_byte(self, timeout):
        return self.queue.get(True, timeout)

    def read_port(self, read_queue):
        logging.info ("read thread")
        while self.connected:
            logging.info ("read thread loop")
            try:
                response = self.socket.recv(1)
            except OSError:
                break

            if not response:
                continue

            for b in response:
                read_queue.put(b)
            
    def __enter__(self):
        return self

    def __exit__(self,type, value, traceback):
        self.disconnect()
        
