'''
A Bot is a model for a script that can be run. The script has a status (running, paused, stopped). It can be paused, resumed, and stopped.
The script can also be configured to run for a certain number of iterations. The script can also be configured to take random breaks.
The script should be able to be configured to use a specific key to start, pause and abort. The script will return text information about its progress.
'''
from abc import ABC, abstractmethod
from enum import Enum
from threading import Thread


class BotStatus(Enum):
    """
    BotStatus enum.
    """
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3


class Bot(ABC):
    @abstractmethod
    def __init__(self, status: BotStatus = BotStatus.STOPPED, iterations: int = 0, current_iter: int = 0, breaks: bool = False, thread: Thread = None):
        self.status = status
        self.iterations = iterations
        self.current_iter = current_iter
        self.breaks = breaks
        self.thread = thread

    @abstractmethod
    def play_pause(self):
        pass

    @abstractmethod
    def restart(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def main_loop(self):
        pass
