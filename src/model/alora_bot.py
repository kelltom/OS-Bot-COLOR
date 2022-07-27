'''
The AloraBot class contains properties and functions that are specific to the Alora client. This class should
be inherited by Alora script classes.
'''
from abc import ABCMeta
from model.runelite_bot import RuneliteBot
from model.bot import Rectangle, Point
import time


class AloraBot(RuneliteBot, metaclass=ABCMeta):

    # ------- Rects of Interest -------
    rect_current_action = Rectangle(Point(10, 52), Point(171, 93))  # combat/skilling plugin text
    rect_game_view = Rectangle(Point(9, 31), Point(517, 362))  # gameplay area
    rect_hp = Rectangle(Point(526, 80), Point(552, 100))  # contains HP text value
    rect_inventory = Rectangle(Point(554, 230), Point(737, 491))  # inventory area
    # TODO: Add more rectangles of interest (prayer, spec, etc.)

    # ------- Points of Interest -------
    # --- Orbs ---
    orb_compass = Point(x=571, y=48)
    orb_prayer = Point(x=565, y=119)
    orb_spec = Point(x=597, y=178)

    # --- Control Panel (CP) ---
    h1 = 213  # y-axis pixels to top of cp
    h2 = 510  # y-axis pixels to bottom of cp
    cp_combat = Point(x=545, y=h1)
    cp_inventory = Point(x=646, y=h1)
    cp_equipment = Point(x=678, y=h1)
    cp_prayer = Point(x=713, y=h1)
    cp_spellbook = Point(x=744, y=h1)
    cp_logout = Point(x=646, y=h2)
    cp_settings = Point(x=680, y=h2)

    def is_in_combat(self) -> bool:
        '''
        Returns whether the player is in combat. This is achieved by checking if text exists in the Runelite activity
        section in the game view.
        '''
        result = self.get_text_in_rect(self.rect_current_action)
        return result.strip() != ""

    def toggle_auto_retaliate(self, toggle_on: bool):
        '''
        Toggles auto retaliate. Assumes client window is configured.
        Args:
            toggle_on: Whether to turn on or off.
        '''
        # click the combat tab
        self.hc.move(self.cp_combat, duration=1)
        self.hc.click()
        time.sleep(0.5)

        # Search for the auto retaliate button (deselected)
        # If None, then auto retaliate is on.
        auto_retal_btn = self.search_img_in_rect(f"{self.BOT_IMAGES}/alora/cp_combat_autoretal.png", self.rect_inventory, conf=0.9)

        if toggle_on and auto_retal_btn is not None or not toggle_on and auto_retal_btn is None:
            self.hc.move((644, 402), 0.2)
            self.hc.click()
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
        self.setup_client(window_title="Alora")
