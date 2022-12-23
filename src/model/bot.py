"""
A Bot is a base class for bot script models. It is abstract and cannot be instantiated. Many of the methods in this base class are
pre-implemented and can be used by subclasses, or called by the controller. Code in this class should not be modified.
"""
import re
import time
import warnings
from abc import ABC, abstractmethod
from enum import Enum
from threading import Thread
from typing import List, Union

import customtkinter
import keyboard
import numpy as np
import pyautogui as pag
import pygetwindow
import pytweening
from deprecated import deprecated

import utilities.color as clr
import utilities.debug as debug
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
from utilities.geometry import Point, Rectangle
from utilities.mouse_utils import MouseUtils
from utilities.options_builder import OptionsBuilder
from utilities.window import Window, WindowInitializationError
from utilities.random_util import RandomUtil as rm
from utilities.api import item_ids as ids
from utilities.api.status_socket import StatusSocket

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
    # --- Properties ---
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
        """
        Main logic of the bot. This function is called in a separate thread.
        """
        pass

    @abstractmethod
    def create_options(self):
        """
        Defines the options for the bot using the OptionsBuilder.
        """
        pass

    @abstractmethod
    def save_options(self, options: dict):
        """
        Saves a dictionary of options as properties of the bot.
        Args:
            options: dict - dictionary of options to save
        """
        pass

    def get_options_view(self, parent) -> customtkinter.CTkFrame:
        """
        Builds the options view for the bot based on the options defined in the OptionsBuilder.
        """
        self.clear_log()
        self.log_msg("Options panel opened.")
        self.create_options()
        view = self.options_builder.build_ui(parent, self.controller)
        self.options_builder.options = {}
        return view

    def play_pause(self):
        """
        Depending on the bot status, this function either starts a bot's main_loop() on a new thread, or pauses it.
        """
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
        """
        Attempts to focus and initialize the game window by identifying core UI elements.
        Returns:
            bool - True if the window was successfully initialized, False otherwise.
        """
        try:
            self.win.focus()
            time.sleep(0.5)
        except pygetwindow.PyGetWindowException as e:
            return self.__halt_with_msg(str(e))
        try:
            self.win.initialize()
            return True
        except WindowInitializationError as e:
            return self.__halt_with_msg(str(e))

    def stop(self):
        """
        Fired when the user stops the bot manually.
        """
        self.log_msg("Manual stop requested. Attempting to stop...")
        if self.status != BotStatus.STOPPED:
            self.set_status(BotStatus.STOPPED)
        else:
            self.log_msg("Bot is already stopped.")

    def __check_interrupt(self):
        """
        Checks for keyboard interrupts.
        """
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
        """
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
        """
        # Check for keypress interrupts
        self.__check_interrupt()
        # Check status
        if self.status == BotStatus.STOPPED:
            self.log_msg("Bot has been stopped.")
            return False
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
                    return self.__halt_with_msg("Timeout reached, stopping...")
                if self.status == BotStatus.PAUSED:
                    self.log_msg(msg=f"Terminating in {timeout}.", overwrite=True)
                    continue
        return True

    def __halt_with_msg(self, msg):
        self.log_msg(msg)
        self.set_status(BotStatus.STOPPED)
        return False

    # ---- Controller Setter ----
    def set_controller(self, controller):
        self.controller = controller

    # ---- Functions that notify the controller of changes ----
    def reset_progress(self):
        """
        Resets the current progress property to 0 and notifies the controller to update UI.
        """
        self.progress = 0
        self.controller.update_progress()

    def update_progress(self, progress: float):
        """
        Updates the progress property and notifies the controller to update UI.
        Args:
            progress: float - number between 0 and 1 indicating percentage of progress.
        """
        if progress < 0:
            progress = 0
        elif progress > 1:
            progress = 1
        self.progress = progress
        self.controller.update_progress()

    def set_status(self, status: BotStatus):
        """
        Sets the status property of the bot and notifies the controller to update UI accordingly.
        Args:
            status: BotStatus - status to set the bot to
        """
        self.status = status
        self.controller.update_status()

    def log_msg(self, msg: str, overwrite=False):
        """
        Sends a message to the controller to be displayed in the log for the user.
        Args:
            msg: str - message to log
            overwrite: bool - if True, overwrites the current log message. If False, appends to the log.
        """
        self.controller.update_log(msg, overwrite)

    def clear_log(self):
        """
        Requests the controller to tell the UI to clear the log.
        """
        self.controller.clear_log()

    # --- Misc Utility Functions
    def drop_inventory(self, skip_rows: int = 0, skip_slots: list[int] = None) -> None:
        """
        Drops all items in the inventory.
        Args:
            skip_rows: The number of rows to skip before dropping.
            skip_slots: The indices of slots to avoid dropping.
        """
        self.log_msg("Dropping inventory...")
        # Determine slots to skip
        if skip_slots is None:
            skip_slots = []
        if skip_rows > 0:
            row_skip = list(range(skip_rows * 4))
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
            self.mouse.move_to(
                (p[0], p[1]),
                mouseSpeed="fastest",
                knotsCount=1,
                offsetBoundaryY=40,
                offsetBoundaryX=40,
                tween=pytweening.easeInOutQuad,
            )
            pag.click()
        pag.keyUp("shift")

    def drop_selected_items(self, ids, api: StatusSocket):
        """
        drops all selected items in inventory

        id number can be found at items_ids.py

        example: self.drop_selected_items(ids.526,api_status) will select & drop bones

        you will need to create a list inside items_ids.py to select multiple items

        """

        self.log_msg("dropping item...")
        items = api.get_inv_item_indices(ids)

        for item in items:
            pag.keyDown("shift")
            self.mouse.move_to(self.win.inventory_slots[item].random_point())
            self.mouse.click()
            rm.sleep_random(0.35, 0.5)
            pass
        else:
            pag.keyUp("shift")
            pass

    def leftclick_items(self, ids, api: StatusSocket):
        """
        left clicks all selected items in inventory

        ids number can be found at items_ids.py

        example: self.__leftclick_items(ids.526,api_status) will select & bury bones

        you will need to create a list inside items_ids.py to select multiple items

        """

        self.log_msg("left clicking item...")
        items = api.get_inv_item_indices(ids)

        for item in items:
            self.mouse.move_to(self.win.inventory_slots[item].random_point())
            self.mouse.click()
            rm.sleep_random(0.7, 1.2)


    def friends_nearby(self) -> bool:
        """
        Checks the minimap for green dots to indicate friends nearby.
        Returns:
            True if friends are nearby, False otherwise.
        """
        minimap = self.win.minimap.screenshot()
        # debug.save_image("minimap.png", minimap)
        only_friends = clr.isolate_colors(minimap, [clr.GREEN])
        # debug.save_image("minimap_friends.png", only_friends)
        mean = only_friends.mean(axis=(0, 1))
        return mean != 0.0

    def logout(self):  # sourcery skip: class-extract-method
        """
        Logs player out.
        """
        self.log_msg("Logging out...")
        self.mouse.move_to(self.win.cp_tabs[10].random_point())
        pag.click()
        time.sleep(1)
        self.mouse.move_rel(0, -53, 5, 5)
        pag.click()

    # --- Player Status Functions ---
    def has_hp_bar(self) -> bool:
        """
        Returns whether the player has an HP bar above their head. Useful alternative to using OCR to check if the
        player is in combat. This function only works when the game camera is all the way up.
        """
        # Position of character relative to the screen
        char_pos = self.win.game_view.get_center()

        # Make a rectangle around the character
        offset = 30
        char_rect = Rectangle.from_points(
            Point(char_pos.x - offset, char_pos.y - offset),
            Point(char_pos.x + offset, char_pos.y + offset),
        )
        # Take a screenshot of rect
        char_screenshot = char_rect.screenshot()
        # Isolate HP bars in that rectangle
        hp_bars = clr.isolate_colors(char_screenshot, [clr.RED, clr.GREEN])
        debug.save_image("hp_bars.png", hp_bars)
        # If there are any HP bars, return True
        return hp_bars.mean(axis=(0, 1)) != 0.0

    def get_hp(self) -> int:
        """
        Gets the HP value of the player.
        """
        res = ocr.extract_text(self.win.hp_orb_text, ocr.PLAIN_11, [clr.ORB_GREEN, clr.ORB_RED])
        return int(res[0]) if (res := re.findall(r"\d+", res)) else None

    def get_prayer(self) -> int:
        """
        Gets the Prayer points of the player.
        """
        res = ocr.extract_text(self.win.prayer_orb_text, ocr.PLAIN_11, [clr.ORB_GREEN, clr.ORB_RED])
        return int(res) if (res := re.findall(r"\d+", res)) else None

    def get_run_energy(self) -> int:
        """
        Gets the run energy of the player.
        """
        res = ocr.extract_text(self.win.run_orb_text, ocr.PLAIN_11, [clr.ORB_GREEN, clr.ORB_RED])
        return int(res) if (res := re.findall(r"\d+", res)) else None

    def get_special_energy(self) -> int:
        """
        Gets the special attack energy of the player.
        """
        res = ocr.extract_text(self.win.spec_orb_text, ocr.PLAIN_11, [clr.ORB_GREEN, clr.ORB_RED])
        return int(res) if (res := re.findall(r"\d+", res)) else None

    def get_total_xp(self) -> int:
        """
        Gets the total XP of the player using OCR.
        """
        fonts = [ocr.PLAIN_11, ocr.PLAIN_12, ocr.BOLD_12]
        for font in fonts:
            res = ocr.extract_text(self.win.total_xp, font, [clr.WHITE])
            if res := re.findall(r"\d+", res):
                return int(res[0])
        return None

    # --- OCR Functions ---
    def mouseover_text(
        self,
        contains: Union[str, List[str]] = None,
        color: Union[clr.Color, List[clr.Color]] = None,
    ) -> Union[bool, str]:
        """
        Examines the mouseover text area.
        Args:
            contains: The text to search for (single word, phrase, or list of words). Case sensitive. If left blank,
                      returns all text in the mouseover area.
            color: The color(s) to isolate. If left blank, isolates all expected colors. Consider using
                   clr.OFF_* colors for best results.
        Returns:
            True if exact string is found, False otherwise.
            If args are left blank, returns the text in the mouseover area.
        """
        if color is None:
            color = [
                clr.OFF_CYAN,
                clr.OFF_GREEN,
                clr.OFF_ORANGE,
                clr.OFF_WHITE,
                clr.OFF_YELLOW,
            ]
        if contains is None:
            return ocr.extract_text(self.win.mouseover, ocr.BOLD_12, color)
        return bool(ocr.find_text(contains, self.win.mouseover, ocr.BOLD_12, color))

    def chatbox_text(self, contains: str = None) -> Union[bool, str]:
        """
        Examines the chatbox for text. Currently only captures player chat text.
        Args:
            contains: The text to search for (single word or phrase). Case sensitive. If left blank,
                      returns all text in the chatbox.
        Returns:
            True if exact string is found, False otherwise.
            If args are left blank, returns the text in the chatbox.
        """
        if contains is None:
            return ocr.extract_text(self.win.chat, ocr.PLAIN_12, clr.BLUE)
        if ocr.find_text(contains, self.win.chat, ocr.PLAIN_12, clr.BLUE):
            return True

    # --- Client Settings ---
    # TODO: Add anti-ban functions that move camera around randomly
    def move_camera_up(self):
        """
        Moves the camera up.
        """
        # Position the mouse somewhere on the game view
        self.mouse.move_to(self.win.game_view.get_center())
        pag.keyDown("up")
        time.sleep(2)
        pag.keyUp("up")
        time.sleep(0.5)

    def set_compass_north(self):
        self.log_msg("Setting compass North...")
        self.mouse.move_to(self.win.compass_orb.random_point())
        self.mouse.click()

    def set_compass_west(self):
        self.__compass_right_click("Setting compass West...", 72)

    def set_compass_east(self):
        self.__compass_right_click("Setting compass East...", 43)

    def set_compass_south(self):
        self.__compass_right_click("Setting compass South...", 57)

    def __compass_right_click(self, msg, rel_y):
        self.log_msg(msg)
        self.mouse.move_to(self.win.compass_orb.random_point())
        pag.rightClick()
        self.mouse.move_rel(0, rel_y, 5, 2)
        self.mouse.click()

    def set_camera_zoom(self, percentage: int) -> bool:
        """
        Sets the camera zoom level.
        Args:
            percentage: The percentage of the camera zoom level to set.
        Returns:
            True if the zoom level was set, False if an issue occured.
        """
        if percentage < 1:
            percentage = 1
        elif percentage > 100:
            percentage = 100
        self.log_msg(f"Setting camera zoom to {percentage}%...")
        if not self.__open_display_settings():
            return False
        scroll_rect = Rectangle(
            left=self.win.control_panel.left + 84,
            top=self.win.control_panel.top + 146,
            width=102,
            height=8,
        )
        x = int((percentage / 100) * (scroll_rect.left + scroll_rect.width - scroll_rect.left) + scroll_rect.left)
        p = scroll_rect.random_point()
        self.mouse.move_to((x, p.y))
        self.mouse.click()
        return True

    def toggle_auto_retaliate(self, toggle_on: bool):
        """
        Toggles auto retaliate. Assumes client window is configured.
        Args:
            toggle_on: Whether to turn on or off.
        """
        state = "on" if toggle_on else "off"
        self.log_msg(f"Toggling auto retaliate {state}...")
        # click the combat tab
        self.mouse.move_to(self.win.cp_tabs[0].random_point())
        pag.click()
        time.sleep(0.5)

        if toggle_on:
            if auto_retal_btn := imsearch.search_img_in_rect(
                imsearch.BOT_IMAGES.joinpath("near_reality", "cp_combat_autoretal.png"),
                self.win.control_panel,
            ):
                self.mouse.move_to(auto_retal_btn.random_point(), mouseSpeed="medium")
                self.mouse.click()
            else:
                self.log_msg("Auto retaliate is already on.")
        elif auto_retal_btn := imsearch.search_img_in_rect(
            imsearch.BOT_IMAGES.joinpath("near_reality", "cp_combat_autoretal_on.png"),
            self.win.control_panel,
        ):
            self.mouse.move_to(auto_retal_btn.random_point(), mouseSpeed="medium")
            self.mouse.click()
        else:
            self.log_msg("Auto retaliate is already off.")

    def toggle_melee_attack(self, toggle_on: bool):
        """
        Toggles attack option. Assumes client window is configured.

        weapon support: 2h swords, godswords, axes, battleaxes, mauls, warhammers, bulwark,
                        claws, pickaxes, long swords, machetes, scimitars, sickles, maces,
                        daggers, harpoons, swords, whips

            toggle_on: Whether to turn on or off.
        """
        state = "on" if toggle_on else "off"
        self.log_msg(f"Toggling attack option {state}...")
        # click the combat tab
        self.mouse.move_to(self.win.cp_tabs[0].random_point())
        pag.click()
        time.sleep(0.5)

        if toggle_on:
            if (
                attack_toggle := imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "attack", "off", "long_sword_off.png"), self.win.control_panel, 0.05  
                )
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "attack", "off", "axe_off.png"), self.win.control_panel, 0.05  
                )
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "attack", "off", "pickaxe_off.png"), self.win.control_panel, 0.05  
                )
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "attack", "off", "bulwark_off.png"), self.win.control_panel, 0.05  
                )
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "attack", "off", "claw_off.png"), self.win.control_panel, 0.05 
                )
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "attack", "off", "dagger_off.png"), self.win.control_panel, 0.05 
                )
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "attack", "off", "mace_off.png"), self.win.control_panel, 0.05 
                )
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "attack", "off", "maul_off.png"), self.win.control_panel, 0.05  
                )
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "attack", "off", "whip_off.png"), self.win.control_panel, 0.05  
                )
            ):
                self.mouse.move_to(attack_toggle.random_point(), mouseSpeed="medium")
                self.mouse.click()
            else:
                self.log_msg("attack option is already on.")

    def toggle_melee_strength(self, toggle_on: bool):
        """
        Toggles strength option. Assumes client window is configured.

        weapon support: axe, battleaxe, banners, claws, dagger, harpoon, swords, halberds,
                        longswords, machetes, scimitars, maces, blackjacks, maces,
                        fun weapons, mauls, warhammers, pickaxes, 2h swords, godswords

            toggle_on: Whether to turn on or off.
        """
        state = "on" if toggle_on else "off"
        self.log_msg(f"Toggling strength option {state}...")
        # click the combat tab
        self.mouse.move_to(self.win.cp_tabs[0].random_point())
        pag.click()
        time.sleep(0.5)

        if toggle_on:
            if (
                strength_toggle := imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "strength", "long_sword_off.png"), self.win.control_panel, 0.05  
                )
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "strength", "axe_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "strength", "banner_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "strength", "claw_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "strength", "dagger_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "strength", "hally_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "strength", "mace_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "strength", "maul_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "strength", "pickaxe_off.png"), self.win.control_panel, 0.05  
                )
            ):
                self.mouse.move_to(strength_toggle.random_point(), mouseSpeed="medium")
                self.mouse.click()
            else:
                self.log_msg("strength option is already on.")

    def toggle_melee_controlled(self, toggle_on: bool):
        """
        Toggles controlled option. Assumes client window is configured.

        weapon support: banners, spears, claws, halberds, long swords, machetes, scimitars,
                        sickles, maces, whips

            toggle_on: Whether to turn on or off.
        """
        state = "on" if toggle_on else "off"
        self.log_msg(f"Toggling controlled option {state}...")
        # click the combat tab
        self.mouse.move_to(self.win.cp_tabs[0].random_point())
        pag.click()
        time.sleep(0.5)

        if toggle_on:
            if (
                strength_toggle := imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "controlled", "claw_off.png"), self.win.control_panel, 0.05  
                )
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "controlled", "hally_off.png"), self.win.control_panel, 0.05  
                )
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "controlled", "spear_off.png"), self.win.control_panel, 0.05  
                )
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "controlled", "long_sword_off.png"), self.win.control_panel, 0.05  
                )
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "controlled", "mace_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "controlled", "whip_off.png"), self.win.control_panel, 0.05)  
            ):
                self.mouse.move_to(strength_toggle.random_point(), mouseSpeed="medium")
                self.mouse.click()
            else:
                self.log_msg("controlled option is already on.")

    def toggle_melee_defense(self, toggle_on: bool):
        """
        Toggles defense option. Assumes client window is configured.

        weapon support: axe, battleaxe, banners, claws, dagger, harpoon, swords, halberds,
                        longswords, machetes, scimitars, maces, blackjacks, fun weapons, mauls, warhammers,
                        pickaxes, 2h swords, godswords, whips

            toggle_on: Whether to turn on or off.
        """
        state = "on" if toggle_on else "off"
        self.log_msg(f"Toggling defense option {state}...")
        # click the combat tab
        self.mouse.move_to(self.win.cp_tabs[0].random_point())
        pag.click()
        time.sleep(0.5)

        if toggle_on:
            if (
                strength_toggle := imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "defense", "axe_off.png"), self.win.control_panel, 0.05  
                )
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "defense", "claw_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "defense", "hally_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(
                    imsearch.BOT_IMAGES.joinpath("melee_combat", "defense", "long_sword_off.png"), self.win.control_panel, 0.05  
                )
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "defense", "dagger_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "defense", "mace_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "defense", "maul_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "defense", "pickaxe_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "defense", "spear_off.png"), self.win.control_panel, 0.05)  
                or imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("melee_combat", "defense", "whip_off.png"), self.win.control_panel, 0.05)  
            ):
                self.mouse.move_to(strength_toggle.random_point(), mouseSpeed="medium")
                self.mouse.click()
            else:
                self.log_msg("defense option is already on.")


    def __open_display_settings(self) -> bool:
        """
        Opens the display settings for the game client.
        Returns:
            True if the settings were opened, False if an error occured.
        """
        control_panel = self.win.control_panel
        self.mouse.move_to(self.win.cp_tabs[11].random_point())
        self.mouse.click()
        time.sleep(0.5)
        display_tab = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("cp_settings_display_tab.png"), control_panel)
        if display_tab is None:
            self.log_msg("Could not find the display settings tab.")
            return False
        self.mouse.move_to(display_tab.random_point())
        self.mouse.click()
        time.sleep(0.5)
        return True
