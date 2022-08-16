'''
The OSNRBot class contains properties and functions that are specific to the OSNR client. This class should
be inherited by OSNR script classes.
'''
from abc import ABCMeta
import utilities.bot_cv as bcv
import utilities.runelite_cv as rcv
from enum import Enum
from model.runelite_bot import RuneliteBot
from utilities.bot_cv import Point
import pyautogui as pag
import time


class OSNRBot(RuneliteBot, metaclass=ABCMeta):
    class Spellbook(Enum):
        '''
        TODO: Consider moving to parent class.
        '''
        standard = 0
        ancient = 1

    # -- Teleports --
    spellbook_standard_home = Point(578, 258)
    spellbook_standard_tele_menu = Point(591, 307)

    spellbook_ancients_home = Point(581, 251)
    spellbook_ancients_tele_menu = Point(713, 250)

    teleport_menu_search = Point(63, 49)
    teleport_menu_search_result = Point(305, 100)

    # -- Bank Points --
    presets_btn = Point(458, 50)
    presets_load_btn = Point(76, 315)
    presets_close_btn = Point(490, 65)

    def __disable_private_chat(self):
        '''
        Disables private chat in game.
        '''
        self.log_msg("Disabling private chat...")
        private_btn = Point(218, 517)
        show_none_btn = Point(225, 489)
        self.mouse.move_to(private_btn, duration=0.5, variance=3)
        pag.rightClick()
        time.sleep(0.05)
        self.mouse.move_to(show_none_btn, duration=0.2, variance=1)
        pag.click()

    def teleport_and_bank(self, spellbook: Spellbook) -> bool:
        '''
        Teleports to a predefined location and enters the bank interface.
        Args:
            spellbook: The spellbook to use.
        Returns:
            True if successful, False otherwise.
        '''
        if not self.teleport_to(spellbook, "Castle Wars"):
            return False

        if not self.status_check_passed():
            return

        time.sleep(4)

        if not self.status_check_passed():
            return

        bank_icon = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/minimap_bank_icon.png", self.rect_minimap, conf=0.8)
        if bank_icon is None:
            self.log_msg("Bank icon not found.")
            return False
        self.mouse.move_to(Point(bank_icon.x-3, bank_icon.y-3), duration=0.5)
        pag.click()

        if not self.status_check_passed():
            return

        time.sleep(4)

        if not self.status_check_passed():
            return

        banks = self.get_all_tagged_in_rect(self.rect_game_view, self.TAG_PINK)
        if len(banks) == 0:
            self.log_msg("No banks found.")
            return False
        self.mouse.move_to(banks[0], duration=0.5)
        pag.click()
        return True

    def teleport_home(self, spellbook: Spellbook):
        '''
        Teleports to the home location.
        '''
        self.log_msg("Teleporting to home...")
        self.mouse.move_to(self.cp_spellbook, duration=0.5, variance=2)
        pag.click()
        time.sleep(0.5)
        if spellbook == self.Spellbook.standard:
            self.mouse.move_to(self.spellbook_standard_home, duration=0.5, variance=1)
        elif spellbook == self.Spellbook.ancient:
            self.mouse.move_to(self.spellbook_ancients_home, duration=0.5, variance=1)
        pag.click()

    def teleport_to(self, spellbook: Spellbook, location: str) -> bool:
        '''
        Teleports player to a location from the teleport menu interface.
        Args:
            location: The location name to lookup in the teleport interface.
        Returns:
            True if successful, False otherwise.
        '''
        self.log_msg(f"Teleporting to {location}...")
        self.mouse.move_to(self.cp_spellbook, duration=0.5, variance=2)
        pag.click()
        time.sleep(0.5)

        if not self.status_check_passed():
            return

        if spellbook == self.Spellbook.standard:
            self.mouse.move_to(self.spellbook_standard_tele_menu, duration=0.5)
        elif spellbook == self.Spellbook.ancient:
            self.mouse.move_to(self.spellbook_ancients_tele_menu, duration=0.5)
        pag.click()
        time.sleep(1.5)

        if not self.status_check_passed():
            return

        self.mouse.move_to(self.teleport_menu_search, duration=0.5)
        pag.click()
        time.sleep(1)
        no_result_rgb = pag.pixel(self.teleport_menu_search_result.x, self.teleport_menu_search_result.y)
        pag.typewrite(location, interval=0.05)

        if not self.status_check_passed():
            return

        time.sleep(1.5)
        if no_result_rgb == pag.pixel(self.teleport_menu_search_result.x, self.teleport_menu_search_result.y):
            self.log_msg(f"No results found for {location}.")
            return False
        self.mouse.move_to(self.teleport_menu_search_result, duration=0.5, variance=1)
        pag.click()
        self.log_msg("Teleport successful.")
        return True

    def toggle_auto_retaliate(self, toggle_on: bool):
        '''
        Toggles auto retaliate. Assumes client window is configured.
        Args:
            toggle_on: Whether to turn on or off.
        '''
        self.log_msg("Toggling auto retaliate...")
        # click the combat tab
        self.mouse.move_to(self.cp_combat, duration=1, variance=3)
        pag.click()
        time.sleep(0.5)

        # Search for the auto retaliate button (deselected)
        # If None, then auto retaliate is on.
        auto_retal_btn = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/near_reality/cp_combat_autoretal.png", self.rect_inventory, conf=0.9)

        if toggle_on and auto_retal_btn is not None or not toggle_on and auto_retal_btn is None:
            self.mouse.move_to((644, 402), 0.2, variance=5)
            pag.click()
        elif toggle_on:
            print("Auto retaliate is already on.")
        else:
            print("Auto retaliate is already off.")

    def load_preset(self):
        '''
        Loads the default preset from the bank interface.
        '''
        self.log_msg("Loading preset...")
        self.mouse.move_to(self.presets_btn, duration=0.2, variance=2)
        pag.click()
        time.sleep(1)
        self.mouse.move_to(self.presets_load_btn, duration=0.2, variance=1)
        pag.click()
        time.sleep(1)
        self.mouse.move_to(self.presets_close_btn, duration=0.2, variance=1)
        pag.click()
        time.sleep(1)

    def setup_osnr(self, set_layout_fixed=True, logout_runelite=False, collapse_runelite_settings=True, zoom_percentage=25):
        '''
        Sets up the OSNR client.
        '''
        self.setup_client(window_title="Near-Reality",
                          set_layout_fixed=set_layout_fixed,
                          logout_runelite=logout_runelite,
                          collapse_runelite_settings=collapse_runelite_settings)
        self.set_camera_zoom(zoom_percentage)
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.cp_inventory)
        self.mouse.click()
        time.sleep(0.5)
        self.__disable_private_chat()
        time.sleep(0.5)
