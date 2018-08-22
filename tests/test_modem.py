from . import context
import unittest
from iec870ree import modem
import six
if six.PY2:
    from mock import patch, MagicMock
else:
    from unittest.mock import patch, MagicMock
import logging
from collections import OrderedDict
logging.basicConfig(level=logging.DEBUG)

class TestModem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    #@unittest.skip
    @patch('serial.Serial')
    def test_connect_disconnect(self, Serial):
        mock = MockSerial()
        Serial.return_value = mock
        phone_number = '636813395'
        m  = modem.Modem(phone_number)
        print(m)
        m.connect()
        self.assertEqual(m.connected, True)
        self.assertEqual(m.data_mode, True)
        m.disconnect()
        self.assertEqual(m.connected, False)
        self.assertEqual(m.data_mode, False)

    
    #@unittest.skip
    @patch('serial.Serial')
    def test_get_byte(self, Serial):
        mock = MockSerial()
        Serial.return_value = mock
        phone_number = '636813395'
        with modem.Modem(phone_number) as m: 
            m.connect_port()
            self.assertEqual(m.connected, True)
            m.data_mode = True
            m.sport.data_mode = True
            time.sleep(2)
            bt = m.get_byte()
            self.assertEqual(bt, ord('A'))
            bt = m.get_byte()
            self.assertEqual(bt, ord('\n'))
        
    @patch('serial.Serial')
    def test_send_bytes(self, Serial):
        mock = MockSerial()
        Serial.return_value = mock
        phone_number = '636813395'
        with modem.Modem(phone_number) as m: 
            m.connect_port()
            self.assertEqual(m.connected, True)
            m.data_mode = True
            m.sport.data_mode = True
            time.sleep(2)
            bt = b'A'
            m.send_bytes(bt)
            self.assertEqual(m.sport.last_command, b'A')

    
import time
class MockSerial():

    def __init__(self):
        self.last_command = ""
        self.data_mode = False

    def write(self, value):
        logging.info("WRITING:{}".format(value))
        self.last_command = value
    
    def read(self, size):
        time.sleep(1)
        if self.data_mode:
            logging.info("Mock DATAMODE READ")
            return bytearray(b'A\x0a')

        try:
            logging.info("Mock NOT DATAMODE READ")
            resp = MockSerial.RESPONSES_COMMAND_MODE[self.last_command]
            self.last_command = None
            return resp
        except Exception as e:
            logging.info(e)

    def close(self):
        pass

    RESPONSES_COMMAND_MODE = OrderedDict([
        (b'ATZ\x0d', bytearray(b'ATZ\x0d\x0a' + b'OK\x0d\x0a')),
        (b'AT+CBST=7,0,1\x0d', bytearray(b'AT+CBST=7,0,1\x0d\x0d\x0a' + b'OK\x0d\x0a')),
        (b'ATD636813395\x0d', bytearray(b'ATD636813395\x0d\x0d\x0a'
        + b'CONNECT 9600/RLP\x0d\x0a')),
    ])
