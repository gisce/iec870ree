import bitstring
import struct
import datetime


class AppAsduRegistry(type):
    types = dict()

    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        AppAsduRegistry.register_class(cls)
        return cls

    @staticmethod
    def register_class(cls):
        if cls.__name__ == 'BaseAppAsdu':
            return
        AppAsduRegistry.types[cls.type] = cls


class BaseAppAsdu(metaclass=AppAsduRegistry):
    pass


class C_AC_NA_2(BaseAppAsdu):
    """
    used to send the password of the thing
    """
    type = 183

    def __init__(self, clave=0):
        self.clave = clave

    def from_hex(self, data, cualificador_ev):
        self.clave = struct.unpack("I", data)[0]

    @property
    def length(self):
        return 0x0d

    def to_bytes(self):
        return struct.pack("I", self.clave)

    def __repr__(self):
        output = " -- C_AC_NA_2 Begin -- \n"
        output += "  clave: " + str(self.clave) + "\n"
        output += " -- C_AC_NA_2 End \n"
        return output


class C_FS_NA_2:
    type = 187

    def from_hex(self, data, cualificador_ev):
        pass

    @property
    def length(self):
        return 0x0d

    def to_bytes(self):
        return bytes()

    def __repr__(self):
        output = " -- C_FS_NA_2 Begin -- \n"
        output += " -- C_FS_NA_2 End \n"
        return output


class TimeA():

    def __init__(self, fecha=datetime.datetime.now()):
        self.minute = fecha.minute  # UI6
        self.TIS = 0  # BS1 TIS=tariff information switch
        self.IV = 0  # BS1 IV=invalid
        self.hour = fecha.hour  # UI5
        self.RES1 = 0  # BS2 RES1=reserve 1
        self.minute = fecha.minute  # UI6
        self.TIS = 0  # BS1 TIS=tariff information switch
        self.IV = 0  # BS1 IV=invalid
        self.hour = fecha.hour  # UI5
        self.RES1 = 0  # BS2 RES1=reserve 1
        # BS1 SUMMER TIME
        # (0 STANDARD TIME, 1 summer time or daylight saving time)
        self.SU = 0
        self.dayofmonth = fecha.day  # UI5
        self.dayofweek = fecha.weekday() + 1  # UI3
        self.month = fecha.month  # UI4
        self.ETI = 0  # UI2 ETI=energy tariff information
        self.PTI = 0  # UI2 PTI=power tariff information
        self.year = fecha.year % 100  # UI7
        self.RES2 = 0  # BS1

    def from_hex(self, data):
        reversed_bytes = bitstring.BitArray(bytes(reversed(data)))
        reversed_bits = bitstring.BitStream(reversed(reversed_bytes))
        self.minute = bitstring.BitArray(reversed(reversed_bits.read(6))).uint
        self.TIS = reversed_bits.read(1).uint
        self.IV = reversed_bits.read(1).uint
        self.hour = bitstring.BitArray(reversed(reversed_bits.read(5))).uint
        self.RES1 = bitstring.BitArray(reversed(reversed_bits.read(2))).uint
        self.SU = reversed_bits.read(1).uint
        self.dayofmonth = bitstring.BitArray(reversed(reversed_bits.read(5)))\
                                   .uint
        self.dayofweek = bitstring.BitArray(reversed(reversed_bits.read(3)))\
                                  .uint
        self.month = bitstring.BitArray(reversed(reversed_bits.read(4))).uint
        self.ETI = bitstring.BitArray(reversed(reversed_bits.read(2))).uint
        self.PTI = bitstring.BitArray(reversed(reversed_bits.read(2))).uint
        self.year = bitstring.BitArray(reversed(reversed_bits.read(7))).uint
        self.RES2 = reversed_bits.read(1).uint
        
    def to_bytes(self):
        response = bitstring.BitArray()
        thedata = bitstring.BitArray(bytes([self.minute]))
        response = response + thedata[-1:-7:-1]
        thedata = bitstring.BitArray(bytes([self.TIS]))
        response = response + thedata[-1:]
        thedata = bitstring.BitArray(bytes([self.IV]))
        response = response + thedata[-1:]
        thedata = bitstring.BitArray(bytes([self.hour]))
        response = response + thedata[-1:-6:-1]
        thedata = bitstring.BitArray(bytes([self.RES1]))
        response = response + thedata[-1:-3:-1]
        thedata = bitstring.BitArray (bytes([self.SU]))
        response = response + thedata[-1:]
        thedata = bitstring.BitArray (bytes([self.dayofmonth]))
        response = response + thedata[-1:-6:-1]
        thedata = bitstring.BitArray (bytes([self.dayofweek]))
        response = response + thedata[-1:-4:-1]
        thedata = bitstring.BitArray (bytes([self.month]))
        response = response + thedata[-1:-5:-1]
        thedata = bitstring.BitArray (bytes([self.ETI]))
        response = response + thedata[-1:-3:-1]
        thedata = bitstring.BitArray (bytes([self.PTI]))
        response = response + thedata[-1:-3:-1]
        thedata = bitstring.BitArray (bytes([self.year]))
        response = response + thedata[-1:-8:-1]
        thedata = bitstring.BitArray (bytes([self.RES2]))
        response = response + thedata[-1:]
        response = response[::-1]
        inbytes = response.tobytes()[::-1]
        return inbytes


    @property
    def datetime(self):
        year = self.year+2000
        return datetime.datetime(year, self.month, self.dayofmonth,
                                 self.hour, self.minute)

    def __repr__(self):
        output = "  -- TiempoA Begin -- \n"
        output += "    minute: " + str(self.minute) + "\n"
        output += "    TIS: " + str(self.TIS) + "\n"
        output += "    IV: " + str(self.IV) + "\n"
        output += "    hour: " + str(self.hour) + "\n"
        output += "    RES1: " + str(self.RES1) + "\n"
        output += "    SU: " + str(self.SU) + "\n"
        output += "    dayofmonth: " + str(self.dayofmonth) + "\n"
        output += "    dayofweek: " + str(self.dayofweek) + "\n"
        output += "    month: " + str(self.month) + "\n"
        output += "    ETI: " + str(self.ETI) + "\n"
        output += "    PTI: " + str(self.PTI) + "\n"
        output += "    year: " + str(self.year) + "\n"
        output += ("    content: "
                   + (":".join("%02x" % b for b in self.to_bytes())) + "\n")
        output += "    datetime: " + str(self.datetime) + "\n"
        output += "  -- TiempoA End \n"
        return output
