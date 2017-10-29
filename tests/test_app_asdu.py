from . import context
import unittest
from reeprotocol import app_asdu
import datetime

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
        
        
    def test_time_a_from_hex(self):
        tiempo = app_asdu.TimeA()

        #segun el pdf 18/09/09 00:01:00
        tiempo.from_hex(bytes.fromhex("01 0012 0909"))
        print(tiempo)
        self.assertEqual(tiempo.datetime, datetime.datetime(2009,9,18,0,1))

        #segun el pdf 7/02/10 11:00
        tiempo.from_hex(bytes.fromhex("00 0b 07 02 0a"))
        print(tiempo)
        self.assertEqual(tiempo.datetime, datetime.datetime(2010,2,7,11,0))

    def test_time_a_to_bytes(self):
        d = datetime.datetime(2017,1,2,3,4)
        tiempo = app_asdu.TimeA(d)
        thebytes = tiempo.to_bytes()

        tiempo2 = app_asdu.TimeA()
        tiempo2.from_hex(thebytes)
        self.assertEqual(tiempo2.datetime, d)
