'''
This file demonstrates how to set up a simple bot. It demonstrates how to implement the functions for
capturing user configuration of the bot, and includes a simulated bot loop that does not have any
side affects during testing.

To better understand how to implement a bot, please see the documentation for the Bot class as well as
the README/Wiki.
'''
from model.runelite_bot import RuneLiteBot, BotStatus
from typing import List
from utilities.geometry import Rectangle
import time


class TestBot(RuneLiteBot):
    def __init__(self):
        title = "Test Bot"
        description = ("This bot is for testing the new Window feature.")
        super().__init__(title=title, description=description)
        self.running_time = 1
        self.multi_select_example = None
        self.menu_example = None

    def create_options(self):
        '''
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        '''
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 180)  # max 180 minutes
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])

    def save_options(self, options: dict):
        '''
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False. No need to set bot status.
        '''
        self.options_set = True
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
                self.log_msg(f"Bot will run for {self.running_time} minutes.")
            elif option == "multi_select_example":
                self.multi_select_example = options[option]
                self.log_msg(f"Multi-select example set to: {self.multi_select_example}")
            elif option == "menu_example":
                self.menu_example = options[option]
                self.log_msg(f"Menu example set to: {self.menu_example}")
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False

        if self.options_set:
            self.log_msg("Options set successfully.")
        else:
            self.log_msg("Failed to set options.")
            print("Developer: ensure option keys are correct, and that the option values are being accessed correctly.")

    def main_loop(self):  # sourcery skip: merge-list-append

        # First thing that happens when the play button is pressed is the client window
        # is scanned and initialized.

        # Let's move the mouse to important locations on the screen.

        spots: List[tuple] = []
        spots.append(("Moving to chatbox...", self.win.chat))
        spots.append(("Moving to control panel...", self.win.control_panel))
        spots.append(("Moving to game view...", self.win.game_view))

        for spot in spots:
            self.log_msg(spot[0])
            if isinstance(spot[1], Rectangle):
                self.mouse.move_to(spot[1].get_center())
            elif isinstance(spot[1], List[Rectangle]):
                for rect in spot[1]:
                    self.mouse.move_to(rect.get_center())
            else:
                self.log_msg("Unknown type in spot list.")
            time.sleep(1.5)

            # Check once more for status and keyboard interrupts
            if not self.status_check_passed():
                return

        # If the bot reaches here it has completed its running time.
        self.update_progress(1)
        self.log_msg("Bot has completed all of its iterations.")
        self.set_status(BotStatus.STOPPED)
