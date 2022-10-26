'''
The AloraBot class contains properties and functions that are specific to the Alora client. This class should
be inherited by Alora script classes.
'''
from abc import ABCMeta
import utilities.bot_cv as bcv
from model.runelite_bot import RuneLiteBot
from model.bot import BotStatus
import pyautogui as pag
import time


class AloraBot(RuneLiteBot, metaclass=ABCMeta):

    def toggle_auto_retaliate(self, toggle_on: bool):
        '''
        Toggles auto retaliate. Assumes client window is configured.
        Args:
            toggle_on: Whether to turn on or off.
        '''
        self.log_msg("Enabling auto retaliate...")
        # click the combat tab
        self.mouse.move_to(self.rl.cp_tab(1), duration=1, destination_variance=3)
        pag.click()
        time.sleep(0.5)

        # Search for the auto retaliate button (deselected)
        # If None, then auto retaliate is on.
        auto_retal_btn = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/alora/cp_combat_autoretal.png", self.rl.rect_inventory(), precision=0.9)

        if toggle_on and auto_retal_btn is not None or not toggle_on and auto_retal_btn is None:
            self.mouse.move_to(self.rl.get_relative_point(644, 402), destination_variance=5, targetPoints=50)
            pag.click()
        elif toggle_on:
            print("Auto retaliate is already on.")
        else:
            print("Auto retaliate is already off.")

    def teleport_home(self):
        pass

    def bank_at_home(self):
        pass

    def did_set_layout_fixed(self):
        '''
        Attempts to set the client's layout to "Fixed - Classic layout".
        Returns:
            True if the layout was set, False if an issue occured.
        '''
        self.log_msg("Setting layout to Fixed - Classic layout.")
        time.sleep(0.3)
        cp_settings_selected = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/cp_settings_selected.png",
                                                      self.rl.rectangle(),
                                                      precision=0.95)
        cp_settings = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/cp_settings.png",
                                             self.rl.rectangle(),
                                             precision=0.95)
        if cp_settings_selected is None and cp_settings is None:
            self.log_msg("Could not find settings button.")
            return False
        elif cp_settings is not None and cp_settings_selected is None:
            self.mouse.move_to(cp_settings)
            pag.click()
        time.sleep(0.5)
        self.mouse.move_rel(-99, -257)
        pag.click()
        time.sleep(0.5)
        self.mouse.move_rel(36, 123)
        pag.click()
        time.sleep(1.5)
        click_here_to_play = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/alora/click_here_to_play.png",
                                                    self.rl.rectangle())
        if click_here_to_play is not None:
            self.mouse.move_to(click_here_to_play)
            pag.click()
            time.sleep(1.5)
        return True

    def setup_alora(self):  # sourcery skip: merge-nested-ifs
        '''
        Sets up the Alora client.
        '''
        # Not letting RuneLiteBot.setup() touch layout since we have a custom function for it.
        self.setup_client(window_title="Alora", set_layout_fixed=False, logout_runelite=True)
        if not self.did_set_layout_fixed():
            if pag.confirm("Could not set layout to Fixed - Classic layout. Continue anyway?") == "Cancel":
                self.set_status(BotStatus.STOPPED)
                return
