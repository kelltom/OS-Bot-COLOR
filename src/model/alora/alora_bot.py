'''
The AloraBot class contains properties and functions that are specific to the Alora client. This class should
be inherited by Alora script classes.
'''
from abc import ABCMeta
from model.runelite_bot import RuneliteBot
import pyautogui as pag
import time


class AloraBot(RuneliteBot, metaclass=ABCMeta):

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
        auto_retal_btn = self.search_img_in_rect(f"{self.BOT_IMAGES}/alora/cp_combat_autoretal.png", self.rect_inventory, conf=0.9)

        if toggle_on and auto_retal_btn is not None or not toggle_on and auto_retal_btn is None:
            self.mouse.move_to((644, 402), 0.2, variance=5)
            pag.click()
        elif toggle_on:
            print("Auto retaliate is already on.")
        else:
            print("Auto retaliate is already off.")

    def teleport_home(self):
        pass

    def bank_at_home(self):
        pass

    def setup_alora(self):
        '''
        Sets up the Alora client.
        '''
        self.setup_client(window_title="Alora", logout_runelite=True, close_runelite_settings=True)
