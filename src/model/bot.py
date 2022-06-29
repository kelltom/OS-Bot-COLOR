'''
A Bot is a model for a script that can be run. The script has a status (running, paused, stopped). It can be paused, resumed, and stopped.
The script can also be configured to run for a certain number of iterations. The script can also be configured to take random breaks.
The script should be able to be configured to use a specific key to start, pause and abort. The script will return text information about its progress.
'''
from enum import Enum


class BotStatus(Enum):
    """
    BotStatus enum.
    """
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3


class Bot():
    def __init__(self, name, status: BotStatus = BotStatus.STOPPED, iterations: int = 0, breaks: bool = True):
        self.name = name
        self.status = status
        self.iterations = iterations
        self.breaks = breaks

    @property
    def name(self):
        return self.name

    @property
    def status(self) -> BotStatus:
        return self.status

    @status.setter
    def status(self, status: BotStatus):
        self.status = status

    @property
    def iterations(self) -> int:
        return self.iterations

    @iterations.setter
    def iterations(self, iterations: int):
        self.iterations = iterations

    @property
    def breaks(self) -> bool:
        return self.breaks

    @breaks.setter
    def breaks(self, breaks: bool):
        self.breaks = breaks

    def __str__(self):
        return f"{self.name} - {self.status} - {self.iterations} - {self.breaks}"
