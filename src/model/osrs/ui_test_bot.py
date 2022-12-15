"""
This script is used to ensure that the Window properties are being set correctly.
"""
import time
from typing import List

from model.runelite_bot import BotStatus, RuneLiteBot, RuneLiteWindow
from utilities.geometry import Rectangle


class TestBot(RuneLiteBot):
    def __init__(self):
        title = "Test Bot"
        description = "This bot is for testing the new Window feature. Open an instance of RuneLite to see how the " + "mouse travels to the UI elements."
        super().__init__(
            title=title,
            description=description,
            window=RuneLiteWindow(window_title="RuneLite"),
        )

    def create_options(self):
        pass

    def save_options(self, options: dict):
        self.options_set = True
        self.log_msg("Options set successfully.")

    def main_loop(
        self,
    ):  # sourcery skip: merge-list-append, merge-list-appends-into-extend, merge-list-extend, unwrap-iterable-construction
        """The first thing that happens when the Play button is pressed is the client window
        is scanned and initialized. Then, all of the window properties are available.
        The program will let you know if the initialization failed.

        If you need to move the client for any reason, pause the bot first, then it will re-initialize
        once your resume. That won't work in this script though, since we are hardcoding the positions
        into the list before the loop. It is best practice to only use the window properties within
        your bot loop."""

        # Here, we'll define some points on screen that we'll move the mouse to.
        spots: List[tuple] = []
        spots.append(("Moving to chatbox...", self.win.chat))
        spots.append(("Moving to control panel...", self.win.control_panel))
        spots.append(("Moving to minimaparea...", self.win.minimap_area))
        spots.append(("Moving to game view...", self.win.game_view))
        spots.append(("Moving to minimap...", self.win.minimap))
        spots.append(("Moving to hp orb text...", self.win.hp_orb_text))
        spots.append(("Moving to prayer orb text...", self.win.prayer_orb_text))
        spots.append(("Moving to quick pray orb...", self.win.prayer_orb))
        spots.append(("Moving to run orb...", self.win.run_orb))
        spots.append(("Moving to spec orb...", self.win.spec_orb))
        spots.append(("Moving to compass...", self.win.compass_orb))
        spots.append(("Moving to control panel tabs...", self.win.cp_tabs))
        spots.append(("Moving to inv slots...", self.win.inventory_slots))
        spots.append(("Moving to chat tabs...", self.win.chat_tabs))

        for spot_count, spot in enumerate(spots, start=1):
            self.log_msg(spot[0])
            if isinstance(spot[1], Rectangle):
                self.mouse.move_to(spot[1].get_center())
            else:
                for rect in spot[1]:
                    self.mouse.move_to(rect.random_point(), mouseSpeed="fastest")
                    if not self.status_check_passed():
                        return
            time.sleep(0.2)

            if not self.status_check_passed():
                return

            self.update_progress(spot_count / len(spots))

        # If the bot reaches here it has completed its running time.
        self.update_progress(1)
        self.log_msg("Bot has completed all of its iterations.")
        self.set_status(BotStatus.STOPPED)
