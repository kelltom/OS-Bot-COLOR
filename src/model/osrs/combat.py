import time

import utilities.api.item_ids as item_ids
import utilities.color as clr
from model.runelite_bot import BotStatus, RuneLiteBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSCombat(RuneLiteBot):
    def __init__(self):
        title = "Combat"
        description = (
            "This bot kills NPCs. Position your character near some NPCs and tag them. If you want the bot to pick up "
            + "loot, add the item name to the highlight list in the Ground Items plugin (one day this will be done automatically)."
        )
        super().__init__(title=title, description=description)
        self.running_time = 1
        self.loot_items = []
        self.hp_threshold = 0

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_text_edit_option("loot_items", "Loot items (comma separated):", "E.g., Coins, Dragon bones")
        self.options_builder.add_slider_option("hp_threshold", "Low HP threshold (0-100)?", 0, 100)

    def save_options(self, options: dict):
        self.options_set = True
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "loot_items":
                self.loot_items = options[option]
            elif option == "hp_threshold":
                self.hp_threshold = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False
                self.log_msg("Failed to set options.")
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Loot items: {self.loot_items}.")
        self.log_msg(f"Bot will eat when HP is below: {self.hp_threshold}.")
        self.log_msg("Options set successfully.")

    def main_loop(self):
        # Setup API
        api_morg = MorgHTTPSocket()
        api_status = StatusSocket()

        self.toggle_auto_retaliate(True)

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if not self.status_check_passed():
                return

            # If inventory is full...
            if api_status.get_is_inv_full():
                self.__logout("Inventory full. Logging out...")
                return

            # While not in combat
            while not api_morg.get_is_in_combat():
                if not self.status_check_passed():
                    return

                # Find a target
                target = self.get_nearest_tagged_NPC()
                if target is None:
                    failed_searches += 1
                    if failed_searches % 10 == 0:
                        self.log_msg("Searching for targets...")
                    if failed_searches > 60:
                        # If we've been searching for a whole minute...
                        self.__logout("No tagged targets found. Logging out.")
                        return
                    time.sleep(1)
                    continue
                failed_searches = 0

                # Click target if mouse is actually hovering over it, else recalculate
                self.mouse.move_to(target.random_point())
                if not self.mouseover_text(contains="Attack", color=clr.OFF_WHITE):
                    continue
                self.mouse.click()
                time.sleep(1)

            # While in combat
            while api_morg.get_is_in_combat():
                # Check to eat food
                if self.get_hp() < self.hp_threshold:
                    self.__eat(api_status)
                if not self.status_check_passed():
                    return
                time.sleep(1)

            # Loot all highlighted items on the ground
            if self.loot_items:
                self.__loot(api_status)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __eat(self, api: StatusSocket):
        self.log_msg("HP is low.")
        food_slots = api.get_inv_item_indices(item_ids.all_food)
        if len(food_slots) == 0:
            self.log_msg("No food found. Pls tell me what to do...")
            self.set_status(BotStatus.STOPPED)
            return
        self.log_msg("Eating food...")
        self.mouse.move_to(self.win.inventory_slots[food_slots[0]].random_point())
        self.mouse.click()

    def __loot(self, api: StatusSocket):
        """Picks up loot while there is loot on the ground"""
        while self.pick_up_loot(self.loot_items):
            if api.get_is_inv_full():
                self.__logout("Inventory full. Cannot loot.")
                return
            curr_inv = len(api.get_inv())
            self.log_msg("Picking up loot...")
            for _ in range(5):  # give the bot 5 seconds to pick up the loot
                if len(api.get_inv()) != curr_inv:
                    self.log_msg("Loot picked up.")
                    time.sleep(1)
                    break
                if not self.status_check_passed():
                    return
                time.sleep(1)

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)
