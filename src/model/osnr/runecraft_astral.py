'''
Trains Runecrafting via Astral Runes.
'''
import utilities.bot_cv as bcv
from model.bot import BotStatus
from model.osnr.osnr_bot import OSNRBot
import pyautogui as pag
from utilities.bot_cv import Point
import time


class OSNRAstralRunes(OSNRBot):
    def __init__(self):
        title = "Runecraft: Astral Runes"
        description = ("This bot runs Astral Runes to train Runecrafting. Create a preset full of Rune Essence and set it as the " +
                       "default preset. Then, run this bot from anywhere.")
        super().__init__(title=title, description=description)
        self.running_time = 0
        self.spellbook: self.Spellbook = None

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("spellbook", "Spellbook", ["Standard", "Ancients"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
                self.log_msg(f"Running time: {self.running_time} minutes.")
            elif option == "spellbook":
                if options[option] == "Standard":
                    self.spellbook = self.Spellbook.standard
                    self.log_msg("Spellbook: Standard.")
                elif options[option] == "Ancients":
                    self.spellbook = self.Spellbook.ancient
                    self.log_msg("Spellbook: Ancients.")
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

        last_inventory_pos = self.inventory_slots[6][3]
        last_inventory_rgb = None

        runes_crafted = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if not self.status_check_passed():
                return

            # Bank and empty inventory
            if not self.teleport_and_bank(spellbook=self.spellbook):
                self.set_status(BotStatus.STOPPED)
                return
            time.sleep(1)
            empty = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/bank_deposit_all.png", self.rect_game_view)
            if empty is None:
                self.log_msg("Failed to deposit inventory.")
                self.set_status(BotStatus.STOPPED)
                return
            self.mouse.move_to(empty)
            pag.click()
            time.sleep(1)

            if not self.status_check_passed():
                return

            # Set last inv slot pixel color if it's not set
            if last_inventory_rgb is None:
                last_inventory_rgb = pag.pixel(last_inventory_pos.x, last_inventory_pos.y)

            # Restock inventory
            self.load_preset()
            time.sleep(1)
            self.mouse.move_to(self.cp_inventory)
            pag.click()
            time.sleep(0.5)

            if not self.status_check_passed():
                return

            # -- If last inventory slot is empty, terminate bot
            if pag.pixel(last_inventory_pos.x, last_inventory_pos.y) == last_inventory_rgb:
                self.log_msg("Out of rune essence. Terminating bot.")
                self.set_status(BotStatus.STOPPED)
                return

            # Teleport to Astral altar
            if not self.teleport_to(spellbook=self.spellbook, location="Astral Altar"):
                self.set_status(BotStatus.STOPPED)
                return
            time.sleep(4)

            if not self.status_check_passed():
                return

            # Move closer to altar
            self.mouse.move_to(Point(667, 125))
            pag.click()
            time.sleep(3)

            if not self.status_check_passed():
                return

            # Click the altar
            points = self.get_all_tagged_in_rect(self.rect_game_view, self.TAG_PINK)
            if len(points) == 0:
                self.log_msg("Failed to find altar.")
                self.set_status(BotStatus.STOPPED)
                return
            self.mouse.move_to(points[0])
            pag.click()

            runes_crafted += 28
            self.log_msg(f"Runes crafted: {runes_crafted}")
            time.sleep(2)

            if not self.status_check_passed():
                return

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.set_status(BotStatus.STOPPED)
