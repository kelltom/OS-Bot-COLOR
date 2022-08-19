'''
Trains Runecrafting via Astral Runes.
'''
from model.bot import BotStatus
from model.osnr.osnr_bot import OSNRBot
import pyautogui as pag
import time
import utilities.bot_cv as bcv


class OSNRFishing(OSNRBot):
    def __init__(self):
        title = "Fishing: Fly"
        description = ("This bot power-fishes trout/salmon. Take out a fly fishing rod and feathers, position your character " +
                       "near a fishing spot, and press play. Make sure the rest of your inventory is empty.")
        super().__init__(title=title, description=description)
        self.running_time = 0

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
                self.log_msg(f"Running time: {self.running_time} minutes.")
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False
                self.log_msg("Failed to set options.")
                return
        self.options_set = True
        self.log_msg("Options set successfully.")

    def main_loop(self):  # sourcery skip: low-code-quality, use-named-expression
        # Setup
        self.setup_osnr(zoom_percentage=25)

        # Set compass
        self.mouse.move_to(self.orb_compass)
        self.mouse.click()
        time.sleep(0.5)

        last_inventory_pos = self.inventory_slots[6][3]
        last_inventory_rgb = pag.pixel(last_inventory_pos.x, last_inventory_pos.y)
        fished = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if not self.status_check_passed():
                return

            # Check to drop inventory
            if pag.pixel(last_inventory_pos.x, last_inventory_pos.y) != last_inventory_rgb:
                self.drop_inventory(skip_rows=1)
                fished += 25
                self.log_msg(f"Fishes fished: ~{fished}")
                time.sleep(1)
                continue

            if not self.status_check_passed():
                return

            # If not fishing, click fishing spot
            is_fishing = bcv.search_text_in_rect(self.rect_current_action, ["fishing"], ["not"])
            if not is_fishing:
                spot = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/near_reality/salmon_sprite.png", self.rect_game_view)
                if spot is None:
                    failed_searches += 1
                    if failed_searches > 10:
                        self.log_msg("Failed to find fishing spot.")
                        self.set_status(BotStatus.STOPPED)
                        return
                else:
                    self.mouse.move_to(spot)
                    pag.click()
            time.sleep(5)

            if not self.status_check_passed():
                return

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.set_status(BotStatus.STOPPED)
