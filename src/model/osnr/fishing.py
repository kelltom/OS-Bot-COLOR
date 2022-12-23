import time

import pyautogui as pag

import utilities.color as clr
from model.bot import BotStatus
from model.osnr.osnr_bot import OSNRBot
from utilities.api.status_socket import StatusSocket
from utilities.geometry import Point, RuneLiteObject


class OSNRFishing(OSNRBot):
    def __init__(self):
        title = "Fishing"
        description = "This bot fishes... fish. Take out a rod and bait, position your character " + "near a tagged fishing spot, and press play."
        super().__init__(bot_title=title, description=description)
        self.running_time = 2
        self.protect_slots = 2

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_slider_option("protect_slots", "When dropping, protect first x slots:", 0, 4)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "protect_slots":
                self.protect_slots = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Bot will run for {self.running_time} minutes.")
        self.log_msg(f"Protecting first {self.protect_slots} slots when dropping inventory.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):  # sourcery skip: low-code-quality, use-named-expression
        # API setup
        api = StatusSocket()

        # Client setup
        self.set_camera_zoom(50)

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        time.sleep(0.5)
        self.disable_private_chat()
        time.sleep(0.5)

        # Set compass
        self.set_compass_north()
        self.move_camera_up()

        fished = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # Check to drop inventory
            if api.get_is_inv_full():
                self.drop_inventory(skip_slots=list(range(self.protect_slots)))
                fished += 28 - self.protect_slots
                self.log_msg(f"Fishes fished: ~{fished}")
                time.sleep(2)

            # If not fishing, click fishing spot
            while not self.is_player_doing_action("Fishing"):
                spot = self.get_nearest_tag(clr.CYAN)
                if spot is None:
                    failed_searches += 1
                    time.sleep(2)
                    if failed_searches > 10:
                        self.log_msg("Failed to find fishing spot.")
                        self.set_status(BotStatus.STOPPED)
                        return
                else:
                    self.log_msg("Clicking fishing spot...")
                    self.mouse.move_to(spot.random_point())
                    pag.click()
                    time.sleep(1)
                    break
            time.sleep(3)

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.set_status(BotStatus.STOPPED)
