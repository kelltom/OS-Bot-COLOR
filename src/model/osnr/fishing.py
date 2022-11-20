from model.bot import BotStatus
from model.osnr.osnr_bot import OSNRBot
from utilities.APIs.status_socket import StatusSocket
from utilities.geometry import Point, Shape
import pyautogui as pag
import time
import utilities.bot_cv as bcv


class OSNRFishing(OSNRBot):
    def __init__(self):
        title = "Fishing"
        description = ("This bot fishes... fish. Take out a rod and bait, position your character " +
                       "near a fishing spot, and press play. Make sure the rest of your inventory is empty.")
        super().__init__(title=title, description=description)
        self.running_time = 0
        self.fish_type = None

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("fish_type", "What fish to catch?", ["Anglerfish", "Trout/Salmon"])

    def save_options(self, options: dict):
        self.options_set = True
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "fish_type":
                if options[option] == "Anglerfish":
                    self.fish_type = "anglerfish"
                elif options[option] == "Trout/Salmon":
                    self.fish_type = "salmon"
                else:
                    self.log_msg(f"Unknown fish type: {options[option]}")
                    self.options_set = False
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False
        if not self.options_set:
            self.log_msg("Failed to set options.")
            return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Fish type: {self.fish_type}.")
        self.log_msg("Options set successfully.")

    def main_loop(self):  # sourcery skip: low-code-quality, use-named-expression
        # Setup
        api = StatusSocket()
        self.setup_osnr(zoom_percentage=50)

        # Set compass
        self.mouse.move_to(self.win.orb_compass())
        self.mouse.click()
        time.sleep(0.5)

        self.move_camera_up()

        fished = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if not self.status_check_passed():
                return

            # Check to drop inventory
            if api.get_is_inv_full():
                self.drop_inventory(skip_rows=1)
                fished += 25
                self.log_msg(f"Fishes fished: ~{fished}")
                time.sleep(2)

            if not self.status_check_passed():
                return

            # If not fishing, click fishing spot
            # TODO: this has to be removed and replaced with a API info
            while not self.is_player_doing_action("fishing"):
                im_path = None
                if self.fish_type == "anglerfish":
                    im_path = f"{bcv.BOT_IMAGES}/near_reality/anglerfish_sprite.png"
                elif self.fish_type == "salmon":
                    im_path = f"{bcv.BOT_IMAGES}/near_reality/salmon_sprite.png"
                spot = bcv.search_img_in_rect(im_path, self.win.rect_game_view())
                if spot is None:
                    failed_searches += 1
                    time.sleep(1)
                    if failed_searches > 10:
                        self.log_msg("Failed to find fishing spot.")
                        self.set_status(BotStatus.STOPPED)
                        return
                else:
                    self.mouse.move_to(spot)
                    pag.click()
                    break
            time.sleep(3)
            if not self.status_check_passed():
                return
            time.sleep(3)
            if not self.status_check_passed():
                return

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.set_status(BotStatus.STOPPED)
