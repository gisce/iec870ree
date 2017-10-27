from .protocol import PhysicalLayer
import threading, queue
import serial
import time
import logging

class Modem(PhysicalLayer):
    CONNECTED_WORDS = ["CONNECT", "REL ASYNC"]

    def __init__(self, phone_number, serial_port = '/dev/ttyUSB0'):
        self.phone_number = phone_number
        self.serial_port = serial_port
        self.connected = False
        self.data_mode = False
        self.queue = queue.Queue()
                
    def connect(self):
        if (self.connected):
            return
        max_tries = 20
        for i in range(1,max_tries+1):
            try:
                self.sport=serial.Serial(self.serial_port, baudrate=9600,
                                        timeout = 1)
                break
            except serial.serialutil.SerialException as ex:
                time.sleep(1)
                if (i >= max_tries or "Permission" not in str(ex)):
                    raise ex
        self.connected = True
        self.dthread = threading.Thread(target=self.read_port,
                                        args=(self.queue,))
        self.dthread.start()
        self.writeat("ATZ")
        time.sleep(2)
        self.writeat("AT+CBST=7,0,1")
        time.sleep(5)
        self.writeat("ATD" + str(self.phone_number) )
        self.waitforconnect()
        time.sleep(1)

    def disconnect(self):
        if not self.connected:
            return
        if self.data_mode:
            time.sleep(1)
            self.write("+++".encode("ascii"))
            time.sleep(1)
            self.data_mode = False
        self.writeat("ATH0")
        time.sleep(1)
        self.connected = False
        time.sleep(2)
        self.sport.close()

    def waitforconnect(self):
        for i in range(40):
            try:
                i = self.queue.get(False, 1)
                logging.info("got message> " + i)
                for word in Modem.CONNECTED_WORDS:
                    if word in i:
                        logging.info("CONNECTED!!!!!!!!!!!!!!!!!!!!")
                        self.data_mode = True
                        self.queue.task_done()
                        if "CONNECTED" not in i:
                           time.sleep(10)
                        return
                self.queue.task_done()
            except queue.Empty:
                logging.info("nothing yet...")
                time.sleep(1)
        raise ConnectionError("Error Waiting for connection")

    def send_byte(self, bt):
        self.write(bt)

    def get_byte(self):
        if self.data_mode:
            raise ModemException("modem not in datamode")
        return self.queue.get(False, 1)
                
    def writeat(self, value):
        logging.info("sending command " + value)
        self.write((value + "\r").encode("ascii"))

    def write(self, value):
        if not self.connected:
            raise ModemException("modem not connected")
        logging.info("->" + ":".join("%02x" % b for b in value))
        self.sport.write(value)

    def read_port(self, read_queue):
        logging.info ("read thread")
        buffer=bytearray()
        while self.connected:
            response = self.sport.read(16)
            if not response:
                continue
            logging.info("<-" + ":".join("%02x" % b for b in response))
            
            for b in response:
                #if not self.data_mode and (b == 0x0A or b == 0x0D):
                if not self.data_mode:
                    #answer with the line
                    buffer.append(b)
                    if (b == 0x0A):
                        logging.info("R-" + buffer.decode("ascii"))
                        read_queue.put(buffer.decode("ascii"))
                        del buffer[:]
                else:
                    read_queue.put(b)

        logging.info ("read thread END")
        
