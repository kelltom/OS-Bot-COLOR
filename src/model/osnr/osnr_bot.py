'''
The OSNRBot class contains properties and functions that are specific to the OSNR client. This class should
be inherited by OSNR script classes.
'''
from abc import ABCMeta
from model.runelite_bot import RuneliteBot
from model.bot import Point
import pyautogui as pag
import time


class OSNRBot(RuneliteBot, metaclass=ABCMeta):

    def bank_at_home(self):
        pass

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

    def teleport_home(self):
        pass

    def toggle_auto_retaliate(self, toggle_on: bool):
        '''
        Toggles auto retaliate. Assumes client window is configured.
        Args:
            toggle_on: Whether to turn on or off.
        '''
        self.log_msg("Enabling auto retaliate...")
        # click the combat tab
        self.mouse.move_to(self.cp_combat, duration=1, variance=3)
        pag.click()
        time.sleep(0.5)

        # Search for the auto retaliate button (deselected)
        # If None, then auto retaliate is on.
        auto_retal_btn = self.search_img_in_rect(f"{self.BOT_IMAGES}/near_reality/cp_combat_autoretal.png", self.rect_inventory, conf=0.9)

        if toggle_on and auto_retal_btn is not None or not toggle_on and auto_retal_btn is None:
            self.mouse.move_to((644, 402), 0.2, variance=5)
            pag.click()
        elif toggle_on:
            print("Auto retaliate is already on.")
        else:
            print("Auto retaliate is already off.")

    def setup_osnr(self):
        '''
        Sets up the OSNR client.
        '''
        self.setup_client(window_title="Near-Reality", set_layout_fixed=True, logout_runelite=False, collapse_runelite_settings=True)
        self.__disable_private_chat()
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.cp_inventory)
        self.mouse.click()
        time.sleep(0.5)
