'''
A Bot is a base class for bot script models. It is abstract and cannot be instantiated. Many of the methods in this base class are
pre-implemented and can be used by subclasses, or called by the controller. Code in this class should not be modified.
'''
from abc import ABC, abstractmethod
from deprecated import deprecated
from enum import Enum
from model.window import Window
from threading import Thread
from utilities.geometry import Point, Rectangle
from utilities.mouse_utils import MouseUtils
from utilities.options_builder import OptionsBuilder
import customtkinter
import keyboard
import numpy as np
import pyautogui as pag
import pygetwindow
import pytweening
import time
import utilities.bot_cv as bcv
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

    GREEN = [0, 255, 0]
    RED = [255, 0, 0]

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
            success = self.win.initialize()
            if not success:
                msg = "Failed to initialize window. Make sure the client is NOT in 'Resizable-Modern' " \
                      "mode. Make sure you're using the default client configuration (E.g., Opaque UI, status orbs ON)."
                self.log_msg(msg)
                return False
            return True
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

    # --- Misc Utility Functions
    def drop_inventory(self, skip_rows: int = 0, skip_slots: list[int] = None) -> None:
        '''
        Drops all items in the inventory.
        Args:
            skip_rows: The number of rows to skip before dropping.
            skip_slots: The indices of slots to avoid dropping.
        '''
        self.log_msg("Dropping inventory...")
        # Determine slots to skip
        if skip_slots is None:
            skip_slots = []
        if skip_rows > 0:
            row_skip = list(range(skip_rows*4))
            skip_slots = np.unique(row_skip + skip_slots)
        # Start dropping
        pag.keyDown("shift")
        for i, slot in enumerate(self.win.inventory_slots):
            if not self.status_check_passed():
                pag.keyUp("shift")
                return
            if i in skip_slots:
                continue
            p = slot.random_point()
            self.mouse.move_to((p[0], p[1]),
                                mouseSpeed='fastest',
                                knotsCount=1,
                                offsetBoundaryY=40,
                                offsetBoundaryX=40,
                                tween=pytweening.easeInOutQuad)
            pag.click()
        pag.keyUp("shift")

    def friends_nearby(self) -> bool:
        '''
        Checks the minimap for green dots to indicate friends nearby.
        Returns:
            True if friends are nearby, False otherwise.
        '''
        # screenshot minimap
        minimap = bcv.screenshot(self.win.minimap)
        bcv.save_image("minimap.png", minimap)
        only_friends = bcv.isolate_colors(minimap, [self.GREEN])
        bcv.save_image("minimap_friends.png", only_friends)
        mean = only_friends.mean(axis=(0, 1))
        return mean != 0.0

    def logout(self):
        '''
        Logs player out.
        '''
        self.log_msg("Logging out...")
        self.mouse.move_to(self.win.cp_tabs[10].random_point())
        pag.click()
        time.sleep(1)
        self.mouse.move_rel(0, -53, 5, 5)  # Logout button
        pag.click()

    # --- Player Status Functions ---
    def has_hp_bar(self) -> bool:
        '''
        Returns whether the player has an HP bar above their head. Useful alternative to using OCR to check if the
        player is in combat. This function only works when the game camera is all the way up.
        '''
        # Position of character relative to the screen
        char_pos = self.win.game_view.get_center()

        # Make a rectangle around the character
        offset = 30
        char_rect = Rectangle.from_points(Point(char_pos.x - offset, char_pos.y - offset*2),
                                          Point(char_pos.x + offset, char_pos.y))
        # Take a screenshot of rect
        char_screenshot = bcv.screenshot(char_rect)
        # Isolate HP bars in that rectangle
        hp_bars = bcv.isolate_colors(char_screenshot, [self.RED, self.GREEN])
        # If there are any HP bars, return True
        return hp_bars.mean(axis=(0, 1)) != 0.0
    
    @deprecated(reason="The OCR this function uses may be innacurate. Consider using an API function, or check colors on the win.hp_bar.")
    def get_hp(self) -> int:
        """
        Gets the HP value of the player.
        Returns:
            The HP of the player, or None if not found.
        """
        res = bcv.get_numbers_in_rect(self.win.hp_orb_text, True)
        print(res)
        return None if res is None else res[0]

    @deprecated(reason="The OCR this function uses may be innacurate. Consider using an API function, or check colors on the win.prayer_bar.")
    def get_prayer(self) -> int:
        """
        Gets the prayer value of the player.
        Returns:
            The prayer value of the player, or None if not found.
        """
        res = bcv.get_numbers_in_rect(self.win.prayer_orb_text, True)
        print(res)
        return None if res is None else res[0]

    # --- Client Settings ---
    # TODO: Add anti-ban functions that move camera around randomly
    def move_camera_up(self):
        '''
        Moves the camera up.
        '''
        # Position the mouse somewhere on the game view
        self.mouse.move_to(self.win.game_view.get_center())
        pag.keyDown('up')
        time.sleep(2)
        pag.keyUp('up')
        time.sleep(0.5)

    def set_camera_zoom(self, percentage: int) -> bool:
        '''
        Sets the camera zoom level.
        Args:
            percentage: The percentage of the camera zoom level to set.
        Returns:
            True if the zoom level was set, False if an issue occured.
        '''
        if percentage < 1:
            percentage = 1
        elif percentage > 100:
            percentage = 100
        self.log_msg(f"Setting camera zoom to {percentage}%...")
        if not self.__open_display_settings():
            return False
        scroll_rect = Rectangle(left=self.win.control_panel.left + 84, top=self.win.control_panel.top + 146,
                                width=102, height=8)
        x = int((percentage / 100) * (scroll_rect.left + scroll_rect.width - scroll_rect.left) + scroll_rect.left)
        p = scroll_rect.random_point()
        self.mouse.move_to((x, p.y))
        self.mouse.click()
        return True
    
    def __open_display_settings(self) -> bool:
        '''
        Opens the display settings for the game client.
        Returns:
            True if the settings were opened, False if an error occured.
        '''
        control_panel = self.win.control_panel
        self.mouse.move_to(self.win.cp_tabs[11].random_point())
        self.mouse.click()
        time.sleep(0.5)
        display_tab = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/cp_settings_display_tab.png", control_panel)
        if display_tab is None:
            self.log_msg("Could not find the display settings tab.")
            return False
        self.mouse.move_to(display_tab.random_point())
        self.mouse.click()
        time.sleep(0.5)
        return True