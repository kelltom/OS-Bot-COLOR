'''
A Bot is a base class for bot script models. It is abstract and cannot be instantiated. Many of the methods in this base class are
pre-implemented and can be used by subclasses, or called by the controller. Code in this class should not be modified.
'''
from abc import ABC, abstractmethod
from enum import Enum
from model.window import Window
from threading import Thread
from utilities.mouse_utils import MouseUtils
from utilities.options_builder import OptionsBuilder
import customtkinter
import keyboard
import pygetwindow
import time
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


class BotStatus(Enum):
    """
    BotStatus enum.
    """
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3
    CONFIGURING = 4


class Bot(ABC):
    mouse = MouseUtils()
    options_set: bool = False
    progress: float = 0
    status = BotStatus.STOPPED
    thread: Thread = None
    win: Window = None

    # ---- Abstract Functions ----
    @abstractmethod
    def __init__(self, title, description, window: Window):
        self.title = title
        self.description = description
        self.options_builder = OptionsBuilder(title)
        self.win = window

    @abstractmethod
    def main_loop(self):
        '''
        Main logic of the bot. This function is called in a separate thread.
        '''
        pass

    @abstractmethod
    def create_options(self):
        '''
        Defines the options for the bot using the OptionsBuilder.
        '''
        pass

    @abstractmethod
    def save_options(self, options: dict):
        '''
        Saves a dictionary of options as properties of the bot.
        Args:
            options: dict - dictionary of options to save
        '''
        pass

    def get_options_view(self, parent) -> customtkinter.CTkFrame:
        '''
        Builds the options view for the bot based on the options defined in the OptionsBuilder.
        '''
        self.clear_log()
        self.log_msg("Options panel opened.")
        self.create_options()
        view = self.options_builder.build_ui(parent, self.controller)
        self.options_builder.options = {}
        return view

    def play_pause(self):
        '''
        Depending on the bot status, this function either starts a bot's main_loop() on a new thread, or pauses it.
        '''
        if self.status == BotStatus.STOPPED:
            self.clear_log()
            self.log_msg("Starting bot...")
            if not self.options_set:
                self.log_msg("Options not set. Please set options before starting.")
                return
            if not self.__initialize_window():
                self.log_msg("Bot.play_pause(): Failed to initialize window.")
                return
            self.reset_progress()
            self.set_status(BotStatus.RUNNING)
            self.thread = Thread(target=self.main_loop)
            self.thread.setDaemon(True)
            self.thread.start()
        elif self.status == BotStatus.RUNNING:
            self.log_msg("Pausing bot...")
            self.set_status(BotStatus.PAUSED)
        elif self.status == BotStatus.PAUSED:
            self.log_msg("Resuming bot...")
            if not self.__initialize_window():
                self.set_status(BotStatus.STOPPED)
                print("Bot.play_pause(): Failed to initialize window.")
            self.set_status(BotStatus.RUNNING)
    
    def __initialize_window(self) -> bool:
        '''
        Attempts to focus and initialize the game window by identifying core UI elements.
        Returns:
            bool - True if the window was successfully initialized, False otherwise.
        '''
        try:
            self.win.focus()
            time.sleep(0.5)
            return self.win.initialize()
        except pygetwindow.PyGetWindowException as e:
            print(f"Error: {e}")
            self.set_status(BotStatus.STOPPED)
            return False

    def stop(self):
        '''
        Fired when the user stops the bot manually.
        '''
        self.log_msg("Manual stop requested. Attempting to stop...")
        if self.status != BotStatus.STOPPED:
            self.set_status(BotStatus.STOPPED)
        else:
            self.log_msg("Bot is already stopped.")

    def __check_interrupt(self):
        '''
        Checks for keyboard interrupts.
        '''
        if keyboard.is_pressed("-"):
            if self.status == BotStatus.RUNNING:
                self.log_msg("Pausing bot...")
                self.set_status(BotStatus.PAUSED)
        elif keyboard.is_pressed("="):
            if self.status == BotStatus.PAUSED:
                self.log_msg("Resuming bot...")
                if not self.__initialize_window():
                    self.set_status(BotStatus.STOPPED)
                    print("Bot.__check_interrupt(): Failed to initialize window.")
                    return
                self.set_status(BotStatus.RUNNING)
        elif keyboard.is_pressed("ESC"):
            self.stop()

    def status_check_passed(self, timeout: int = 120) -> bool:
        '''
        Does routine check for:
            - Bot status (stops/pauses)
            - Keyboard interrupts
        Best used in main_loop() inner loops while bot is waiting for a
        condition to be met. If the Bot Status is PAUSED, this function
        will enter a loop waiting for the status to change to RUNNING/STOPPED.
        Args:
            timeout: int - number of seconds to pause for if bot is paused.
        Returns:
            True if the bot is safe to continue, False if the bot should terminate.
        Example:
            if not self.status_check_passed():
                return
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
    def reset_progress(self):
        '''
        Resets the current progress property to 0 and notifies the controller to update UI.
        '''
        self.progress = 0
        self.controller.update_progress()

    def update_progress(self, progress: float):
        '''
        Updates the progress property and notifies the controller to update UI.
        Args:
            progress: float - number between 0 and 1 indicating percentage of progress.
        '''
        if progress < 0:
            progress = 0
        elif progress > 1:
            progress = 1
        self.progress = progress
        self.controller.update_progress()

    def set_status(self, status: BotStatus):
        '''
        Sets the status property of the bot and notifies the controller to update UI accordingly.
        Args:
            status: BotStatus - status to set the bot to
        '''
        self.status = status
        self.controller.update_status()

    def log_msg(self, msg: str, overwrite=False):
        '''
        Sends a message to the controller to be displayed in the log for the user.
        Args:
            msg: str - message to log
            overwrite: bool - if True, overwrites the current log message. If False, appends to the log.
        '''
        self.controller.update_log(msg, overwrite)

    def clear_log(self):
        '''
        Requests the controller to tell the UI to clear the log.
        '''
        self.controller.clear_log()
