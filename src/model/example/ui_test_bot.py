"""
This script is used to ensure that the Window properties are being set correctly.
"""
import time
from typing import List

from model.bot import Bot, BotStatus
from model.runelite_bot import RuneLiteWindow
from utilities.geometry import Rectangle

import utilities.game_launcher as launcher


class TestBot(Bot, launcher.Launchable):
    def __init__(self):
        self.win: RuneLiteWindow = None
        game_title = "Example"
        bot_title = "Test Bot"
        description = "This bot is for testing the new Window feature. Log in to RuneLite and run this script to see how the mouse travels around the UI."
        super().__init__(
            game_title=game_title,
            bot_title=bot_title,
            description=description,
            window=RuneLiteWindow(window_title="RuneLite"),
        )

    def create_options(self):
        pass

    def save_options(self, options: dict):
        self.options_set = True
        self.log_msg("Options set successfully.")
        self.log_msg("Please launch the game via the control panel button above. If RuneLite is already running with the correct settings, ignore this.")
    
    def launch_game(self):
        self.game_title = "OSRS" # This is a hack to allow the correct RL settings to be loaded despite this bot belonging to the "Example" game.
        launcher.launch_runelite_with_settings(bot=self, settings_file=None)

    def main_loop(
        self,
    ):
        """The first thing that happens when the Play button is pressed is the client window
        is scanned and initialized. Then, all of the window properties are available.
        The program will let you know if the initialization failed."""

        # Here, we'll define some points on screen that we'll move the mouse to.
        spots: List[tuple] = [
            ("Moving to chatbox...", self.win.chat),
            ("Moving to control panel...", self.win.control_panel),
            ("Moving to minimaparea...", self.win.minimap_area),
            ("Moving to game view...", self.win.game_view),
            ("Moving to minimap...", self.win.minimap),
            ("Moving to hp orb text...", self.win.hp_orb_text),
            ("Moving to prayer orb text...", self.win.prayer_orb_text),
            ("Moving to quick pray orb...", self.win.prayer_orb),
            ("Moving to run orb...", self.win.run_orb),
            ("Moving to spec orb...", self.win.spec_orb),
            ("Moving to compass...", self.win.compass_orb),
            ("Moving to control panel tabs...", self.win.cp_tabs),
            ("Moving to inv slots...", self.win.inventory_slots),
            ("Moving to chat tabs...", self.win.chat_tabs),
        ]
        for spot_count, spot in enumerate(spots, start=1):
            self.log_msg(spot[0])
            if isinstance(spot[1], Rectangle):
                self.mouse.move_to(spot[1].get_center())
            else:
                for rect in spot[1]:
                    self.mouse.move_to(rect.random_point(), mouseSpeed="fastest")
            time.sleep(0.2)

            self.update_progress(spot_count / len(spots))

        # If the bot reaches here it has completed its running time.
        self.update_progress(1)
        self.log_msg("Bot has completed all of its iterations.")
        self.set_status(BotStatus.STOPPED)
