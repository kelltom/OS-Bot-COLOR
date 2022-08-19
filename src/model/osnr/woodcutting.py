'''
Trains Runecrafting via Astral Runes.
'''
from model.bot import BotStatus
from model.osnr.osnr_bot import OSNRBot
import pyautogui as pag
import time
import utilities.bot_cv as bcv


class OSNRWoodcutting(OSNRBot):
    def __init__(self):
        title = "Woodcutting"
        description = ("This bot chops wood. Position your character near some trees, tag them, equip your axe, and press the play button.")
        super().__init__(title=title, description=description)
        self.running_time = 0

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("should_bank", "Bank logs?", ["Yes", "No"])
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
            elif option == "should_bank":
                if options[option] == "Yes":
                    self.should_bank = True
                    self.log_msg("Bot will bank logs.")
                else:
                    self.should_bank = False
                    self.log_msg("Bot will not bank logs.")
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False
                self.log_msg("Failed to set options.")
                return
        self.options_set = True
        self.log_msg("Options set successfully.")

    def main_loop(self):  # sourcery skip: low-code-quality
        # Setup
        self.setup_osnr(zoom_percentage=30)

        if not self.status_check_passed():
            return

        # Set compass
        self.mouse.move_to(self.orb_compass)
        self.mouse.click()
        time.sleep(0.5)

        # Move camera up
        self.move_camera_up()

        last_inventory_pos = self.inventory_slots[6][3]
        last_inventory_rgb = pag.pixel(last_inventory_pos.x, last_inventory_pos.y)
        logs = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if not self.status_check_passed():
                return

            # If inventory is full
            if pag.pixel(last_inventory_pos.x, last_inventory_pos.y) != last_inventory_rgb:
                logs += 28
                self.log_msg(f"Logs cut: ~{logs}")
                if self.should_bank:
                    # TODO: THIS ONLY WORKS FOR ::DI AND IS A TEMPORARY SOLUTION
                    bank = self.get_nearest_tag(self.TAG_BLUE)
                    if bank is None:
                        self.log_msg("Could not find bank.")
                        self.set_status(BotStatus.STOPPED)
                        return
                    self.mouse.move_to(bank)
                    self.mouse.click()
                    time.sleep(3)
                    if not self.deposit_inventory():
                        self.set_status(BotStatus.STOPPED)
                        return
                    self.close_bank()
                else:
                    self.drop_inventory()
                    time.sleep(1)
                continue

            if not self.status_check_passed():
                return

            # Check to logout
            if self.logout_on_friends and self.friends_nearby():
                self.log_msg("Friends nearby. Logging out.")
                self.logout()
                self.set_status(BotStatus.STOPPED)
                return

            # Find a tree
            tree = self.get_nearest_tag(self.TAG_PINK)
            if tree is None:
                failed_searches += 1
                if failed_searches > 10:
                    self.log_msg("No tagged trees found. Logging out.")
                    self.logout()
                    self.set_status(BotStatus.STOPPED)
                    return
                time.sleep(1)
                continue

            # Click tree and wait to start cutting
            self.mouse.move_to(tree)
            self.mouse.click()
            time.sleep(3)

            # Wait so long as the player is cutting
            timer = 0
            while bcv.search_text_in_rect(self.rect_game_view, ["Woodcutting"], ["Not"]):
                self.update_progress((time.time() - start_time) / end_time)
                if not self.status_check_passed():
                    return
                if timer % 5 == 0:
                    self.log_msg("Chopping tree...")
                time.sleep(2)
                timer += 2
            self.log_msg("Idle...")

            if not self.status_check_passed():
                return

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.set_status(BotStatus.STOPPED)
