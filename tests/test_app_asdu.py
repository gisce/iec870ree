from . import context
import unittest
import datetime
from pytz import timezone
from iec870ree import app_asdu
from iec870ree.app_asdu import IntegratedTotals, BillingRegister

import logging
logging.basicConfig(level=logging.DEBUG)

TIMEZONE = timezone('Europe/Madrid')


def localize(dt):
    return TIMEZONE.localize(dt)


class TestAppAsdu(unittest.TestCase):

    def test_registry(self):
        t = app_asdu.AppAsduRegistry.types[app_asdu.C_AC_NA_2.type]
        self.assertEqual(t, app_asdu.C_AC_NA_2)

    def test_C_AC_NA_2(self):
        c = app_asdu.C_AC_NA_2(7)
        self.assertEqual(c.to_bytes(), bytearray.fromhex("07 00 00 00"))
        self.assertEqual(c.length, 13)

    def test_C_AC_NA_2_from_hex(self):
        c = app_asdu.C_AC_NA_2()
        c.from_hex(bytearray.fromhex("07 00 00 00"), None)
        self.assertEqual(c.clave, 7)
        
        
    def test_time_a_from_hex(self):
        tiempo = app_asdu.TimeA()

        #segun el pdf 18/09/09 00:01:00
        tiempo.from_hex(bytearray.fromhex("01 0012 0909"))
        print(tiempo)
        self.assertEqual(
            tiempo.datetime,
            localize(datetime.datetime(2009,9,18,0,1))
        )

        #segun el pdf 7/02/10 11:00
        tiempo.from_hex(bytearray.fromhex("00 0b 07 02 0a"))
        print(tiempo)
        self.assertEqual(
            tiempo.datetime,
            localize(datetime.datetime(2010,2,7,11,0))
        )

    def test_time_b_from_hex(self):
        tiempo = app_asdu.TimeB()

        # al voltant del 2019-08-28 11:40
        tiempo.from_hex(bytearray.fromhex("00 90 25 8b 7c 08 13"))
        print(tiempo)
        self.assertEqual(
            tiempo.datetime,
            localize(datetime.datetime(2019, 8, 28, 11, 37, 36, 0))
        )

        tiempo.from_hex(bytearray.fromhex("0a 2a 10 0b e7 02 0a"))
        print(tiempo)
        self.assertEqual(
            tiempo.datetime,
            localize(datetime.datetime(2010, 2, 7, 11, 16, 10, 522000))
        )

    def test_time_a_to_bytes(self):
        d = datetime.datetime(2017, 1, 2, 3, 4)
        tiempo = app_asdu.TimeA(d)
        thebytes = tiempo.to_bytes()

        tiempo2 = app_asdu.TimeA()
        tiempo2.from_hex(thebytes)
        self.assertEqual(tiempo2.datetime, localize(d))

    def test_time_a_StoW_to_bytes(self):
        d = datetime.datetime(2019, 10, 27, 2, 0, 0)
        ds = TIMEZONE.localize(d, is_dst=True)
        dw = TIMEZONE.localize(d, is_dst=False)

        # Change hour Summer
        tiempo_summer = app_asdu.TimeA(ds)
        self.assertEqual(tiempo_summer.SU, 1)
        thebytes = tiempo_summer.to_bytes()
        print(thebytes)
        t2s = app_asdu.TimeA()
        t2s.from_hex(thebytes)
        self.assertGreater(t2s.datetime.dst().seconds, 0)
        self.assertEqual(t2s.datetime, ds)

        # Change hour Winter
        tiempo_winter = app_asdu.TimeA(dw)
        self.assertEqual(tiempo_winter.SU, 0)
        thebytes = tiempo_winter.to_bytes()
        t2w = app_asdu.TimeA()
        t2w.from_hex(thebytes)
        self.assertEqual(t2w.datetime.dst().seconds, 0)
        self.assertEqual(t2w.datetime, dw)

    def test_time_b_to_bytes(self):
        d = datetime.datetime(2017, 1, 2, 3, 4, 5, 678000)
        tiempo = app_asdu.TimeB(d)
        thebytes = tiempo.to_bytes()
        print(thebytes)
        tiempo2 = app_asdu.TimeB()
        tiempo2.from_hex(thebytes)
        self.assertEqual(tiempo2.datetime, localize(d))

    def test_time_b_to_bytes_big(self):
        d = datetime.datetime(2017, 11, 29, 23, 58, 59, 978000)
        tiempo = app_asdu.TimeB(d)
        thebytes = tiempo.to_bytes()
        print(thebytes)
        tiempo2 = app_asdu.TimeB()
        tiempo2.from_hex(thebytes)
        self.assertEqual(tiempo2.datetime, localize(d))

    def test_C_CS_TA_2_from_hex(self):
        sincrotime = datetime.datetime(2018, 8, 18, 4, 42, 25)
        c = app_asdu.C_CS_TA_2(sincrotime)
        c.from_hex(bytearray.fromhex("00 64 2a 44 12 08 12"), 1)
        self.assertEqual(
            c.tiempo.datetime,
            localize(datetime.datetime(2018, 8, 18, 4, 42, 25))
        )

    def test_M_TI_TA_2_from_hex(self):
        c = app_asdu.M_TI_TA_2()
        c.from_hex(bytearray.fromhex("00 64 2a 44 12 08 12"), 1)
        self.assertEqual(
            c.tiempo.datetime,
            localize(datetime.datetime(2018, 8, 18, 4, 42, 25))
        )



    def test_P_MP_NA_2_from_hex(self):
        c = app_asdu.P_MP_NA_2()
        c.from_hex(bytearray.fromhex("04 fb a2 97 42 24"), 1)
        self.assertEqual(c.codigo_fabricante, 251)
        self.assertEqual(c.codigo_equipo, 608343970)

    def test_C_CI_NU_2(self):
        c = app_asdu.C_CI_NU_2(
            datetime.datetime(2018, 7, 1, 1),
            datetime.datetime(2018, 8, 1, 0)
        )
        self.assertEqual(
            c.to_bytes(),
            bytearray(bytearray.fromhex("01 08 00 81 e1 07 12 00 80 61 08 12"))
        )
        self.assertEqual(c.length, 21)

    def test_C_CI_NU_2_from_hex(self):
        c = app_asdu.C_CI_NU_2()
        c.from_hex(bytearray.fromhex("01 08 00 81 e1 07 12 00 80 61 08 12"), 1)
        self.assertEqual(c.primer_integrado, 1)
        self.assertEqual(c.ultimo_integrado, 8)
        self.assertEqual(
            c.tiempo_inicial.datetime,
            localize(datetime.datetime(2018, 7, 1, 1))
        )
        self.assertEqual(
            c.tiempo_final.datetime,
            localize(datetime.datetime(2018, 8, 1, 0))
        )

    def test_C_CI_NT_2(self):
        asdu = app_asdu.C_CI_NT_2(
            datetime.datetime(2018, 7, 1, 1),
            datetime.datetime(2018, 8, 1, 0)
        )
        self.assertEqual(asdu.tiempo_inicial.SU, 1)
        self.assertEqual(asdu.tiempo_final.SU, 1)
        self.assertEqual(
            asdu.to_bytes(),
            bytearray(bytearray.fromhex("01 08 00 81 e1 07 12 00 80 61 08 12"))
        )
        self.assertEqual(asdu.length, 21)

    def test_C_CI_NT_2_from_hex(self):
        c = app_asdu.C_CI_NT_2()
        c.from_hex(bytearray.fromhex("01 08 00 01 e1 07 12 00 80 61 08 12"), 1)
        self.assertEqual(c.primer_integrado, 1)
        self.assertEqual(c.ultimo_integrado, 8)
        self.assertEqual(
            c.tiempo_inicial.datetime,
            localize(datetime.datetime(2018, 7, 1, 1))
        )
        self.assertEqual(
            c.tiempo_final.datetime,
            localize(datetime.datetime(2018, 8, 1, 0))
        )

    def test_M_IT_TK_2_from_hex(self):
        c = app_asdu.M_IT_TK_2()
        self.assertEqual(c.valores, [])
        self.assertEqual(c.tiempo, None)
        c.from_hex(bytearray.fromhex("01 04 00 00 00 00 02 00 00 00 00 00 03 1b 00 00 00 00 04 00 00 00 00 00 05 00 00 00 00 00 06 00 00 00 00 00 07 00 00 00 00 80 08 00 00 00 00 80 00 81 e1 07 12"), 8)

        self.assertEqual(
            c.valores,
            [
                IntegratedTotals(
                    address=1,
                    total=4,
                    quality=0,
                    datetime=localize(datetime.datetime(2018, 7, 1, 1, 0))
                ),
                IntegratedTotals(
                    address=2,
                    total=0,
                    quality=0,
                    datetime=localize(datetime.datetime(2018, 7, 1, 1, 0))
                ),
                IntegratedTotals(
                    address=3,
                    total=27,
                    quality=0,
                    datetime=localize(datetime.datetime(2018, 7, 1, 1, 0))
                ),
                IntegratedTotals(
                    address=4,
                    total=0,
                    quality=0,
                    datetime=localize(datetime.datetime(2018, 7, 1, 1, 0))
                ),
                IntegratedTotals(
                    address=5,
                    total=0,
                    quality=0,
                    datetime=localize(datetime.datetime(2018, 7, 1, 1, 0))
                ),
                IntegratedTotals(
                    address=6,
                    total=0,
                    quality=0,
                    datetime=localize(datetime.datetime(2018, 7, 1, 1, 0))
                ),
                IntegratedTotals(
                    address=7,
                    total=0,
                    quality=128,
                    datetime=localize(datetime.datetime(2018, 7, 1, 1, 0))
                ),
                IntegratedTotals(
                    address=8,
                    total=0,
                    quality=128,
                    datetime=localize(datetime.datetime(2018, 7, 1, 1, 0))
                )
            ]
        )
        self.assertEqual(
            c.tiempo.datetime,
            localize(datetime.datetime(2018, 7, 1, 1))
        )

    def test_C_TA_VM_2(self):
        c = app_asdu.C_TA_VM_2(
            datetime.datetime(2018, 7, 1, 1),
            datetime.datetime(2018, 8, 1, 0)
        )
        print(c.to_bytes())
        self.assertEqual(c.to_bytes(), bytearray(
            bytearray.fromhex("00 81 e1 07 12 00 80 61 08 12")))
        self.assertEqual(c.length, 19)

    def test_C_TA_VM_2_from_hex(self):
        c = app_asdu.C_TA_VM_2()
        c.from_hex(bytearray.fromhex("00 01 e1 07 12 00 00 61 08 12"), 1)
        self.assertEqual(
            c.start_date.datetime,
            localize(datetime.datetime(2018, 7, 1, 1))
        )
        self.assertEqual(
            c.end_date.datetime,
            localize(datetime.datetime(2018, 8, 1, 0))
        )

    def test_M_TA_VX_2_from_hex(self):
        c = app_asdu.M_TA_VX_2()
        self.assertEqual(c.valores, [])
        c.from_hex(bytearray.fromhex("14 74 37 3b 00 c0 6e 00 00 00 fb 59 1c 00 ba 5c 00 00 00 e4 bd 05 00 db 06 00 00 00 00 00 00 00 80 00 00 00 00 80 65 01 00 00 0f 87 f2 07 12 00 00 00 00 00 80 00 80 e1 07 12 00 80 61 08 12"), 1)
        print(c.valores)
        self.assertEqual(
            c.valores,
            [
                BillingRegister(
                    address=20,
                    active_abs=3880820,
                    active_inc=28352,
                    active_qual=0,
                    reactive_abs_ind=1858043,
                    reactive_inc_ind=23738,
                    reactive_qua_ind=0,
                    reactive_abs_cap=376292,
                    reactive_inc_cap=1755,
                    reactive_qual_cap=0,
                    reserved_7=0,
                    reserved_7_qual=128,
                    reserved_8=0,
                    reserved_8_qual=128,
                    max_power=357,
                    max_power_date=localize(
                        datetime.datetime(2018, 7, 18, 7, 15)
                    ),
                    max_power_qual=0,
                    excess_power=0,
                    ecxess_power_qual=128,
                    date_start=localize(
                        datetime.datetime(2018, 7, 1, 0, 0)
                    ),
                    date_end=localize(
                        datetime.datetime(2018, 8, 1, 0, 0)
                    )
                )
            ]
        )
