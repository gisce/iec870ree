import bitstring
import struct
import datetime


__all__ = [
    'C_AC_NA_2',
    'C_CI_NU_2',
    'C_FS_NA_2',
    'C_TI_NA_2',
    'C_RD_NA_2',
    'M_IT_TK_2',
    'M_TI_TA_2',
    'P_MP_NA_2'
]


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

    @property
    def values(self):
        return "\n".join([
            "    {}: {}".format(k, v) for k,v in vars(self).items()
        ])
    
    def __repr__(self):
        return '\n'.join([
            " -- {class_name} Begin --",
            "{values}",
            " -- {class_name} End --"
        ]).format(
            class_name=self.__class__.__name__,
            values=self.values
        )


class C_TI_NA_2(BaseAppAsdu):
    """
    Leer fecha y hora actuales
    """
    type = 103
    
    def to_bytes(self):
        return bytes()

    def from_hex(self, data, cualificador_ev):
        pass

class P_MP_NA_2(BaseAppAsdu):
    """
    Leer el código de fabricante e identificador de equipo
    """
    type = 71
    data_length = 0x06

    def __init__(self):
        self.codigo_fabricante = None
        self.codigo_equipo = None

    def to_bytes(self):
        return bytes()

    def from_hex(self, data, cualificador_ev):
        self.codigo_fabricante = struct.unpack("B", data[1:2])[0]
        self.codigo_equipo = struct.unpack("I", data[2:6])[0]


class M_TI_TA_2(BaseAppAsdu):
    """
    Fecha y hora actuales
    """
    type = 72

    def __init__(self):
        self.tiempo = None

    def from_hex(self, data, cualificador_ev):
        self.tiempo = TimeA()
        self.tiempo.from_hex(data)


class C_RD_NA_2(BaseAppAsdu):
    """
    Leer el código de fabricante e identificador de equipo
    """
    type = 100
    causa_tm = 5
    
    def to_bytes(self):
        return bytes()

    def from_hex(self, data, cualificador_ev):
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


class C_FS_NA_2(BaseAppAsdu):
    """
    Finalizar sesión
    """

    type = 187

    def from_hex(self, data, cualificador_ev):
        pass

    @property
    def length(self):
        return 0x09

    def to_bytes(self):
        return bytes()


class C_CI_NU_2(BaseAppAsdu):
    type = 123

    def __init__(self, start_date=datetime.datetime.now(),
                 end_date=datetime.datetime.now()):
        self.primer_integrado = 1
        self.ultimo_integrado = 8
        self.tiempo_inicial = TimeA(start_date)
        self.tiempo_final = TimeA(end_date)

    def from_hex(self, data, cualificador_ev):
        self.primer_integrado = struct.unpack("B", data[0:1])[0]
        self.ultimo_integrado = struct.unpack("B", data[1:2])[0]
        self.tiempo_inicial.from_hex(data[2:7])
        self.tiempo_final.from_hex(data[7:12])

    @property
    def length(self):
        return 0x15

    def to_bytes(self):
        response = bytearray()
        response.extend(struct.pack("B", self.primer_integrado))
        response.extend(struct.pack("B", self.ultimo_integrado))
        response.extend(self.tiempo_inicial.to_bytes())
        response.extend(self.tiempo_final.to_bytes())
        return response


class M_IT_TK_2(BaseAppAsdu):
    type = 11

    def __init__(self):
        self.valores = []
        self.tiempo = None
        pass

    def from_hex(self, data, cualificador_ev):
        for i in range(0, cualificador_ev):
            position = i * 6  # 1 byte de typo 4 de medida 1 de cualificador
            # total integrado (4 octetos de energía+1 octeto con cualificadores
            # y número de secuencia), para cada uno de los totales.
            direccion_objeto = struct.unpack("B", data[position:position+1])[0]
            total_integrado = struct.unpack("I",
                                            data[position + 1:position + 5])[0]
            cualificador = struct.unpack("B", data[position+5:position+6])[0]
            self.valores.append((direccion_objeto,
                                 total_integrado, cualificador))
        position = position + 6
        # ok, ahora el tiempo
        self.tiempo = TimeA()
        self.tiempo.from_hex(data[position:position+5])


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
        thedata = bitstring.BitArray(bytes([self.SU]))
        response = response + thedata[-1:]
        thedata = bitstring.BitArray(bytes([self.dayofmonth]))
        response = response + thedata[-1:-6:-1]
        thedata = bitstring.BitArray(bytes([self.dayofweek]))
        response = response + thedata[-1:-4:-1]
        thedata = bitstring.BitArray(bytes([self.month]))
        response = response + thedata[-1:-5:-1]
        thedata = bitstring.BitArray(bytes([self.ETI]))
        response = response + thedata[-1:-3:-1]
        thedata = bitstring.BitArray(bytes([self.PTI]))
        response = response + thedata[-1:-3:-1]
        thedata = bitstring.BitArray(bytes([self.year]))
        response = response + thedata[-1:-8:-1]
        thedata = bitstring.BitArray(bytes([self.RES2]))
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
