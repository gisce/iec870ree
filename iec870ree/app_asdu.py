# -*- coding: utf-8 -*-
import bitstring
import struct
import datetime
from collections import namedtuple

from six import with_metaclass


__all__ = [
    'C_AC_NA_2',
    'C_CI_NU_2',
    'C_CI_NT_2',
    'C_FS_NA_2',
    'C_TI_NA_2',
    'C_RD_NA_2',
    'M_IT_TG_2',
    'M_IT_TK_2',
    'M_TI_TA_2',
    'P_MP_NA_2',
    'C_TA_VC_2',
    'C_TA_VM_2',
    'C_CB_UN_2',
    'M_TA_VC_2',
    'M_TA_VM_2',
    'M_IB_TK_2',
    'C_CS_TA_2',
    'C_PC_NA_2',
    'M_PC_NA_2',
    'C_CH_TA_2',
    'M_CH_TA_2'
]

BillingRegister = namedtuple('BillingRegister', ['address', 'active_abs',
    'active_inc', 'active_qual', 'reactive_abs_ind', 'reactive_inc_ind',
    'reactive_qua_ind', 'reactive_abs_cap', 'reactive_inc_cap',
    'reactive_qual_cap', 'reserved_7', 'reserved_7_qual', 'reserved_8',
    'reserved_8_qual', 'max_power', 'max_power_date', 'max_power_qual',
    'excess_power', 'ecxess_power_qual', 'date_start', 'date_end'])

IntegratedTotals = namedtuple('IntegratedTotals', ['address', 'total', 'quality'
                              , 'datetime'])

ContractedPower = namedtuple('ContractedPower', ['address', 'power'])

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


class BaseAppAsdu(with_metaclass(AppAsduRegistry)):

    data_length = 0
    type = 0

    @property
    def length(self):
        return self.data_length + 0x09

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
    causa_tm = 5
    
    def to_bytes(self):
        return bytes()

    def from_hex(self, data, cualificador_ev):
        pass


class M_TI_TA_2(BaseAppAsdu):
    """
    Fecha y hora actuales
    """
    type = 72
    causa_tm = 5

    def __init__(self):
        self.tiempo = None

    def from_hex(self, data, cualificador_ev):
        self.tiempo = TimeB()
        self.tiempo.from_hex(data)


class C_CS_TA_2(BaseAppAsdu):
    """
    Modificación Fecha y Hora
    """
    type = 181
    causa_tm = 6
    data_length = 0x06

    def __init__(self, sincrotime=datetime.datetime.now()):
        self.tiempo = TimeB(sincrotime)

    def from_hex(self, data, cualificador_ev):
        self.tiempo = TimeB()
        self.tiempo.from_hex(data)

    def to_bytes(self):
        response = bytearray()
        response.extend(self.tiempo.to_bytes())
        return response

    @property
    def length(self):
        return 0x10


class C_RD_NA_2(BaseAppAsdu):
    """
    Leer identificador de fabricante y equipo
    """
    type = 100
    causa_tm = 5

    def to_bytes(self):
        return bytes()

    def from_hex(self, data, cualificador_ev):
        pass


class P_MP_NA_2(BaseAppAsdu):
    """
    Identificador del fabricante y equipo
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


class C_AC_NA_2(BaseAppAsdu):
    """
    used to send the password of the thing
    """
    type = 183
    data_length = 0x06

    def __init__(self, clave=0):
        self.clave = clave

    def from_hex(self, data, cualificador_ev):
        self.clave = struct.unpack("I", data)[0]

    def to_bytes(self):
        return struct.pack("I", self.clave)

    @property
    def length(self):
        return 0x0d


class C_CH_TA_2(BaseAppAsdu):
    """
    Solicitar fechas de cambio de hora
    """
    type = 185
    causa_tm = 5

    def to_bytes(self):
        return bytes()

    def from_hex(self, data, cualificador_ev):
        pass


class M_CH_TA_2(BaseAppAsdu):
    """
    Leer fechas de cambio de hora
    """
    type = 131
    causa_tm = 5

    def to_bytes(self):
        return bytes()

    def __init__(self):
        self.tiempo_W2S = None
        self.tiempo_S2W = None

    def from_hex(self, data, cualificador_ev):
        self.tiempo_W2S = TimeA()
        self.tiempo_W2S.from_hex(data[0:5])
        self.tiempo_S2W = TimeA()
        self.tiempo_S2W.from_hex(data[5:10])


class C_FS_NA_2(BaseAppAsdu):
    """
    Finalizar sesión
    """
    type = 187

    def from_hex(self, data, cualificador_ev):
        pass

    def to_bytes(self):
        return bytes()


class C_CI_NX_2(BaseAppAsdu):
    """
    Class for the C_CI_NT_2(122) and C_CI_NU_2(123) ASDUs

    Leer totales integrados operacionales repuestos periódicamente por intervalo
    de tiempo y rango de direcciones
    """
    data_length = 0x06
    causa_tm = 6

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

    def to_bytes(self):
        response = bytearray()
        response.extend(struct.pack("B", self.primer_integrado))
        response.extend(struct.pack("B", self.ultimo_integrado))
        response.extend(self.tiempo_inicial.to_bytes())
        response.extend(self.tiempo_final.to_bytes())
        return response

    @property
    def length(self):
        return 0x15


class C_CI_NT_2(C_CI_NX_2):
    """
    Class to read absolute measures
    """
    type = 122


class C_CI_NU_2(C_CI_NX_2):
    """
    Class to read incremental measures
    """
    type = 123


class C_TA_VC_2(BaseAppAsdu):
    """
    Leer Información de Tarificación (Valores en Curso)
    """
    type = 133
    causa_tm = 6

    # Register address: 134 or 135 or 136

    def from_hex(self, data, cualificador_ev):
        pass

    def to_bytes(self):
        return bytes()


class C_TA_VM_2(BaseAppAsdu):
    """
    Leer Información de Tarificación (Valores Memorizados)
    """
    type = 134
    data_length = 0x06
    causa_tm = 6

    # Register address: 134 or 135 or 136
    def __init__(self, start_date=datetime.datetime.now(),
                 end_date=datetime.datetime.now()):
        self.start_date = TimeA(start_date)
        self.end_date = TimeA(end_date)

    def from_hex(self, data, cualificador_ev):
        self.start_date.from_hex(data[0:5])
        self.end_date.from_hex(data[5:10])

    def to_bytes(self):
        response = bytearray()
        response.extend(self.start_date.to_bytes())
        response.extend(self.end_date.to_bytes())
        return response

    @property
    def length(self):
        return 0x13


class M_TA_VX_2(BaseAppAsdu):
    """
    Class for the M_TA_VC_2(135) and M_TA_VM_2(136) ASDUs
    """
    data_length = 0x06
    causa_tm = 5

    def __init__(self):
        self.valores = []

    def from_hex(self, data, cualificador_ev):
        address = struct.unpack("B", data[0:1])[0]
        # Active energy
        active_abs = struct.unpack("I", data[1:5])[0]
        active_inc = struct.unpack("I", data[5:9])[0]
        active_qual = struct.unpack("B", data[9:10])[0]
        # Inductive reactive energy
        reactive_abs_ind = struct.unpack("I", data[10:14])[0]
        reactive_inc_ind = struct.unpack("I", data[14:18])[0]
        reactive_qua_ind = struct.unpack("B", data[18:19])[0]
        # Absolute reactive energy
        reactive_abs_cap = struct.unpack("I", data[19:23])[0]
        reactive_inc_cap = struct.unpack("I", data[23:27])[0]
        reactive_qual_cap = struct.unpack("B", data[27:28])[0]
        # Reserved 7
        reserved_7 = struct.unpack("I", data[28:32])[0]
        reserved_7_qual = struct.unpack("B", data[32:33])[0]
        # Reserved 8
        reserved_8 = struct.unpack("I", data[33:37])[0]
        reserved_8_qual = struct.unpack("B", data[37:38])[0]
        # Maximum power
        max_power = struct.unpack("I", data[38:42])[0]
        max_power_date = TimeA()
        max_power_date.from_hex(data[42:47])
        max_power_qual = struct.unpack("B", data[47:48])[0]
        # Excessive power
        excess_power = struct.unpack("I", data[48:52])[0]
        ecxess_power_qual = struct.unpack("B", data[52:53])[0]
        # Period start date
        date_start = TimeA()
        date_start.from_hex(data[53:58])
        # Period end date
        date_end = TimeA()
        date_end.from_hex(data[58:63])

        br = BillingRegister(address, active_abs, active_inc, active_qual,
        reactive_abs_ind, reactive_inc_ind, reactive_qua_ind, reactive_abs_cap,
        reactive_inc_cap, reactive_qual_cap, reserved_7, reserved_7_qual,
        reserved_8, reserved_8_qual, max_power, max_power_date.datetime,
        max_power_qual, excess_power, ecxess_power_qual, date_start.datetime,
        date_end.datetime)

        self.valores.append(br)


class M_TA_VC_2(M_TA_VX_2):
    """
    Información de Tarificación (Valores en Curso)
    """
    type = 135


class M_TA_VM_2(M_TA_VX_2):
    """
    Información de Tarificación (Valores Memorizados)
    """
    type = 136


class M_IT_TX_2(BaseAppAsdu):
    """
    Class for the M_IT_TG_2(8) and M_IT_TK_2(11) ASDUs
    """

    def __init__(self):
        self.valores = []
        self.tiempo = None

    def from_hex(self, data, cualificador_ev):
        time_pos = cualificador_ev * 6
        self.tiempo = TimeA()
        self.tiempo.from_hex(data[time_pos:time_pos + 5])
        for i in range(0, cualificador_ev):
            position = i * 6  # 1 byte de typo 4 de medida 1 de cualificador
            # total integrado (4 octetos de energía+1 octeto con cualificadores
            # y número de secuencia), para cada uno de los totales.
            address = struct.unpack("B", data[position:position + 1])[0]
            total = struct.unpack("I",
                                  data[position + 1:position + 5])[0]
            quality = struct.unpack("B", data[position + 5:position + 6])[0]
            self.valores.append(IntegratedTotals(address, total, quality,
                                                 self.tiempo.datetime))


class M_IT_TK_2(M_IT_TX_2):
    """
    Totales integrados operacionales repuestos periódicamente, 4 octetos
    (incrementos de energía, en kWh o kVARh)
    """

    type = 11


class M_IT_TG_2(M_IT_TX_2):
    """
    Totales integrados operacionales, 4 octetos (lecturas de contadores
    absolutos, en kWh o kVARh)
    """

    type = 8


class C_CB_UN_2(BaseAppAsdu):
    """
    Leer los bloques de totales integrados operacionales por intervalo de
    tiempo para una dirección de objeto indicada
    """
    type = 190
    data_length = 0x06
    causa_tm = 6

    def __init__(self, start_date=datetime.datetime.now(),
                 end_date=datetime.datetime.now(), adr_object=10):
        self.start_date = TimeA(start_date)
        self.end_date = TimeA(end_date)
        self.object = adr_object

    def from_hex(self, data, cualificador_ev):
        self.object = struct.unpack("B", data[0:1])[0]
        self.start_date.from_hex(data[1:6])
        self.end_date.from_hex(data[6:11])

    def to_bytes(self):
        response = bytearray()
        response.extend(struct.pack("B", self.object))
        response.extend(self.start_date.to_bytes())
        response.extend(self.end_date.to_bytes())
        return response

    @property
    def length(self):
        return 0x14


class M_IB_TK_2(BaseAppAsdu):
    """
    Bloques de totales integrados operacionales por intervalo de tiempo para una
    dirección de objeto indicada
    """
    type = 140

    def __init__(self):
        self.valores = []
        self.tiempo = None

    def from_hex(self, data, cualificador_ev):
        adr_aux = {
            9: 8,
            10: 6,
            11: 3
        }

        position = 0
        for i in range(0, cualificador_ev):
            address = struct.unpack("B", data[position:position + 1])[0]
            amount = adr_aux[address]
            position += 1
            time_pos = position + (amount * 5)
            self.tiempo = TimeA()
            self.tiempo.from_hex(data[time_pos:time_pos + 5])

            for t in range(1, amount+1):
                total = struct.unpack("I", data[position:position+4])[0]
                quality = struct.unpack("B", data[position+4:position+5])[0]
                self.valores.append(IntegratedTotals(t, total, quality,
                                                     self.tiempo.datetime))
                position += 5
                if t == amount:
                    position += 5


class C_PC_NA_2(BaseAppAsdu):
    """
    Petición Leer potencias contratadas
    """
    type = 144
    causa_tm = 5

    # Register address: 134 or 135 or 136

    def from_hex(self, data, cualificador_ev):
        pass

    def to_bytes(self):
        return bytes()


class M_PC_NA_2(BaseAppAsdu):
    """
    Respuesta potencias contratadas
    """
    type = 145

    def __init__(self):
        self.valores = []
        self.tiempo = None

    def from_hex(self, data, cualificador_ev):
        position = 0
        for i in range(0, cualificador_ev):
            address = struct.unpack("B", data[position:position + 1])[0]
            position += 1
            power = struct.unpack("I", data[position:position + 4])[0]
            position += 4
            self.valores.append(ContractedPower(address, power))
        self.tiempo = TimeA()
        self.tiempo.from_hex(data[position:position + 5])


class TimeBase():

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

        # time B
        self.seconds = fecha.second
        self.microseconds = fecha.microsecond

    @property
    def datetime(self):
        year = self.year + 2000
        return datetime.datetime(
            year, self.month, self.dayofmonth, self.hour, self.minute,
            self.seconds, self.microseconds)

    def __repr__(self):
        # output = "  -- TiempoA Begin -- \n"
        # output += "    minute: " + str(self.minute) + "\n"
        # output += "    TIS: " + str(self.TIS) + "\n"
        # output += "    IV: " + str(self.IV) + "\n"
        # output += "    hour: " + str(self.hour) + "\n"
        # output += "    RES1: " + str(self.RES1) + "\n"
        # output += "    SU: " + str(self.SU) + "\n"
        # output += "    dayofmonth: " + str(self.dayofmonth) + "\n"
        # output += "    dayofweek: " + str(self.dayofweek) + "\n"
        # output += "    month: " + str(self.month) + "\n"
        # output += "    ETI: " + str(self.ETI) + "\n"
        # output += "    PTI: " + str(self.PTI) + "\n"
        # output += "    year: " + str(self.year) + "\n"
        # output += ("    content: "
        #            + (":".join("%02x" % b for b in self.to_bytes())) + "\n")
        # output += "    datetime: " + str(self.datetime) + "\n"
        # output += "  -- TiempoA End \n"
        # return output
        return str(self.datetime)


class TimeA(TimeBase):

    def from_hex(self, data):
        reversed_bytes = bitstring.BitArray(bytearray(reversed(data)))
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

        self.seconds = 0
        self.microseconds = 0

    def to_bytes(self):
        response = bitstring.BitArray()
        thedata = bitstring.BitArray(bytearray([self.minute]))
        response = response + thedata[-1:-7:-1]
        thedata = bitstring.BitArray(bytearray([self.TIS]))
        response = response + thedata[-1:]
        thedata = bitstring.BitArray(bytearray([self.IV]))
        response = response + thedata[-1:]
        thedata = bitstring.BitArray(bytearray([self.hour]))
        response = response + thedata[-1:-6:-1]
        thedata = bitstring.BitArray(bytearray([self.RES1]))
        response = response + thedata[-1:-3:-1]
        thedata = bitstring.BitArray(bytearray([self.SU]))
        response = response + thedata[-1:]
        thedata = bitstring.BitArray(bytearray([self.dayofmonth]))
        response = response + thedata[-1:-6:-1]
        thedata = bitstring.BitArray(bytearray([self.dayofweek]))
        response = response + thedata[-1:-4:-1]
        thedata = bitstring.BitArray(bytearray([self.month]))
        response = response + thedata[-1:-5:-1]
        thedata = bitstring.BitArray(bytearray([self.ETI]))
        response = response + thedata[-1:-3:-1]
        thedata = bitstring.BitArray(bytearray([self.PTI]))
        response = response + thedata[-1:-3:-1]
        thedata = bitstring.BitArray(bytearray([self.year]))
        response = response + thedata[-1:-8:-1]
        thedata = bitstring.BitArray(bytearray([self.RES2]))
        response = response + thedata[-1:]
        response = response[::-1]
        inbytes = response.tobytes()[::-1]
        return inbytes


class TimeB(TimeBase):

    def from_hex(self, data):
        reversed_bytes = bitstring.BitArray(bytearray(reversed(data)))
        reversed_bits = bitstring.BitStream(reversed(reversed_bytes))

        milliseconds = bitstring.BitArray(reversed(reversed_bits.read(10))).uint
        self.microseconds = milliseconds * 1000
        self.seconds = bitstring.BitArray(reversed(reversed_bits.read(6))).uint
        self.minute = bitstring.BitArray(reversed(reversed_bits.read(6))).uint
        self.TIS = reversed_bits.read(1).uint
        self.IV = reversed_bits.read(1).uint
        self.hour = bitstring.BitArray(reversed(reversed_bits.read(5))).uint
        self.RES1 = bitstring.BitArray(reversed(reversed_bits.read(2))).uint
        self.SU = reversed_bits.read(1).uint
        self.dayofmonth = bitstring.BitArray(reversed(reversed_bits.read(5))).uint
        self.dayofweek = bitstring.BitArray(reversed(reversed_bits.read(3))).uint
        self.month = bitstring.BitArray(reversed(reversed_bits.read(4))).uint
        self.ETI = bitstring.BitArray(reversed(reversed_bits.read(2))).uint
        self.PTI = bitstring.BitArray(reversed(reversed_bits.read(2))).uint
        self.year = bitstring.BitArray(reversed(reversed_bits.read(7))).uint
        self.RES2 = reversed_bits.read(1).uint

    def to_bytes(self):
        response = bitstring.BitArray()

        milliseconds = int(self.microseconds / 1000)
        thedata = bitstring.BitArray(bytearray(
            [milliseconds >> 8, milliseconds & 0xFF]
        ))
        response = response + thedata[-1:-11:-1]
        thedata = bitstring.BitArray(bytearray([self.seconds]))
        response = response + thedata[-1:-7:-1]
        thedata = bitstring.BitArray(bytearray([self.minute]))
        response = response + thedata[-1:-7:-1]
        thedata = bitstring.BitArray(bytearray([self.TIS]))
        response = response + thedata[-1:]
        thedata = bitstring.BitArray(bytearray([self.IV]))
        response = response + thedata[-1:]
        thedata = bitstring.BitArray(bytearray([self.hour]))
        response = response + thedata[-1:-6:-1]
        thedata = bitstring.BitArray(bytearray([self.RES1]))
        response = response + thedata[-1:-3:-1]
        thedata = bitstring.BitArray(bytearray([self.SU]))
        response = response + thedata[-1:]
        thedata = bitstring.BitArray(bytearray([self.dayofmonth]))
        response = response + thedata[-1:-6:-1]
        thedata = bitstring.BitArray(bytearray([self.dayofweek]))
        response = response + thedata[-1:-4:-1]
        thedata = bitstring.BitArray(bytearray([self.month]))
        response = response + thedata[-1:-5:-1]
        thedata = bitstring.BitArray(bytearray([self.ETI]))
        response = response + thedata[-1:-3:-1]
        thedata = bitstring.BitArray(bytearray([self.PTI]))
        response = response + thedata[-1:-3:-1]
        thedata = bitstring.BitArray(bytearray([self.year]))
        response = response + thedata[-1:-8:-1]
        thedata = bitstring.BitArray(bytearray([self.RES2]))
        response = response + thedata[-1:]
        response = response[::-1]
        inbytes = response.tobytes()[::-1]
        return inbytes
