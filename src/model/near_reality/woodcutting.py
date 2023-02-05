import time

import utilities.color as clr
from model.bot import BotStatus
from model.near_reality.nr_bot import NRBot
from utilities.api.status_socket import StatusSocket


class OSNRWoodcutting(NRBot):
    def __init__(self):
        title = "Woodcutting"
        description = "This bot chops wood. Position your character near some trees, tag them, and press the play button."
        super().__init__(bot_title=title, description=description)
        self.running_time = 1
        self.protect_slots = 0
        self.logout_on_friends = True

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_slider_option("protect_slots", "When dropping, protect first x slots:", 0, 4)
        self.options_builder.add_dropdown_option("logout_on_friends", "Logout when friends are nearby?", ["Yes", "No"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "protect_slots":
                self.protect_slots = options[option]
            elif option == "logout_on_friends":
                self.logout_on_friends = options[option] == "Yes"
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Protect slots: {self.protect_slots}.")
        self.log_msg("Bot will not logout when friends are nearby.")
        self.options_set = True

    def main_loop(self):  # sourcery skip: low-code-quality
        # Setup API
        api = StatusSocket()

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        logs = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # If inventory is full
            if api.get_is_inv_full():
                self.drop_all(skip_slots=list(range(self.protect_slots)))
                logs += 28 - self.protect_slots
                self.log_msg(f"Logs cut: ~{logs}")
                time.sleep(1)
                continue

            # Check to logout
            if self.logout_on_friends and self.friends_nearby():
                self.__logout("Friends nearby. Logging out.")

            # Find a tree
            tree = self.get_nearest_tag(clr.PINK)
            if tree is None:
                failed_searches += 1
                if failed_searches > 10:
                    self.__logout("No tagged trees found. Logging out.")
                time.sleep(1)
                continue

            # Click tree and wait to start cutting
            self.mouse.move_to(tree.random_point())
            self.mouse.click()
            time.sleep(5)

            # Wait so long as the player is cutting
            # -Could alternatively check the API for the player's idle status-
            timer = 0
            while self.is_player_doing_action("Woodcutting"):
                self.update_progress((time.time() - start_time) / end_time)
                if timer % 6 == 0:
                    self.log_msg("Chopping tree...")
                time.sleep(2)
                timer += 2
            self.log_msg("Idle...")

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()
