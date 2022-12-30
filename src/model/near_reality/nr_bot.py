"""
The NRBot class contains properties and functions that are specific to the NR client. This class should
be inherited by NR script classes.
"""
import time
from abc import ABCMeta

import pyautogui as pag

from model.runelite_bot import RuneLiteBot, RuneLiteWindow
from utilities.geometry import Point


class NRBot(RuneLiteBot, metaclass=ABCMeta):
    win: RuneLiteWindow = None

    def __init__(self, bot_title, description) -> None:
        super().__init__("Near-Reality", bot_title, description, RuneLiteWindow("Near-Reality"))

    def disable_private_chat(self):
        """
        Disables private chat in game.
        """
        self.log_msg("Disabling private chat...")
        self.mouse.move_to(self.win.chat_tabs[3].random_point())
        pag.rightClick()
        time.sleep(0.05)
        self.mouse.move_rel(0, -28, 5, 2)
        pag.click()

    # # -- Banking --
    # def close_bank(self):
    #     '''
    #     Closes the bank interface.
    #     '''
    #     self.log_msg("Closing bank...")
    #     self.mouse.move_to(self.win.bank_close_btn())
    #     pag.click()
    #     time.sleep(1)

    # def deposit_inventory(self) -> bool:
    #     '''
    #     From within the banking interface, clicks the "deposit all" button.
    #     '''
    #     empty = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/bank_deposit_all.png", self.win.game_view)
    #     if empty is None:
    #         self.log_msg("Cannot find deposit button.")
    #         return False
    #     self.mouse.move_to(empty.random_point())
    #     pag.click()
    #     time.sleep(1)
    #     return True

    # def load_preset(self):
    #     '''
    #     Loads the default preset from the bank interface.
    #     '''
    #     self.log_msg("Loading preset...")
    #     self.mouse.move_to(self.win.presets_btn())
    #     pag.click()
    #     time.sleep(1)
    #     self.mouse.move_to(self.win.presets_load_btn())
    #     pag.click()
    #     time.sleep(1)
    #     self.mouse.move_to(self.win.presets_close_btn())
    #     pag.click()
    #     time.sleep(1)

    # def teleport_and_bank(self, spellbook: Spellbook) -> bool:
    #     '''
    #     Teleports to a predefined location and enters the bank interface.
    #     Args:
    #         spellbook: The spellbook to use.
    #     Returns:
    #         True if successful, False otherwise.
    #     '''
    #     if not self.teleport_to(spellbook, "Castle Wars"):
    #         return False

    #     if not self.status_check_passed():
    #         return

    #     time.sleep(4)

    #     if not self.status_check_passed():
    #         return

    #     bank_icon = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/minimap_bank_icon.png",
    #                                        self.win.rect_minimap(),
    #                                        confidence=0.8)
    #     if bank_icon is None:
    #         self.log_msg("Bank icon not found.")
    #         return False
    #     self.mouse.move_to(bank_icon.random_point())
    #     pag.click()

    #     if not self.status_check_passed():
    #         return

    #     time.sleep(4)

    #     if not self.status_check_passed():
    #         return

    #     banks = self.get_all_tagged_in_rect(self.win.rect_game_view(), self.PINK)
    #     if len(banks) == 0:
    #         self.log_msg("No banks found.")
    #         return False
    #     self.mouse.move_to(banks[0])
    #     pag.click()
    #     return True

    # # Teleporting
    # def teleport_home(self, spellbook: Spellbook):
    #     '''
    #     Teleports to the home location.
    #     '''
    #     self.log_msg("Teleporting to home...")
    #     self.mouse.move_to(self.win.cp_tab(7))
    #     pag.click()
    #     time.sleep(0.5)
    #     self.mouse.move_to(self.win.spellbook_home_tele(spellbook), mouseSpeed='medium')
    #     pag.click()

    # def teleport_to(self, spellbook: Spellbook, location: str) -> bool:
    #     '''
    #     Teleports player to a location from the teleport menu interface.
    #     Args:
    #         spellbook: The player's current spellbook.
    #         location: The location name to lookup in the teleport interface.
    #     Returns:
    #         True if successful, False otherwise.
    #     '''
    #     self.log_msg(f"Teleporting to {location}...")
    #     self.mouse.move_to(self.win.cp_tab(7), mouseSpeed='medium')
    #     pag.click()
    #     time.sleep(0.5)

    #     if not self.status_check_passed():
    #         return

    #     self.mouse.move_to(self.win.teleport_menu(spellbook), mouseSpeed='medium')
    #     pag.click()
    #     time.sleep(1.5)

    #     if not self.status_check_passed():
    #         return

    #     self.mouse.move_to(self.win.teleport_menu_search(), mouseSpeed='medium')
    #     pag.click()
    #     time.sleep(1)
    #     result = self.win.teleport_menu_search_result()
    #     no_result_rgb = pag.pixel(result.x, result.y)
    #     pag.typewrite(location, interval=0.05)

    #     if not self.status_check_passed():
    #         return

    #     time.sleep(1.5)
    #     new_result = self.win.teleport_menu_search_result()
    #     if no_result_rgb == pag.pixel(new_result.x, new_result.y):
    #         self.log_msg(f"No results found for {location}.")
    #         return False
    #     self.mouse.move_to(new_result, mouseSpeed='medium')
    #     pag.click()
    #     self.log_msg("Teleport successful.")
    #     return True
