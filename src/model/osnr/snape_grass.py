'''
Thieving bot for OSNR. Thieves from NPCs.
'''
from itertools import chain
from model.bot import BotStatus, Point
from model.osnr.osnr_bot import OSNRBot
import pyautogui as pag
import time


class OSNRSnapeGrass(OSNRBot):
    def __init__(self):
        title = "Snape Grass Looter"
        description = ("This bot picks up spawning snape grass in Near Reality and banks it. Before starting the bot, " +
                       "clear your inventory and ensure snape grass is highlighted in the Ground Items plugin. Click play " +
                       "from anywhere to start.")
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
                elif options[option] == "Ancients":
                    self.spellbook = self.Spellbook.ancient
                self.log_msg(f"Spellbook: {self.spellbook}.")
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False
                self.log_msg("Failed to set options.")
                return
        self.options_set = True
        self.log_msg("Options set successfully.")

    def main_loop(self):  # sourcery skip: low-code-quality, use-named-expression
        # Setup
        self.setup_osnr()

        # Config camera
        self.log_msg("Setting compass...")
        self.mouse.move_to(self.orb_compass)
        self.mouse.click()
        time.sleep(0.3)

        # Anchors/counters
        last_inventory_pos = self.inventory_slots[6][3]  # TODO: or [-1][-1]?
        last_inventory_rgb = pag.pixel(last_inventory_pos.x, last_inventory_pos.y)
        total = 0

        # Flatten inventory into 1D list
        inventory = list(chain.from_iterable(self.inventory_slots))

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if not self.status_check_passed():
                return

            # Config camera
            self.log_msg("Setting compass...")
            self.mouse.move_to(self.orb_compass)
            self.mouse.click()
            time.sleep(0.3)

            # Bank and empty inventory
            self.log_msg("Depositing inventory...")
            self.teleport_and_bank()
            time.sleep(2)
            self.mouse.move_to(self.cp_inventory)
            pag.click()
            empty = self.search_img_in_rect(f"{self.BOT_IMAGES}/bank_deposit_all.png", self.rect_game_view)
            if empty is None:
                self.log_msg("Failed to deposit inventory.")
                self.set_status(BotStatus.STOPPED)
                return
            self.mouse.move_to(empty)
            pag.click()
            time.sleep(1)
            self.mouse.move_to(Point(489, 48))  # close bank interface
            pag.click()
            time.sleep(0.5)

            # Travel to waterbirth island
            self.log_msg("Traveling to waterbirth island...")
            self.teleport_to(self.spellbook, "Waterbirth Island")
            time.sleep(4)
            self.mouse.move_to(self.cp_inventory)
            pag.click()

            # Travel to the spot where the snape grass is
            self.mouse.move_to(Point(640, 40))
            pag.click()
            time.sleep(5)
            self.mouse.move_to(Point(707, 82))
            pag.click()
            time.sleep(10)
            self.mouse.move_to(Point(682, 152))
            time.sleep(5)

            # Move camera up
            self.log_msg("Moving camera up...")
            pag.keyDown("up")
            time.sleep(2)
            pag.keyUp("up")

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

            # While inv is not full, pick up snape grass
            i = 0
            timeout = 0
            while pag.pixel(last_inventory_pos.x, last_inventory_pos.y) == last_inventory_rgb:
                points = self.get_all_tagged_in_rect(rect=self.rect_game_view, color=self.TAG_PURPLE)
                if len(points) == 0:
                    self.log_msg("No snape grass found.")
                    time.sleep(2)
                    timeout += 2
                    if timeout > 20:
                        self.log_msg("Failed to find snape grass.")
                        self.logout()
                        self.set_status(BotStatus.STOPPED)
                        return
                    continue
                empty_slot_rgb = pag.pixel(inventory[i].x, inventory[i].y)
                self.mouse.move_to(points[0])
                pag.click()
                did_pickup = True
                while pag.pixel(inventory[i].x, inventory[i].y) == empty_slot_rgb:
                    time.sleep(2)
                    timeout += 2
                    if timeout > 15:
                        self.log_msg("Misclicked snape grass. Trying again...")
                        did_pickup = False
                        break
                if did_pickup:
                    total += 1
                    i += 1
                    self.log_msg(f"Picked up snape grass. Total: {total}")

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.set_status(BotStatus.STOPPED)
