import struct


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
