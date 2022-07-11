'''
A Bot is a model for a script that can be run. The script has a status (running, paused, stopped). It can be paused, resumed, and stopped.
The script can also be configured to run for a certain number of iterations. The script can also be configured to take random breaks.
The script should be able to be configured to use a specific key to start, pause and abort. The script will return text information about its progress.
'''
from abc import ABC, abstractmethod
from enum import Enum
import keyboard
from threading import Thread
import time


class BotStatus(Enum):
    """
    BotStatus enum.
    """
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3
    CONFIGURING = 4


class Bot(ABC):
    status = BotStatus.STOPPED
    iterations: int = 0
    current_iter: int = 0
    options_set: bool = False
    thread: Thread = None

    # ---- Abstract Functions ----
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
    def save_options(self, options: dict):
        '''
        Given a dictionary of options, this function should save the options to the model's properties.
        '''
        pass

    def play_pause(self):  # sourcery skip: extract-method
        '''
        Depending on the bot status, this function either starts a bot's main_loop() on a new thread, or pauses it.
        '''
        if self.status == BotStatus.STOPPED:
            self.clear_log()
            if not self.options_set:
                self.log_msg("Options not set. Please set options before starting.")
                return
            self.log_msg("Starting bot...")
            self.reset_iter()
            self.set_status(BotStatus.RUNNING)
            self.thread = Thread(target=self.main_loop)
            self.thread.setDaemon(True)
            self.thread.start()
        elif self.status == BotStatus.RUNNING:
            self.log_msg("Pausing bot...")
            self.set_status(BotStatus.PAUSED)
        elif self.status == BotStatus.PAUSED:
            self.log_msg("Resuming bot...")
            self.set_status(BotStatus.RUNNING)

    def stop(self):
        '''
        This function is fired when the user stops the bot manually.
        '''
        self.log_msg("Manual stop requested. Attempting to stop...")
        if self.status != BotStatus.STOPPED:
            self.set_status(BotStatus.STOPPED)
            self.reset_iter()
        else:
            self.log_msg("Bot is already stopped.")

    def __check_interrupt(self):
        if keyboard.is_pressed("F1"):
            if self.status != BotStatus.PAUSED:
                self.log_msg("Pausing bot...")
                self.set_status(BotStatus.PAUSED)
        elif keyboard.is_pressed("ESC"):
            self.stop()

    def status_check_passed(self, timeout: int = 10) -> bool:
        '''
        Does routine check for:
            - Bot status (stops/pauses)
            - Keyboard interrupts
        This function enters a pause loop for the given timeout. This function also handles sending
        messages to controller. Best used in main_loop() inner loops while bot is waiting for a
        condition to be met.
        Params:
            timeout: int - number of seconds to wait for condition to be met
        Returns:
            True if the bot can continue, False if the bot should terminate.
        '''
        # Check for keypress interrupts
        self.__check_interrupt()
        # Check status
        if self.status == BotStatus.STOPPED:
            self.log_msg("Bot has been stopped.")
            return False
        # If paused, enter loop until status is not paused
        elif self.status == BotStatus.PAUSED:
            self.log_msg("Bot is paused.\n")
            while self.status == BotStatus.PAUSED:
                self.__check_interrupt()
                time.sleep(1)
                if self.status == BotStatus.STOPPED:
                    self.log_msg("Bot has been stopped.")
                    return False
                timeout -= 1
                if timeout == 0:
                    self.log_msg("Timeout reached, stopping...")
                    self.set_status(BotStatus.STOPPED)
                    return False
                if self.status == BotStatus.PAUSED:
                    self.log_msg(msg=f"Terminating in {timeout}.", overwrite=True)
                    continue
        return True

    # ---- Controller Setter ----
    def set_controller(self, controller):
        self.controller = controller

    # ---- Functions that notify the controller of changes ----
    def reset_iter(self):
        '''
        Resets the current iteration property to 0 and notifies the controller to update UI.
        '''
        self.current_iter = 0
        self.controller.update_progress()

    def increment_iter(self):
        '''
        Increments the current iteration property by 1 and notifies the controller to update UI.
        '''
        self.current_iter += 1
        self.controller.update_progress()

    def set_status(self, status: BotStatus):
        '''
        Sets the status property of the bot and notifies the controller to update UI accordingly.
        '''
        self.status = status
        self.controller.update_status()

    def log_msg(self, msg: str, overwrite=False):
        '''
        Sends a message to the controller to be displayed in the log for the user.
        '''
        self.controller.update_log(msg, overwrite)

    def clear_log(self):
        '''
        Requests the controller to tell the UI to clear the log.
        '''
        self.controller.clear_log()
