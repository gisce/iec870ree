from . import context
import unittest

import reeprotocol

class TestASDUParser(unittest.TestCase):
    def test_fixed_asdu(self):
        parser = reeprotocol.asdu.ASDUParser()

        fixed_asdu = bytes.fromhex("10 00 0c 87 93 16")
        for b in fixed_asdu:
            asdu = parser.appendAndReturnIfFinished(b)

        self.assertIsInstance(asdu, reeprotocol.asdu.FixedAsdu)

class TestFixedAsdu(unittest.TestCase):
    
    def test_create_asdu1(self):
        fixed_asdu = bytes.fromhex("10 00 0c 87 93 16")
        asdu = reeprotocol.asdu.FixedAsdu()
        for b in fixed_asdu: asdu.append(b)
        self.assertTrue(asdu.completed)
        asdu.generate()
        self.assertEqual(asdu.buffer, fixed_asdu)

    def test_create_asdu2(self):
        fixed_asdu = bytes.fromhex("10 49 0c 87 DC 16")
        asdu = reeprotocol.asdu.FixedAsdu()
        for b in fixed_asdu: asdu.append(b)
        self.assertTrue(asdu.completed)
        asdu.generate()
        self.assertEqual(asdu.buffer, fixed_asdu)

    def test_generate_fixed(self):
        asdu = reeprotocol.asdu.FixedAsdu()
        asdu.c.res = 0
        asdu.c.prm = 1
        asdu.c.fcb = 0
        asdu.c.fcv = 0
        asdu.c.cf = 9
        asdu.der = 34572
        asdu.generate()
        fixed_asdu = bytes.fromhex("10 49 0c 87 DC 16")
        self.assertEqual(asdu.buffer, fixed_asdu)
