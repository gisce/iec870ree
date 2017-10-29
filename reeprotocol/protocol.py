import logging
from abc import ABCMeta, abstractmethod
from .base_asdu import (
    AsduParser, FixedAsdu, VariableAsdu
)


class ProtocolException(Exception):
    pass


class AppLayer(metaclass=ABCMeta):

    def initialize(self, link_layer):
        self.link_layer

    def send_user_data(self, asdu):
        pass

    def get_user_data(self):
        pass


class LinkLayer(metaclass=ABCMeta):

    def __init__(self, der=None, dir_pm=None):
        self.der = der
        self.dir_pm = dir_pm

    def initialize(self, physical_layer):
        self.physical_layer = physical_layer
        self.asdu_parser = AsduParser()
        self._fcb = 0

    def send_frame(self, frame):
        for bt in frame.buffer:
            self.physical_layer.send_byte(bt)

    def get_frame(self):
        frame = None
        while not frame:
            bt = self.physical_layer.get_byte(self)
            frame = self.asdu_parser.append_and_get_if_completed(bt)
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
        asdu.c.cf = 0 # link state reposition
        asdu.der = self.der
        asdu.generate()
        return asdu
        
    @property
    def fcb(self):
        self._fcb += 1 % 2
        return self._fcb


class PhysicalLayer(metaclass=ABCMeta):

    @abstractmethod
    def send_byte(self, byte):
        pass

    @abstractmethod
    def get_byte(self):
        pass
