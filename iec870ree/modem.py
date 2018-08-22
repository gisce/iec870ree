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

logger = logging.getLogger('iec870ree.modem')

class ModemException(Exception):
    pass


class Modem(PhysicalLayer):
    CONNECTED_WORDS = ["CONNECT", "REL ASYNC"]

    def __init__(self, phone_number, serial_port='/dev/ttyUSB0'):
        self.phone_number = phone_number
        self.serial_port = serial_port
        self.connected = False
        self.data_mode = False
        self.queue = queue.Queue()
 
    def connect(self):
        if (self.connected):
            return

        try:
            self.connect_port()
            self.initialize_modem()
        except Exception as e:
            self.disconnect()
            raise ModemException(e)

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
            raise ModemException("couldn't connect to port {}".format(
                self.serial_port))
                    
        self.connected = True
        self.dthread = threading.Thread(target=self.read_port,
                                        args=(self.queue,))
        self.dthread.start()

    def initialize_modem(self):
        self.writeat("ATZ")
        time.sleep(2)  # at least two seconds after ATZ (reset) command
        self.writeat("AT+CBST=7,0,1")
        time.sleep(3)
        self.writeat("ATD" + str(self.phone_number))
        self.waitforconnect()
        time.sleep(1)

    def waitforconnect(self):
        max_tries = 40
        for i in range(max_tries):
            try:
                i = self.queue.get(False, 1)
                logger.info("got message> " + i)
                for word in Modem.CONNECTED_WORDS:
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
        raise ModemException("Error Waiting for connection")

    def disconnect(self):
        if not self.connected:
            return

        try:
            if self.data_mode:
                time.sleep(1)
                self.write("+++".encode("ascii"))
                time.sleep(1)
                self.data_mode = False
            self.writeat("ATH0")
            time.sleep(2)
            self.sport.close()
        finally:
            self.data_mode = False
            self.connected = False

    def send_byte(self, bt):
        if not self.data_mode:
            raise ModemException("modem not in datamode")
        self.write(bytes([bt]))

    def send_bytes(self, bt):
        if not self.data_mode:
            raise ModemException("modem not in datamode")
        self.write(bt)
        
    def get_byte(self, timeout = 60):
        if not self.data_mode:
            raise ModemException("modem not in datamode")
        return self.queue.get(True, timeout)

    def writeat(self, value):
        logger.info("sending command " + value)
        if isinstance(value, six.text_type):
            to_write = (value + u"\r").encode("ascii")
        else:
            to_write = (value + b"\r")
        self.write(to_write)

    def write(self, value):
        if not self.connected:
            raise ModemException("modem not connected")
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
