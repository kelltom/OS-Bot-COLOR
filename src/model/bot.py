'''
A Bot is a model for a script that can be run. The script has a status (running, paused, stopped). It can be paused, resumed, and stopped.
The script can also be configured to run for a certain number of iterations. The script can also be configured to take random breaks.
The script should be able to be configured to use a specific key to start, pause and abort. The script will return text information about its progress.
'''
from abc import ABC, abstractmethod
from enum import Enum


class BotStatus(Enum):
    """
    BotStatus enum.
    """
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3


class Bot(ABC):
    def __init__(self, name, status: BotStatus = BotStatus.STOPPED, iterations: int = 0, breaks: bool = False):
        self.name = name
        self.status = status
        self.iterations = iterations
        self.breaks = breaks

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def main_loop(self):
        pass

    def __str__(self):
        return f"{self.name} - {self.status} - {self.iterations} - {self.breaks}"
