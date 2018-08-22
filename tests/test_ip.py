import unittest
from six import PY2
if PY2:
    from mock import patch, Mock, MagicMock
else:
    from unittest.mock import patch, Mock, MagicMock
import logging

from iec870ree.ip import Ip


class TestIp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)

    def test_ip_phisical_initial_values(self):
        ip = Ip(('localhost', 20000))
        self.assertEqual(ip.addr, ('localhost', 20000))
        self.assertIsNone(ip.connection)
        self.assertFalse(ip.connected)

    @patch('socket.create_connection')
    def test_connected(self, mock_socket):
        m_socket = MagicMock()
        m_socket.recv.return_value = bytes([1,2])
        mock_socket.return_value = m_socket
        ip = Ip(('example.org', 20000))
        ip.connect()
        self.assertTrue(ip.connected)
        self.assertIsInstance(ip.connection, MagicMock)
        ip.disconnect()
    
    @patch('socket.create_connection')
    def test_read_from_queue(self, mock_socket):
        m_socket = MagicMock()
        m_socket.recv = Mock()
        m_socket.recv.side_effect = [
            bytearray([1, 2]),
            bytearray([3, 4]),
            bytearray([5, 6])
        ]
        mock_socket.return_value = m_socket
        ip = Ip(('example.org', 20000))
        ip.connect()
        self.assertTrue(ip.connected)
        self.assertIsInstance(ip.connection, MagicMock)
        self.assertEqual(ip.get_byte(), 1)
        ip.disconnect()