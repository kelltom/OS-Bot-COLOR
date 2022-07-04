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
    IDLE = 4


class Bot(ABC):
    status = BotStatus.STOPPED
    iterations: int = 0
    current_iter: int = 0
    breaks: bool = False
    thread: Thread = None

    @abstractmethod
    def __init__(self, title, description):
        self.title = title
        self.description = description

    @abstractmethod
    def main_loop(self):
        pass

    @abstractmethod
    def save_settings(self, settings: dict):
        pass

    def play_pause(self):  # sourcery skip: extract-method
        # if the bot is stopped, start it
        if self.status == BotStatus.STOPPED:
            print("play() from bot.py - starting bot")
            self.set_status(BotStatus.RUNNING)
            self.clear_log()
            self.thread = Thread(target=self.main_loop)
            self.thread.setDaemon(True)
            self.thread.start()
        # otherwise, if bot is already running, pause it and return status
        elif self.status == BotStatus.RUNNING:
            print("play() from bot.py - pausing bot")
            self.set_status(BotStatus.PAUSED)
        # otherwise, if bot is paused, resume it and return status
        elif self.status == BotStatus.PAUSED:
            print("play() from bot.py - resuming bot")
            self.set_status(BotStatus.RUNNING)

    def stop(self):
        '''
        If the bot's status is not stopped, set it to stopped, reset the current iteration to 0, and stop the thread.
        '''
        if self.status != BotStatus.STOPPED:
            print("stop() from bot.py - stopping bot")
            self.set_status(BotStatus.STOPPED)
            self.reset_iter()
            # self.thread.join()  # Causing a deadlock when calling for log updates
            print("stop() from bot.py - bot stopped")

    def restart(self):
        '''
        Runs the stop() function and then the play() function.
        '''
        print("restart() from bot.py - bot restarted")
        self.stop()
        self.play_pause()

    # ---- Functions that notify the controller of changes ----
    def reset_iter(self):
        self.current_iter = 0
        self.controller.update_progress()

    def increment_iter(self):
        self.current_iter += 1
        self.controller.update_progress()

    def set_status(self, status: BotStatus):
        self.status = status
        self.controller.update_status()

    def log_msg(self, msg: str):
        self.controller.update_log(msg)

    def clear_log(self):
        self.controller.clear_log()

    def set_controller(self, controller):
        self.controller = controller
