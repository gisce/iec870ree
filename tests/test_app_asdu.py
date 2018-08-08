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

    def test_M_TI_TA_2_from_hex(self):
        c = app_asdu.M_TI_TA_2()
        c.from_hex(bytes.fromhex("00 64 2a 44 12 08 12"), 1)
        self.assertEqual(c.tiempo.datetime, datetime.datetime(2018, 4, 10, 4))

    def test_P_MP_NA_2_from_hex(self):
        c = app_asdu.P_MP_NA_2()
        c.from_hex(bytes.fromhex("04 fb a2 97 42 24"), 1)
        self.assertEqual(c.codigo_fabricante, 251)
        self.assertEqual(c.codigo_equipo, 608343970)

    def test_C_CI_NU_2(self):
        c = app_asdu.C_CI_NU_2(datetime.datetime(2018, 7, 1, 1),
                               datetime.datetime(2018, 8, 1, 0))
        self.assertEqual(c.to_bytes(), bytearray(bytes.fromhex("01 08 00 01 e1 07 12 00 00 61 08 12")))
        self.assertEqual(c.length, 21)

    def test_C_CI_NU_2_from_hex(self):
        c = app_asdu.C_CI_NU_2()
        c.from_hex(bytes.fromhex("01 08 00 01 e1 07 12 00 00 61 08 12"), 1)
        self.assertEqual(c.primer_integrado, 1)
        self.assertEqual(c.ultimo_integrado, 8)
        self.assertEqual(c.tiempo_inicial.datetime, datetime.datetime(2018, 7, 1, 1))
        self.assertEqual(c.tiempo_final.datetime, datetime.datetime(2018, 8, 1, 0))

    def test_M_IT_TK_2_from_hex(self):
        c = app_asdu.M_IT_TK_2()
        self.assertEqual(c.valores, [])
        self.assertEqual(c.tiempo, None)
        c.from_hex(bytes.fromhex("01 04 00 00 00 00 02 00 00 00 00 00 03 1b 00 00 00 00 04 00 00 00 00 00 05 00 00 00 00 00 06 00 00 00 00 00 07 00 00 00 00 80 08 00 00 00 00 80 00 81 e1 07 12"), 8)

        self.assertEqual(c.valores, [(1, 4, 0), (2, 0, 0), (3, 27, 0), (4, 0, 0)
            , (5, 0, 0), (6, 0, 0), (7, 0, 128), (8, 0, 128)])
        self.assertEqual(c.tiempo.datetime, datetime.datetime(2018, 7, 1, 1))
