import time
from typing import List

import utilities.color as clr
from model.bot import BotStatus
from model.near_reality.nr_bot import NRBot
from utilities.api.status_socket import StatusSocket
from utilities.geometry import Rectangle, RuneLiteObject


class NRMining(NRBot):
    def __init__(self):
        title = "Mining"
        description = (
            "This bot power-mines rocks. Equip a pickaxe, place your character between some rocks and mark "
            + "(Shift + Right-Click) the ones you want to mine."
        )
        super().__init__(bot_title=title, description=description)
        self.running_time = 2
        self.logout_on_friends = False

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 360)
        self.options_builder.add_dropdown_option("logout_on_friends", "Logout when friends are nearby?", ["Yes", "No"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "logout_on_friends":
                self.logout_on_friends = options[option] == "Yes"
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f'Bot will {"" if self.logout_on_friends else "not"} logout when friends are nearby.')
        self.options_set = True

    def main_loop(self):  # sourcery skip: low-code-quality
        # Setup
        api = StatusSocket()

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        mined = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # Check to drop inventory
            if api.get_is_inv_full():
                self.drop_all()
                time.sleep(1)
                continue

            # Check to logout
            if self.logout_on_friends and self.friends_nearby():
                self.__logout("Friends nearby. Logging out.")

            # Get the rocks
            rocks: List[RuneLiteObject] = self.get_all_tagged_in_rect(self.win.game_view, clr.PINK)
            if not rocks:
                failed_searches += 1
                if failed_searches > 5:
                    self.__logout("Failed to find a rock to mine. Logging out.")
                time.sleep(1)
                continue

            # Whack the rock
            failed_searches = 0
            self.mouse.move_to(rocks[0].random_point(), mouseSpeed="fastest")
            self.mouse.click()

            while not api.get_is_player_idle():
                pass

            mined += 1
            self.log_msg(f"Rocks mined: {mined}")

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg: str):
        self.log_msg(msg)
        self.logout()
        self.stop()
