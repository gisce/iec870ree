from .protocol import PhysicalLayer
import threading
import six
if six.PY2:
    import Queue as queue
else:
    import queue
import serial
import time
import logging

logger = logging.getLogger('iec870ree.serial')

class SerialException(Exception):
    pass


class Serial(PhysicalLayer):
    CONNECTED_WORDS = ["CONNECT", "REL ASYNC"]

    def __init__(self, serial_port='/dev/ttyUSB0'):
        self.serial_port = serial_port
        self.connected = False
        self.data_mode = False
        self.queue = queue.Queue()
 
    def connect(self):
        if (self.connected):
            return

        try:
            self.connect_port()
        except Exception as e:
            self.disconnect()
            raise SerialException(e)

    def connect_port(self):
        max_tries = 20
        for i in range(max_tries):
            logger.info("try open port {}".format(i))
            try:
                self.sport = serial.Serial(self.serial_port, baudrate=9600,
                                           timeout=1)
                logger.info("serial port {} opened".format(self.serial_port))
                break
            except serial.serialutil.SerialException as ex:
                logger.warning("error connectiong {}".format(ex))
                time.sleep(1)
                if (i >= max_tries or "Permission" not in str(ex)):
                    raise ex
        else:
            raise SerialException("couldn't connect to port {}".format(
                self.serial_port))
                    
        self.connected = True
        self.dthread = threading.Thread(target=self.read_port,
                                        args=(self.queue,))
        self.dthread.start()

    def waitforconnect(self):
        max_tries = 40
        for i in range(max_tries):
            try:
                i = self.queue.get(False, 1)
                logger.info("got message> " + i)
                for word in Serial.CONNECTED_WORDS:
                    if word in i:
                        logger.info("CONNECTED!!!!!!!!!!!!!!!!!!!!")
                        self.data_mode = True
                        self.queue.task_done()
                        time.sleep(5)  # everything smooth in read thread
                        return
                self.queue.task_done()
            except queue.Empty:
                logger.info("nothing yet...")
                time.sleep(1)
        raise SerialException("Error Waiting for connection")

    def disconnect(self):
        if not self.connected:
            return

        try:
            if self.data_mode:
                self.data_mode = False
            self.sport.close()
        finally:
            self.data_mode = False
            self.connected = False

    def send_byte(self, bt):
        if not self.data_mode:
            raise SerialException("serial not in datamode")
        self.write(bytes([bt]))

    def send_bytes(self, bt):
        if not self.data_mode:
            raise SerialException("serial not in datamode")
        self.write(bt)
        
    def get_byte(self, timeout = 60):
        if not self.data_mode:
            raise SerialException("serial not in datamode")
        return self.queue.get(True, timeout)

    def write(self, value):
        if not self.connected:
            raise SerialException("serial not connected")
        logger.debug("->" + ":".join("%02x" % b for b in bytearray(value)))
        self.sport.write(value)

    def read_port(self, read_queue):
        logger.info("read thread Starting")
        buffer = bytearray()
        while self.connected:
            logger.debug("iterate read thread")
            response = self.sport.read(1)
            if not response:
                continue
            logger.debug("<-" + ":".join("%02x" % b for b in bytearray(response)))

            for b in response:
                # if not self.data_mode and (b == 0x0A or b == 0x0D):
                if not self.data_mode:
                    # answer with the line
                    buffer.append(b)
                    if (b == 0x0A):
                        logger.info("R-" + buffer.decode("ascii"))
                        read_queue.put(buffer.decode("ascii"))
                        del buffer[:]
                else:
                    read_queue.put(b)

        logger.info("read thread END")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()
