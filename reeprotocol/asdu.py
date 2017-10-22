import ctypes
import struct


class ParserException(Exception):
    pass


class ASDUParser:
    def __init__(self):
        self.asdu = None

    def appendAndReturnIfFinished(self, bt):
        if self.asdu is None:
            self.create_asdu(bt)

        if self.asdu.append(bt):
            last_asdu = self.asdu
            self.asdu = None
            return last_asdu

    def create_asdu(self, init_byte):
        if init_byte == FixedAsdu.INIT_BYTE:
            self.asdu = FixedAsdu()
        elif init_byte == VariableAsdu.INIT_BYTE:
            self.asdu = VariableAsdu()


class FixedAsdu:
    INIT_BYTE = 0x10
    END_BYTE = 0x16
    LENGTH = 6

    def __init__(self):
        self.buffer = bytearray()
        self.c = Flags_CampoC()
        self.c.asBytes = 0
        self.der = 0
        self.checksum = 0

    def append(self, bt):
        self.buffer.append(bt)
        if len(self.buffer) > FixedAsdu.LENGTH:
            raise ParserException("Fixed asdu with more than 6 bytes")

        if self.completed:
            self.parse()
            return True
        return False

    @property
    def completed(self):
        if len(self.buffer) == FixedAsdu.LENGTH:
            return True
        return False

    def parse(self):
        """
        el primer byte es 0x10
        el segundo byte es C, que es:
           RES -  PRM -  FCB -  FCV -  Codigo de funcion
        el tercer y cuarto byes es la direcci'on der
        el quinto byte es el checksum
        el sexto es el "end" 0x16
        """
        if self.buffer[0] != FixedAsdu.INIT_BYTE:
            raise ParserException()
        self.c = Flags_CampoC()
        self.c.asByte = self.buffer[1]
        self.der = struct.unpack("H", self.buffer[2:4])[0]
        self.checksum = self.buffer[4]
        self.check_checksum()

    def check_checksum(self):
        checksum = (self.buffer[1] + self.buffer[2] + self.buffer[3]) % 256
        if checksum != self.checksum:
            raise ParserException("wrong checksum")

    def generate(self):
        del self.buffer[:]
        self.buffer.append(FixedAsdu.INIT_BYTE)
        self.buffer.append(self.c.asByte)
        self.buffer.extend(struct.pack("H", self.der))
        self.checksum = (self.buffer[1] + self.buffer[2]
                         + self.buffer[3]) % 256
        self.buffer.extend(struct.pack("B", self.checksum))
        self.buffer.append(FixedAsdu.END_BYTE)

    def __repr__(self):
        output = "----- FixedAsdu Begin -----\n"
        output += (" RES: " + str(self.c.res) + " PRM: " + str(self.c.prm)
                   + " FCB: " + str(self.c.fcb) + " FCV: " + str(self.c.fcv)
                   + " CF(cod. funcion): " + str(self.c.cf) + "\n")
        output += " DER: " + str(self.der) + "\n"
        output += " checksum: " + str(self.checksum)
        output += " " + hex(self.checksum) + "\n"
        output += " " + (":".join("%02x" % b for b in self.buffer)) + "\n"
        output += "----- FixedAsdu End -----"
        return output


class VariableAsdu:
    INIT_BYTE = 0x68
    END_BYTE = 0x16


c_uint8 = ctypes.c_uint8


class Flags_CampoC_bits(ctypes.BigEndianStructure):
    _fields_ = [
        ("res", c_uint8, 1),
        ("prm", c_uint8, 1),
        ("fcb", c_uint8, 1),
        ("fcv", c_uint8, 1),
        ("cf", c_uint8, 4)
    ]


class Flags_CampoC(ctypes.Union):
    _fields_ = [
        ("b", Flags_CampoC_bits),
        ("asByte", c_uint8)
    ]
    _anonymous_ = ("b")
