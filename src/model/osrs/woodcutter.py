'''
This file demonstrates how to set up a simple bot. It demonstrates how to implement the functions for
capturing user configuration of the bot, and includes a simulated bot loop that does not have any
side affects during testing.

To better understand how to implement a bot, please see the documentation for the Bot class as well as
the README/Wiki.
'''

from model.runelite_bot import RuneLiteBot
from model.bot import BotStatus
import pyautogui as pag
import time


class OSRSWoodcutter(RuneLiteBot):
    def __init__(self):
        title = "Woodcutter"
        description = ("This bot will chop tagged trees until the inventory is full, then drop the logs.")
        super().__init__(title=title, description=description)
        self.running_time = 0
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

    def main_loop(self):
        # --- CLIENT SETUP ---
        self.setup_client(window_title="RuneLite",
                          set_layout_fixed=True,
                          logout_runelite=True,
                          collapse_runelite_settings=True)
        
        self.mouse.move_to(self.cp_inventory)
        self.mouse.click()

        # --- RUNTIME PROPERTIES ---
        self.logs_cut = 0
        last_inv_slot = self.inventory_slots[-1][-1]
        last_slot_color_empty = pag.pixel(last_inv_slot.x, last_inv_slot.y)

        # --- MAIN LOOP ---
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            if not self.status_check_passed():
                return

            # 1. If inventory is full, drop inventory. Increment logs_cut counter by 28.
            if pag.pixel(last_inv_slot.x, last_inv_slot.y) != last_slot_color_empty:
                self.drop_inventory()
                time.sleep(1)
            
            self.update_progress((time.time() - start_time) / end_time)

            if not self.status_check_passed():
                return

            # 2. Locate the nearest tagged tree.
            tree = self.get_nearest_tag(self.TAG_PINK)
            if tree is None:
                time.sleep(1)
                continue

            # 3. Click the tree.
            self.mouse.move_to(point=tree,
                               duration=0.3,
                               destination_variance=3,
                               time_variance=0.001,
                               tween='rand')
            self.mouse.click()
            time.sleep(3)

            if not self.status_check_passed():
                return

            # 4. While the player is chopping the tree, wait.
            timer = 0
            while self.is_player_doing_action(action="Woodcutting"):
                if not self.status_check_passed():
                    return
                self.update_progress((time.time() - start_time) / end_time)
                if timer % 5 == 0:  # every 5 seconds, let UI know we are still chopping
                    self.log_msg("Chopping tree...")
                time.sleep(2)  # wait 2 seconds
                timer += 2  # increment timer by 2 seconds
            self.log_msg("Idle...")

            # 5. Return to start of the loop.
        
        # If the bot reaches here it has completed its running time.
        self.update_progress(1)
        self.log_msg("Bot has completed all of its iterations.")
        self.set_status(BotStatus.STOPPED)
