import logging
from abc import ABCMeta, abstractmethod
from .base_asdu import (
    AsduParser, FixedAsdu, VariableAsdu
)
import traceback
from .app_asdu import *
import math

logger = logging.getLogger('reeprotocol')


def parse_asdu(trama):
    p = AsduParser()
    for x in range(0, len(trama), 2):
        a = p.append_and_get_if_completed(int(trama[x:x+2], 16))
    if not a:
        raise Exception('Trama no completa!')
    else:
        return a


class ProtocolException(Exception):
    pass

class IntegrationPeriodNotAvailable(Exception):
    pass

class RequestedASDUTypeNotAvailable(Exception):
    pass

class AppLayer(metaclass=ABCMeta):

    def initialize(self, link_layer):
        self.link_layer = link_layer

    def send_user_data(self, asdu):
        pass

    def get_user_data(self):
        pass

    def process_request(self, request_asdu):
        self.link_layer.send_frame(request_asdu)
        asdu_ack = self.link_layer.get_frame()
        if not asdu_ack:
            raise ProtocolException("Didn't get ACK")
        return self.process_requestresponse()

    def process_requestresponse(self):
        """ this function makes a very ugly assumption,
        if you don't iterate over all elements, the program will fail"""
        # TODO CHECK CORRECT ACK
        while True:
            asdu = FixedAsdu()
            asdu.c.res = 0
            asdu.c.prm = 1
            asdu.c.fcb = self.link_layer.fcb
            asdu.c.fcv = 1
            asdu.c.cf = 11
            asdu.der = self.link_layer.der
            asdu.generate()
            self.link_layer.send_frame(asdu)
            asdu_resp = self.link_layer.get_frame()
            if not asdu_resp:
                logger.error("Did not receive ASDU response.")
                raise ProtocolException("Didn't get ASDU")
            yield asdu_resp

            if asdu_resp.causa_tm == 0x05 and asdu_resp.tipo in [135, 136, 11, 8, 140]:
                logger.info("Received request for next batch of information")
            elif asdu_resp.causa_tm == 0x05:
                logger.info("Request or asked")
                break
            elif asdu_resp.causa_tm == 0x07:
                logger.info("Activation confirmation")
                break
            elif asdu_resp.causa_tm == 0x0A:
                logger.info("Activation terminated")
                break
            elif asdu_resp.causa_tm == 0x0E:
                logger.error("Requested ASDU-type not available")
                raise RequestedASDUTypeNotAvailable()
            elif asdu_resp.causa_tm == 0x12:
                logger.error("Requested integration period not available")
                raise IntegrationPeriodNotAvailable()
            elif asdu_resp.causa_tm == 0x11:
                logger.error("Requested information object not available")
                raise IntegrationPeriodNotAvailable()
            else:
                raise Exception('ERROR: Transmission cause unknown: {}'.format(asdu_resp.causa_tm))

    def authenticate(self, clave_pm):
        #183
        asdu = self.create_asdu_request(C_AC_NA_2(clave_pm))
        resps = list(self.process_request(asdu))
        return resps[0]

    def finish_session(self):
        #187
        asdu = self.create_asdu_request(C_FS_NA_2())
        try:
            resps = list(self.process_request(asdu))
        except Exception as e:
            logger.exception("error finishing session {}".format(e))

    def read_daily_billings(self, start_date, end_date, register=21):
        #122
        asdu = self.create_asdu_request(C_CI_NT_2(start_date, end_date),
                                        register)
        #do not remove this as we have to iterate over physical layer frames.
        try:
            resps = list(self.process_request(asdu))
            for resp in self.process_requestresponse():
                if resp.tipo == 8:
                    yield resp
        except IntegrationPeriodNotAvailable as e:
            pass

    def read_hourly_profiles(self, start_date, end_date, register=11):
        #123
        asdu = self.create_asdu_request(C_CI_NU_2(start_date, end_date),
                                        register)
        #do not remove this as we have to iterate over physical layer frames.
        try:
            resps = list(self.process_request(asdu))
            for resp in self.process_requestresponse():
                if resp.tipo == 11:
                    yield resp
        except IntegrationPeriodNotAvailable as e:
            pass
    
    def read_datetime(self):
        #103
        asdu = self.create_asdu_request(C_TI_NA_2())
        resps = list(self.process_request(asdu))
        for resp in self.process_requestresponse():
            if resp.tipo == 72:
                yield resp

    def get_info(self):
        #100
        asdu = self.create_asdu_request(C_RD_NA_2())
        resps = list(self.process_request(asdu))
        for resp in self.process_requestresponse():
            if resp.tipo == 71:
                yield resp

    def current_tariff_info(self, register=134):
        #133 current values
        asdu = self.create_asdu_request(C_TA_VC_2(), register)
        try:
            resps = list(self.process_request(asdu))
            for resp in self.process_requestresponse():
                if resp.tipo == 135:
                    yield resp
        except IntegrationPeriodNotAvailable as e:
            pass

    def stored_tariff_info(self, start_date, end_date, register=134):
        #134 stored values
        asdu = self.create_asdu_request(C_TA_VM_2(start_date, end_date), register)
        try:
            resps = list(self.process_request(asdu))
            for resp in self.process_requestresponse():
                if resp.tipo == 136:
                    yield resp
        except IntegrationPeriodNotAvailable as e:
            pass

    def get_blocks_hourly_profiles(self, start_date, end_date, register=11,
                                  adr_object=10):
        # 190
        asdu = self.create_asdu_request(C_CB_UN_2(start_date=start_date, end_date=end_date,
                                                  adr_object=adr_object), register)
        # do not remove this as we have to iterate over physical layer frames.
        try:
            resps = list(self.process_request(asdu))
            for resp in self.process_requestresponse():
                if resp.tipo == 140:
                    yield resp
        except IntegrationPeriodNotAvailable as e:
            pass

    def create_asdu_request(self, user_data, registro=0):
        asdu = VariableAsdu()
        asdu.c.res = 0
        asdu.c.prm = 1
        asdu.c.fcb = self.link_layer.fcb
        asdu.c.fcv = 1
        asdu.c.cf = 3
        asdu.der = self.link_layer.der
        asdu.cualificador_ev = math.ceil(getattr(user_data, 'data_length', 0x06)/0x06)
        asdu.causa_tm = getattr(user_data, 'causa_tm', 6)
        asdu.dir_pm = self.link_layer.dir_pm
        # registro> 11 curvas horarias, 12 cuartohorarias, 21 resumenes diarios
        asdu.dir_registro = registro
        asdu.content = user_data
        asdu.generate()
        return asdu


class LinkLayer(metaclass=ABCMeta):

    def __init__(self, der=None, dir_pm=None):
        self.der = der
        self.dir_pm = dir_pm
        self._fcb = 0
    
    def initialize(self, physical_layer):
        self.physical_layer = physical_layer
        self.asdu_parser = AsduParser()

    def send_frame(self, frame):
        logger.info("sending frame\n {}".format(frame))
        logging.info("->" + ":".join("%02x" % b for b in frame.buffer))
        self.physical_layer.send_bytes(frame.buffer)

    def get_frame(self, timeout=60):
        frame = None
        while not frame:
            bt = self.physical_layer.get_byte(timeout)
            frame = self.asdu_parser.append_and_get_if_completed(bt)
        logger.info("receiving frame {}".format(frame))
        return frame

    def link_state_request(self):
        asdu = self.create_link_state_asdu()
        self.send_frame(asdu)
        resp = self.get_frame()
        if resp is None:
            raise ProtocolException("Link state request didn't get response")

    def create_link_state_asdu(self):
        asdu = FixedAsdu()
        asdu.c.res = 0
        asdu.c.prm = 1
        asdu.c.fcb = 0
        asdu.c.fcv = 0
        asdu.c.cf = 9
        asdu.der = self.der
        asdu.generate()
        return asdu

    def remote_link_reposition(self):
        asdu = self.create_remote_link_reposition_asdu()
        self.send_frame(asdu)
        resp = self.get_frame()
        # CHECK IT IS AN ACK?
        if resp is None:
            raise ProtocolException("no answer received. maybe wrong der??")

    def create_remote_link_reposition_asdu(self):
        asdu = FixedAsdu()
        asdu.c.res = 0
        asdu.c.prm = 1
        asdu.c.fcb = 0
        asdu.c.fcv = 0
        asdu.c.cf = 0  # link state reposition
        asdu.der = self.der
        asdu.generate()
        return asdu

    @property
    def fcb(self):
        self._fcb += 1 % 2
        return self._fcb


class PhysicalLayer(metaclass=ABCMeta):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def send_byte(self, byte):
        pass

    def send_bytes(self, bts):
        for byte in bts:
            self.send_byte(byte)
    
    @abstractmethod
    def get_byte(self, timeout):
        pass
