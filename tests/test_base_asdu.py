from . import context
import unittest

import reeprotocol

class TestASDUParser(unittest.TestCase):
    def test_fixed_asdu(self):
        parser = reeprotocol.base_asdu.AsduParser()

        fixed_asdu = bytearray.fromhex("10 00 0c 87 93 16")
        for b in fixed_asdu:
            asdu = parser.append_and_get_if_completed(b)

        self.assertIsInstance(asdu, reeprotocol.base_asdu.FixedAsdu)

    def test_variable_asdu(self):
        var_asdu = bytearray.fromhex("68 0D 0D 68"+"73"
                                 + "0C 87" + "B7 01 06"
                                 + "01 00" + "00" +"07 00 00 00"
                                 +"CC"+ "16")
        parser = reeprotocol.base_asdu.AsduParser()
        for b in var_asdu:
            asdu = parser.append_and_get_if_completed(b)
        self.assertIsInstance(asdu, reeprotocol.base_asdu.VariableAsdu)
        asdurepresentation = str(asdu)

class TestFixedAsdu(unittest.TestCase):
    
    def test_create_asdu1(self):
        fixed_asdu = bytearray.fromhex("10 00 0c 87 93 16")
        asdu = reeprotocol.base_asdu.FixedAsdu()
        for b in fixed_asdu: asdu.append(b)
        self.assertTrue(asdu.completed)
        asdu.generate()
        self.assertEqual(asdu.buffer, fixed_asdu)

    def test_create_asdu2(self):
        fixed_asdu = bytearray.fromhex("10 49 0c 87 DC 16")
        asdu = reeprotocol.base_asdu.FixedAsdu()
        for b in fixed_asdu: asdu.append(b)
        self.assertTrue(asdu.completed)
        asdu.generate()
        self.assertEqual(asdu.buffer, fixed_asdu)

    def test_generate_fixed(self):
        asdu = reeprotocol.base_asdu.FixedAsdu()
        asdu.c.res = 0
        asdu.c.prm = 1
        asdu.c.fcb = 0
        asdu.c.fcv = 0
        asdu.c.cf = 9
        asdu.der = 34572
        asdu.generate()
        fixed_asdu = bytearray.fromhex("10 49 0c 87 DC 16")
        self.assertEqual(asdu.buffer, fixed_asdu)

class TestVariableAsdu(unittest.TestCase):
    def test_generate_variable(self):
        asdu = reeprotocol.base_asdu.VariableAsdu()
        asdu.c.res = 0
        asdu.c.prm = 1
        asdu.c.fcb = 1
        asdu.c.fcv = 1
        asdu.c.cf = 3
        asdu.der = 34572
        asdu.tipo = 183
        asdu.cualificador_ev = 1
        asdu.causa_tm = 6
        asdu.dir_pm = 1
        asdu.dir_registro = 0

        #asdu.content = ree.C_AC_NA_2(8)
        asdu.data = bytearray.fromhex('08 00 00 00')
        asdu.generate()
        var_asdu = bytearray.fromhex("68 0d 0d 68 73 0c 87 b7 01 06 01 00 00"
                                 "08 00 00 00"
                                 "cd 16")
        self.assertEqual(asdu.buffer, var_asdu)

