from . import context
import unittest
from reeprotocol import modem
from unittest.mock import patch, MagicMock
import logging

class TestModem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('serial.Serial')
    def test_modem(self, Serial):
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

import time
class MockSerial():
    def write(self, value):
        pass
    def read(self, size):
        time.sleep(1)
        return "CONNECTED\n".encode('ascii')

    def close(self):
        pass
