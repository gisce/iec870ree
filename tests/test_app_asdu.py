from . import context
import unittest
import datetime
from reeprotocol import app_asdu
from reeprotocol.app_asdu import IntegratedTotals, BillingRegister


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

    def test_C_CI_NT_2(self):
        c = app_asdu.C_CI_NT_2(datetime.datetime(2018, 7, 1, 1),
                               datetime.datetime(2018, 8, 1, 0))
        self.assertEqual(c.to_bytes(), bytearray(bytes.fromhex("01 08 00 01 e1 07 12 00 00 61 08 12")))
        self.assertEqual(c.length, 21)

    def test_C_CI_NT_2_from_hex(self):
        c = app_asdu.C_CI_NT_2()
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

        self.assertEqual(c.valores, [IntegratedTotals(address=1, total=4, quality=0, datetime=datetime.datetime(2018, 7, 1, 1, 0)), IntegratedTotals(address=2, total=0, quality=0, datetime=datetime.datetime(2018, 7, 1, 1, 0)), IntegratedTotals(address=3, total=27, quality=0, datetime=datetime.datetime(2018, 7, 1, 1, 0)), IntegratedTotals(address=4, total=0, quality=0, datetime=datetime.datetime(2018, 7, 1, 1, 0)), IntegratedTotals(address=5, total=0, quality=0, datetime=datetime.datetime(2018, 7, 1, 1, 0)), IntegratedTotals(address=6, total=0, quality=0, datetime=datetime.datetime(2018, 7, 1, 1, 0)), IntegratedTotals(address=7, total=0, quality=128, datetime=datetime.datetime(2018, 7, 1, 1, 0)), IntegratedTotals(address=8, total=0, quality=128, datetime=datetime.datetime(2018, 7, 1, 1, 0))])
        self.assertEqual(c.tiempo.datetime, datetime.datetime(2018, 7, 1, 1))

    def test_C_TA_VM_2(self):
        c = app_asdu.C_TA_VM_2(datetime.datetime(2018, 7, 1, 1),
                               datetime.datetime(2018, 8, 1, 0))
        self.assertEqual(c.to_bytes(), bytearray(
            bytes.fromhex("00 01 e1 07 12 00 00 61 08 12")))
        self.assertEqual(c.length, 19)

    def test_C_TA_VM_2_from_hex(self):
        c = app_asdu.C_TA_VM_2()
        c.from_hex(bytes.fromhex("00 01 e1 07 12 00 00 61 08 12"), 1)
        self.assertEqual(c.start_date.datetime, datetime.datetime(2018, 7, 1, 1))
        self.assertEqual(c.end_date.datetime, datetime.datetime(2018, 8, 1, 0))

    def test_M_TA_VX_2_from_hex(self):
        c = app_asdu.M_TA_VX_2()
        self.assertEqual(c.valores, [])
        c.from_hex(bytes.fromhex("14 74 37 3b 00 c0 6e 00 00 00 fb 59 1c 00 ba 5c 00 00 00 e4 bd 05 00 db 06 00 00 00 00 00 00 00 80 00 00 00 00 80 65 01 00 00 0f 87 f2 07 12 00 00 00 00 00 80 00 80 e1 07 12 00 80 61 08 12"), 1)
        print(c.valores)
        self.assertEqual(c.valores, [BillingRegister(address=20, active_abs=3880820, active_inc=28352, active_qual=0, reactive_abs_ind=1858043, reactive_inc_ind=23738, reactive_qua_ind=0, reactive_abs_cap=376292, reactive_inc_cap=1755, reactive_qual_cap=0, reserved_7=0, reserved_7_qual=128, reserved_8=0, reserved_8_qual=128, max_power=357, max_power_date=datetime.datetime(2018, 7, 18, 7, 15), max_power_qual=0, excess_power=0, ecxess_power_qual=128, date_start=datetime.datetime(2018, 7, 1, 0, 0), date_end=datetime.datetime(2018, 8, 1, 0, 0))])
