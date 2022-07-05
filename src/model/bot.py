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
    options_set: bool = False
    bot_thread: Thread = None
    options_thread: Thread = None

    @abstractmethod
    def __init__(self, title, description):
        self.title = title
        self.description = description

    @abstractmethod
    def main_loop(self):
        '''
        Main logic of the bot. This function is called in a separate thread.
        The main loop should frequently check the status of the bot and terminate when the status is STOPPED.
        '''
        pass

    @abstractmethod
    def set_options_gui(self):
        '''
        Runs PyAutoGUI message boxes to set the options for the bot. This function is called on a separate thread.
        Collect all necessary information from the user and set the bot's options. This function should log messages
        to the controller upon failure or success, and set the options_set flag to True if successful.
        '''
        pass

    def set_options(self):
        '''
        Calls a function on the model to set the options for the bot via a GUI. That function is called on a separate thread.
        '''
        self.options_thread = Thread(target=self.set_options_gui)
        self.options_thread.setDaemon(True)
        self.options_thread.start()

    def play_pause(self):  # sourcery skip: extract-method
        '''
        Depending on the bot status, this function either starts a bot's main_loop() on a new thread, or pauses it.
        '''
        # if the bot is stopped, start it
        if self.status == BotStatus.STOPPED:
            print("play() from bot.py - starting bot")
            self.set_status(BotStatus.RUNNING)
            self.clear_log()
            self.bot_thread = Thread(target=self.main_loop)
            self.bot_thread.setDaemon(True)
            self.bot_thread.start()
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
