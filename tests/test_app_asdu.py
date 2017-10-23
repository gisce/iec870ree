from . import context
import unittest
from reeprotocol import app_asdu

class TestAppAsdu(unittest.TestCase):

    def test_registry(self):
        t = app_asdu.AppAsduRegistry.types[app_asdu.C_AC_NA_2.type]
        self.assertEqual(t, app_asdu.C_AC_NA_2)

    def test_C_AC_NA_2(self):
        c = app_asdu.C_AC_NA_2(7)
        self.assertEqual(c.to_bytes(), bytes.fromhex("07 00 00 00"))
        self.assertEqual(c.length, 13)

    def test_C_AC_NA_2_from_hex(self):
        c = app_asdu.C_AC_NA_2()
        c.from_hex(bytes.fromhex("07 00 00 00"), None)
        self.assertEqual(c.clave, 7)
        
        
