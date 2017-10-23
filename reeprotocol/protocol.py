import time
import serial
import logging

def AppLayer():

    def authenticate(self):
        pass

def LinkLayer():
    pass


def PhysicalLayer():
    pass

    
def Modem(PhysicalLayer):
    CONNECTED_WORDS = ["CONNECT", "REL ASYNC"]

    def __inlit__(self, phone_number, serial_port = '/dev/ttyUSB0'):
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
            self.datamode = False
        self.writeat("ATH0")
        time.sleep(2)
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
                        self.datamode = True
                        self.queue.task_done()
                        if "CONNECTED" not in i:
                           time.sleep(10)
                        return
                self.queue.task_done()
            except queue.Empty:
                logging.info("nothing yet...")
                time.sleep(1)
        raise ConnectionError("Error Waiting for connection")
        
    def writeat(self, value):
        logging.info("sending command " + value)
        self.write((value + "\r").encode("ascii"))

    def write(self, value):
        if not self.connected:
            raise ModemException("modem not connected")
        logging.info("->" + ":".join("%02x" % b for b in value))
        self.sport.write(value)

    def __enter__(self):
        return self

    def __exit__(self,type, value, traceback):
        if self.connected:
            self.disconnect()
