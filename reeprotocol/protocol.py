import logging
from abc import ABCMeta, abstractmethod
from .base_asdu import AsduParser


class AppLayer(metaclass=ABCMeta):

    def initialize(self, link_layer):
        self.link_layer

    def send_user_data(self, asdu):
        pass

    def get_user_data(self):
        pass


class LinkLayer(metaclass=ABCMeta):

    def initialize(self, physical_layer):
        self.physical_layer = physical_layer
        self.asdu_parser = AsduParser()

    def send_frame(self, frame):
        for bt in frame.buffer:
            self.physical_layer.send_byte(bt)

    def get_frame(self):
        frame = None
        while not frame:
            bt = self.physical_layer.get_byte(self)
            frame = self.asdu_parser.append_and_get_if_completed(bt)
        return frame


class PhysicalLayer(metaclass=ABCMeta):

    @abstractmethod
    def send_byte(self, byte):
        pass

    @abstractmethod
    def get_byte(self):
        pass
