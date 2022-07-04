from abc import ABC, abstractmethod


class AbstractOptions(ABC):
    '''
    This class is an abstraction for customized bot option frames. Option frames are used to customize the bot's behavior.
    '''
    options = {}
    controller = None

    @abstractmethod
    def set_controller(self, controller):
        self.controller = controller

    @abstractmethod
    def get_options(self):
        pass
