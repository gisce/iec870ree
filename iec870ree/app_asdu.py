# -*- coding: utf-8 -*-
import bitstring
import struct
import datetime
from pytz import timezone
from collections import namedtuple

from six import with_metaclass

TIMEZONE = timezone('Europe/Madrid')

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
    'C_RM_NA_2',
    'M_RM_NA_2',
    # AMPLIACION DE PROTOCOLO
    'P_IN_VA_2',
    'R_IN_VA_2',
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

SerialPortConf = namedtuple('SerialPortConf', ['speed', 'params', 'start_mode', 'start_string'])

InstantTotals = namedtuple('InstantTotals', [
    'ai', 'ai_val', 'ae', 'ae_val',
    'r1', 'r1_val', 'r2', 'r2_val', 'r3', 'r3_val', 'r4','r4_val',
    'measure_date'])

InstantPower = namedtuple('InstantPower', [
        'fase', 'potencia_activa', 'potencia_reactiva', 'factor_potencia',
        'is_exporting_activa', 'is_exporting_reactiva', 'valid'
    ]
)

InstantPhaseVI = namedtuple('InstantPhaseVI', ['phase', 'I', 'V', 'valid'])

SERIAL_PORT_SPEED = {
    0: 'Not available',
    1: '300',
    2: '600',
    3: '1.200',
    4: '2.400',
    5: '4.800',
    6: '9.600',
    7: '14.400',
    8: '19.200',
    9: '28.800',
    10: '38.400',
    11: '57.600',
    12: '115.200',
    255: 'Other',
}

SERIAL_PORT_PARAM = {
    0: 'Not available',
    1: '7N1',
    2: '7E1',
    3: '7O1',
    4: '7N2',
    5: '7E2',
    6: '7O2',
    7: '8N1',
    8: '8E1',
    9: '8O1',
    10: '8N2',
    11: '8E2',
    12: '8O2',
}


# PROTOCOL EXTENSIONS

# 163 response
INSTANT_VALUES_OBJECTS = {
    192: {
        'name': 'totalizadores',
        'object': 'TotalizadoresInstantaneos'
    },
    193: {
        'name': 'potencias',
        'object': 'PotenciaInstantanea'
    },
    194: {
        'name': 'I_V',
        'object': 'IVInstantaneos'
    }
}


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


class C_RM_NA_2(BaseAppAsdu):
    """
    Petición configuración equipo
    """
    type = 141
    causa_tm = 5

    def from_hex(self, data, cualificador_ev):
        pass

    def to_bytes(self):
        return bytes()


class M_RM_NA_2(BaseAppAsdu):
     """
     Respuesta configuración equipo
     """
     type = 142

     def __init__(self):
         self.codigo_fabricante = None
         self.codigo_equipo = None
         self.modelo_fabricante = ''
         self.firmware = None
         self.iec_date = None
         self.battery = None
         self.iec_version_date = None
         self.serial_port_1 = None
         self.serial_port_2 = None
         self.optical_port = None
         self.primari_V = None
         self.secondary_V = None
         self.primari_I = None
         self.secondary_I = None
         self.integration_period_1 = None
         self.integration_period_2 = None
         self.integration_period_3 = None
         self.active_contracts = []

     def from_hex(self, data, cualificador_ev):
         self.codigo_fabricante = struct.unpack("B", data[0:1])[0]
         self.modelo_fabricante = (
             chr(struct.unpack("B", data[1:2])[0] or '') +
             chr(struct.unpack("B", data[2:3])[0] or '')
         )
         self.firmware = struct.unpack("B", data[3:4])[0]
         self.codigo_equipo = struct.unpack("I", data[4:8])[0]
         # 0-4 bits: month 5-8: year
         iec_date_field = struct.unpack("B", data[8:9])[0]
         self.iec_date = '{}/{}'.format(iec_date_field & 15, ((iec_date_field & 240) >> 4) + 2000)
         self.iec_version_date = TimeA()
         self.iec_version_date.from_hex(data[9:14])
         self.battery = struct.unpack("B", data[14:15])[0]
         position = 15
         for serialport in ['1' ,'2']:
             speed = SERIAL_PORT_SPEED[
                 struct.unpack("B", data[position:position+1])[0]
             ]
             position+=1
             params = SERIAL_PORT_PARAM[
                 struct.unpack("B", data[position:position+1])[0]
             ]
             position += 1
             mode = struct.unpack("B", data[position:position + 1])[0]
             position += 1
             start_string = ''
             eof = False
             for i in range(0, 20):
                 val = struct.unpack("B", data[position:position + 1])[0]
                 position += 1
                 if val != 0 and not eof:
                     start_string += chr(val)
                     eof = True
             portconf = SerialPortConf(
                 speed, params, mode, start_string
             )
             setattr(self, "serial_port_{}".format(serialport), portconf)
         self.optical_port = SerialPortConf(
             SERIAL_PORT_SPEED[struct.unpack("B", data[40:41])[0]],
             SERIAL_PORT_PARAM[struct.unpack("B", data[41:42])[0]],
             0,
             ''
         )
         self.primari_V = struct.unpack("I", data[42:46])[0] / 10.0
         self.secondary_V = struct.unpack("I", data[46:50])[0] / 10.0
         self.primari_I = struct.unpack("I", data[50:54])[0] / 10.0
         self.secondary_I = struct.unpack("I", data[54:58])[0] /10.0
         self.integration_period_1 = struct.unpack("B", data[58:59])[0]
         self.integration_period_2 = struct.unpack("B", data[59:60])[0]
         self.integration_period_3 = struct.unpack("B", data[60:61])[0]
         active_contracts_byte = struct.unpack("B", data[61:62])[0]
         contracts = []
         for i in [0, 2, 4]:
             if active_contracts_byte & (2 << i):
                 contracts.append(int(i/2 + 1))
         self.active_contracts = contracts


# Protocol extension
# Instant Values
class P_IN_VA_2(BaseAppAsdu):
    """
    Petición valores instantáneos
    direccion registro: 0
    direcciones objeto (lista):
        192: Totalizadores Energía
        193: Potencias Activas
        194: Tensiones e Intensidades
    """
    type = 162
    causa_tm = 5

    def __init__(self, objetos=[192]):
        self.objetos = objetos
        self.data_length = len(self.objetos) * 0x06

    def from_hex(self, data, cualificador_ev):
        pass

    def to_bytes(self):
        response = bytearray()
        for objeto in self.objetos:
            response.extend(struct.pack("B", objeto))
        return response

    @property
    def length(self):
        return 0x09 + len(self.objetos)

class R_IN_VA_2(BaseAppAsdu):
    """
    Respuesta valores instantáneos
    direccion registro: 0
    direcciones objeto (lista):
        192: Totalizadores Energía
        193: Potencias Activas
        194: Tensiones e Intensidades
    """
    type = 163
    causa_tm = 5

    def __init__(self):
        self.valores = []

    def from_hex(self, data, cualificador_ev):
        pos = 0
        for obj_idx in range(cualificador_ev):
            object_id = struct.unpack("B", data[pos:pos+1])[0]
            pos +=1
            object_class = globals()[INSTANT_VALUES_OBJECTS[object_id]['object']]
            the_object = object_class()
            the_object.from_hex(data[pos:pos + the_object.length])
            self.valores.append(the_object)
            pos += the_object.length

    def to_bytes(self):
        pass


class TimeBase():

    def __init__(self, fecha=datetime.datetime.now()):
        locfecha = fecha
        if not fecha.tzinfo:
            locfecha = TIMEZONE.localize(fecha)
        self.minute = locfecha.minute  # UI6
        self.TIS = 0  # BS1 TIS=tariff information switch
        self.IV = 0  # BS1 IV=invalid
        self.hour = locfecha.hour  # UI5
        self.RES1 = 0  # BS2 RES1=reserve 1
        # BS1 SUMMER TIME
        # (0 STANDARD TIME, 1 summer time or daylight saving time)
        dst = 0
        if locfecha.tzinfo:
            dst = int(locfecha.dst().seconds > 0)
        self.SU = dst
        self.dayofmonth = locfecha.day  # UI5
        self.dayofweek = locfecha.weekday() + 1  # UI3
        self.month = locfecha.month  # UI4
        self.ETI = 0  # UI2 ETI=energy tariff information
        self.PTI = 0  # UI2 PTI=power tariff information
        self.year = locfecha.year % 100  # UI7
        self.RES2 = 0  # BS1

        # time B
        self.seconds = locfecha.second
        self.microseconds = locfecha.microsecond

    @property
    def datetime(self):
        year = self.year + 2000
        dst = self.SU > 0
        dt = datetime.datetime(
            year, self.month, self.dayofmonth, self.hour, self.minute,
            self.seconds, self.microseconds
        )
        return TIMEZONE.localize(dt, is_dst=dst)

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
        dst_txt = {'1': 'S', '0': 'W'}[str(self.SU)]
        return '{} ({})'.format(str(self.datetime), dst_txt)


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
                                   .uint or 1
        self.dayofweek = bitstring.BitArray(reversed(reversed_bits.read(3)))\
                                  .uint
        self.month = bitstring.BitArray(
            reversed(reversed_bits.read(4))
        ).uint or 1
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
        self.dayofmonth = bitstring.BitArray(
            reversed(reversed_bits.read(5))
        ).uint or 1
        self.dayofweek = bitstring.BitArray(reversed(reversed_bits.read(3))).uint
        self.month = bitstring.BitArray(
            reversed(reversed_bits.read(4))
        ).uint or 1
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


class TotalizadoresInstantaneos():

    tipo = 163
    objeto = 192
    length = 29

    def __init__(self):
        self.valores = None

    def from_hex(self, data):
        ai = struct.unpack("I", data[0:4])[0]
        ae = struct.unpack("I", data[4:8])[0]
        r1 = struct.unpack("I", data[8:12])[0]
        r2 = struct.unpack("I", data[12:16])[0]
        r3 = struct.unpack("I", data[16:20])[0]
        r4 = struct.unpack("I", data[20:24])[0]
        dt = TimeA()
        dt.from_hex(data[24:29])

        it = InstantTotals(
            ai & 0x07ffffff, ai & 0x8000000 and False or True,  # kWh , 0 valid/1 invalid
            ae & 0x07ffffff, ai & 0x8000000 and False or True,  # kWh , 0 valid/1 invalid
            r1 & 0x07ffffff, ai & 0x8000000 and False or True,  # kVArh , 0 valid/1 invalid
            r2 & 0x07ffffff, ai & 0x8000000 and False or True,  # kVArh , 0 valid/1 invalid
            r3 & 0x07ffffff, ai & 0x8000000 and False or True,  # kVArh , 0 valid/1 invalid
            r4 & 0x07ffffff, ai & 0x8000000 and False or True,  # kVArh , 0 valid/1 invalid
            dt)                                                 # Loalized datetime

        self.valores = it

        return self.valores

    def __repr__(self):
        output = "\n-- TotalizadoresInstantaneos BEGIN--\n"
        output += repr(self.valores) + "\n"
        output += "-- TotalizadoresInstantaneos END--\n"
        return output


class PotenciaInstantanea():

    tipo = 163
    objeto = 193
    length = 37

    def __init__(self):
        self.valores = []

    def from_hex(self, data):
        reversed_bytes = bitstring.BitArray(bytearray(reversed(data)))
        reversed_bits = bitstring.BitStream(reversed(reversed_bytes))

        for name in ['Total', 'Phase I', 'Phase II', 'Phase III']:
            potencia_activa = bitstring.BitArray(reversed(reversed_bits.read(24))).uint       # kW
            potencia_reactiva = bitstring.BitArray(reversed(reversed_bits.read(24))).uint     # kVAr
            factor_potencia = bitstring.BitArray(reversed(reversed_bits.read(10))).uint       # cos phi in millis
            is_exporting_activa = bitstring.BitArray(reversed(reversed_bits.read(1))).bool    # 0 importada/ 1 exportada
            is_exporting_reactiva = bitstring.BitArray(reversed(reversed_bits.read(1))).bool  # 0 Q1/Q4 / 1 Q2/Q3
            bitstring.BitArray(reversed(reversed_bits.read(3)))                               # not used
            invalid = bitstring.BitArray(reversed(reversed_bits.read(1))).bool                # 0 valid/ 1 invalid
            ip = InstantPower(
                name, potencia_activa, potencia_reactiva, factor_potencia / 1000.0,
                is_exporting_activa, is_exporting_reactiva, not invalid
            )

            self.valores.append(ip)

        dt = TimeA()
        dt.from_hex(data[32:37])
        self.valores.append(dt)  # Localized datetime
        return self.valores

    def __repr__(self):
        output = "\n-- PotenciaInstantanea BEGIN --\n"
        for value in self.valores:
            output += '{}\n'.format(value)
        output += "-- PotenciaInstantanea BEGIN --\n"
        return output


class IVInstantaneos():

    tipo = 163
    objeto = 194
    length = 26

    def __init__(self):
        self.valores = []

    def from_hex(self, data):
        reversed_bytes = bitstring.BitArray(bytearray(reversed(data)))
        reversed_bits = bitstring.BitStream(reversed(reversed_bytes))

        for phase in ['I', 'II', 'III']:
            intensidad_dA = bitstring.BitArray(reversed(reversed_bits.read(24))).uint  # in dA
            tension_dV = bitstring.BitArray(reversed(reversed_bits.read(30))).uint     # in dV
            bitstring.BitArray(reversed(reversed_bits.read(1)))                        # not used
            invalid = bitstring.BitArray(reversed(reversed_bits.read(1))).bool         # valid 0/invalid 1

            ipiv = InstantPhaseVI(phase, intensidad_dA / 10.0, tension_dV / 10.0, not invalid)
            self.valores.append(ipiv)

        dt = TimeA()
        dt.from_hex(data[21:26])
        self.valores.append(dt)

        return self.valores

    def __repr__(self):
        output = "\n-- IVInstantaneos BEGIN--\n"
        for value in self.valores:
            output += '{}\n'.format(value)
        output += "-- IVInstantaneos END--\n"
        return output