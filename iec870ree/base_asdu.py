import ctypes
import struct
from .app_asdu import AppAsduRegistry


class ParserException (Exception):
    pass


class AsduParser:
    def __init__(self):
        self.asdu = None

    def append_and_get_if_completed(self, bt):
        if self.asdu is None:
            if bt == 255:
                return None
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
        else:
            raise ParserException("Wrong Init Byte {}".format(init_byte))


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
        first byte byte is 0x10
        second byte is C, that it:
           RES -  PRM -  FCB -  FCV -  Function Code
        Third and fourth bytes is DER address
        Fifth byte is checksum
        Sixth byte is "end" 0x16
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
    EXTRA_LENGTH = 6

    def __init__(self):
        self.buffer = bytearray()
        self.length = 0
        self.c = Flags_CampoC()
        self.c.asBytes = 0
        self.der = 0

        self.tipo = 0
        self.cualificador_ev = 0
        self.pn = 0
        self.causa_tm = 0
        self.dir_pm = 0
        self.dir_registro = 0
        self.data = bytearray()
        self.content = None
        self.checksum = 0

    def append(self, bt):
        self.buffer.append(bt)
        if len(self.buffer) == 2:
            self.length = bt

        if (
            len(self.buffer) > 2
            and (len(self.buffer) > self.length + VariableAsdu.EXTRA_LENGTH)
        ):
            raise ParserException("Wrong length in variable length ASDU")

        if self.length != 0 and self.completed:
            self.parse()
            return True

        return False

    @property
    def completed(self):
        return self.length + VariableAsdu.EXTRA_LENGTH == len(self.buffer)

    def parse(self):
        """
        First byte is 0x10
        Second byte is C, that is:
           RES -  PRM -  FCB -  FCV -  Function Code
        Third and fourth bytes is DER address
        Fifth byte is checksum
        Sixth byte is  "end" 0x16
        """
        if self.buffer[0] != VariableAsdu.INIT_BYTE:
            raise ParserException()
        self.length = self.buffer[1]
        self.c.asByte = self.buffer[4]
        self.der = struct.unpack("H", self.buffer[5:7])[0]
        self.tipo = self.buffer[7]
        self.cualificador_ev = self.buffer[8]
        # P/N + causa_tm (6 bits)
        self.pn = (self.buffer[9] & 0x40) >> 6
        self.causa_tm = self.buffer[9] & 0x3f
        self.dir_pm = struct.unpack("H", self.buffer[10:12])[0]
        self.dir_registro = self.buffer[12]
        # data from byte 13 to length - 9
        self.data = self.buffer[13:self.length + 4]
        # TODO WE HAVE TO PARSE DATA TO THE CORRECT TYPE
        if len(self.data):
            self.content = AppAsduRegistry.types[self.tipo]()
            self.content.from_hex(self.data, self.cualificador_ev)
        self.checksum = self.buffer[self.length + 4]
        if self.buffer[self.length + 5] != VariableAsdu.END_BYTE:
            raise ParserException("wrong end byte")
        self.check_checksum()

    def check_checksum(self):
        checksum = 0
        for i in range(4, self.length + 4):
            checksum += self.buffer[i]
        checksum = checksum % 256

        if checksum != self.checksum:
            raise ParserException("wrong checksum")

    def generate(self):
        del self.buffer[:]

        if self.content is None:
            self.length = len(self.data) + 9
        else:
            self.length = self.content.length

        self.buffer.append(VariableAsdu.INIT_BYTE)
        self.buffer.extend(struct.pack("B", self.length))
        self.buffer.extend(struct.pack("B", self.length))
        self.buffer.append(VariableAsdu.INIT_BYTE)
        self.buffer.append(self.c.asByte)
        self.buffer.extend(struct.pack("H", self.der))
        if self.content is not None:
            self.tipo = self.content.type
        self.buffer.extend(struct.pack("B", self.tipo))
        self.buffer.extend(struct.pack("B", self.cualificador_ev))
        self.buffer.extend(struct.pack("B", self.causa_tm))
        self.buffer.extend(struct.pack("H", self.dir_pm))
        self.buffer.extend(struct.pack("B", self.dir_registro))
        # TODO, THINK A BIT MORE ON THIS
        if self.content is None:
            self.buffer.extend(self.data)
        else:
            self.buffer.extend(self.content.to_bytes())
        self.checksum = 0
        for i in range(4, self.length + 4):
            self.checksum += self.buffer[i]
        self.checksum = self.checksum % 256
        self.buffer.extend(struct.pack("B", self.checksum))
        self.buffer.append(VariableAsdu.END_BYTE)

    def __repr__(self):
        output = "----- VariableAsdu Begin -----\n"
        output += " length: " + str(self.length) + "\n"
        output += (" RES: " + str(self.c.res) + " PRM: "+ str(self.c.prm)
                   + " FCB: " + str(self.c.fcb) + " FCV: " + str(self.c.fcv) 
                   + " CF(cod. funcion): " + str(self.c.cf) + "\n")
        output +=  " DER: " + str(self.der) + "\n"
        output +=  " TIPO: " + str(self.tipo) + " " + hex(self.tipo) + "\n"
        output +=  " cualificador estructura variable: " + str(self.cualificador_ev) + "\n"
        output += " causa transmision: " + str(self.causa_tm) + " " + hex(self.causa_tm) + " P/N: " + str(self.pn) + "\n"
        output += " direccion punto medida: " + str(self.dir_pm) + "\n"
        output += " direccion registro: " + str(self.dir_registro) + "\n"
        output += " CONTENIDO: " + (":".join("%02x" % b for b in self.data)) + "\n"
        output += str(self.content) + "\n"
        output += " checksum: " + str(self.checksum) + " " +hex(self.checksum) +  "\n"
        output += " " + (":".join("%02x" % b for b in self.buffer)) + "\n"
        output += "----- VariableAsdu End -----"
        return output
        

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
