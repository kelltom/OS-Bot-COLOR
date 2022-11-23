from model.bot import BotStatus
from model.osnr.osnr_bot import OSNRBot
from typing import List
from utilities.APIs.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject, Rectangle
import pyautogui as pag
import random
import time

class OSNRMining(OSNRBot):
    def __init__(self):
        title = "Mining"
        description = ("This bot power-mines rocks. Equip a pickaxe, place your character between some rocks and mark " +
                       "(Shift + Right-Click) the ones you want to mine.")
        super().__init__(title=title, description=description)
        self.running_time = 2
        self.logout_on_friends = False

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 360)
        self.options_builder.add_dropdown_option("logout_on_friends", "Logout when friends are nearby?", ["Yes", "No"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
                self.log_msg(f"Running time: {self.running_time} minutes.")
            elif option == "logout_on_friends":
                if options[option] == "Yes":
                    self.logout_on_friends = True
                    self.log_msg("Bot will not logout when friends are nearby.")
                else:
                    self.logout_on_friends = False
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False
                self.log_msg("Failed to set options.")
                return
        self.options_set = True
        self.log_msg("Options set successfully.")

    def main_loop(self):  # sourcery skip: low-code-quality
        # Setup
        api = StatusSocket()
        self.setup_osnr(zoom_percentage=70)

        if not self.status_check_passed():
            return

        # Set compass
        self.mouse.move_to(self.win.orb_compass())
        self.mouse.click()
        time.sleep(0.5)

        # Move camera up
        pag.keyDown('up')
        time.sleep(2)
        pag.keyUp('up')
        time.sleep(0.5)

        mined = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if not self.status_check_passed():
                return

            # Check to drop inventory
            if api.get_is_inv_full():
                self.drop_inventory()
                time.sleep(1)
                continue

            if not self.status_check_passed():
                return

            # Check to logout
            if self.logout_on_friends and self.friends_nearby():
                self.__logout("Friends nearby. Logging out.")
                return

            # Get the rocks
            rocks: List[RuneLiteObject] = self.get_all_tagged_in_rect(self.win.rect_game_view, self.PINK)
            if rocks is None:
                failed_searches += 1
                if failed_searches > 5:
                    self.__logout("Failed to find a rock to mine. Logging out.")
                    self.set_status(BotStatus.STOPPED)
                    return
                time.sleep(1)
                continue

            # Whack the rock
            failed_searches = 0
            self.log_msg("Clicking a rock...")
            self.mouse.move_to(rocks[0].random_point(), rect=Rectangle(0, 0, 0, 0), mouseSpeed="fastest")
            self.mouse.click()

            while not api.get_is_player_idle():
                if not self.status_check_passed():
                    return

            mined += 1
            self.log_msg(f"Rocks mined: {mined}")

            if not self.status_check_passed():
                return

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg: str):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)
