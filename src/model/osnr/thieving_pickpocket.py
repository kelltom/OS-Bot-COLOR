'''
Thieving bot for OSNR. Pickpockets from NPCs.
'''
from model.bot import BotStatus
from model.osnr.osnr_bot import OSNRBot
from typing import List
from utilities.api.status_socket import StatusSocket
from utilities.geometry import Point, RuneLiteObject
import pyautogui as pag
import pytweening
import time
import utilities.api.item_ids as item_ids
import utilities.color as clr
import utilities.imagesearch as imsearch

class OSNRThievingPickpocket(OSNRBot):
    def __init__(self):
        title = "Thieving: Pickpocket"
        description = ("This bot steals from NPCs in OSNR. Position your character near a tagged NPC you wish to steal from. " +
                       "Start bot with > 50% HP. If you risk attacking nearby NPCs via misclick, turn NPC attack options to 'hidden'.")
        super().__init__(title=title, description=description)
        self.running_time = 5
        self.logout_on_friends = False
        self.pickpocket_option = 1
        self.should_click_coin_pouch = True
        self.should_drop_inv = True
        self.protect_rows = 5
        self.coin_pouch_path = imsearch.BOT_IMAGES.joinpath('coin_pouch.png')

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 360)
        self.options_builder.add_dropdown_option("logout_on_friends", "Logout when friends are nearby?", ["Yes", "No"])
        self.options_builder.add_dropdown_option("pickpocket_option", "Where is the pickpocket option?", ["Left-click", "2nd option", "3rd option"])
        self.options_builder.add_dropdown_option("should_click_coin_pouch", "Does this NPC drop coin pouches?", ["Yes", "No"])
        self.options_builder.add_dropdown_option("should_drop_inv", "Drop inventory?", ["Yes", "No"])
        self.options_builder.add_slider_option("protect_rows", "If dropping, protect rows?", 0, 6)

    def save_options(self, options: dict):  # sourcery skip: low-code-quality
        for option, res in options.items():
            if option == "running_time":
                self.running_time = options[option]
                self.log_msg(f"Running time: {self.running_time} minutes.")
            elif option == "logout_on_friends":
                if res == "Yes":
                    self.logout_on_friends = True
                    self.log_msg("Bot will logout when friends are nearby.")
                else:
                    self.logout_on_friends = False
                    self.log_msg("Bot will not logout when friends are nearby.")
            elif option == "pickpocket_option":
                if res == "Left-click":
                    self.pickpocket_option = 0
                    self.log_msg("Left click pickpocket enabled.")
                elif res == "2nd option":
                    self.pickpocket_option = 1
                    self.log_msg("Right click pickpocket enabled - 2nd option.")
                elif res == "3rd option":
                    self.pickpocket_option = 2
                    self.log_msg("Right click pickpocket enabled - 3rd option.")
            elif option == "should_click_coin_pouch":
                if res == "Yes":
                    self.should_click_coin_pouch = True
                    self.log_msg("Coin pouch check enabled.")
                else:
                    self.should_click_coin_pouch = False
                    self.log_msg("Coin pouch check disabled.")
            elif option == "should_drop_inv":
                if res == "Yes":
                    self.should_drop_inv = True
                    self.log_msg("Dropping inventory enabled.")
                else:
                    self.should_drop_inv = False
                    self.log_msg("Dropping inventory disabled.")
            elif option == "protect_rows":
                self.protect_rows = options[option]
                self.log_msg(f"Protecting first {self.protect_rows} row(s) when dropping inventory.")
            else:
                self.log_msg(f"Unknown option: {option}")
        self.options_set = True
        self.log_msg("Options set successfully.")

    def main_loop(self):  # sourcery skip: low-code-quality, use-named-expression
        # Setup
        api = StatusSocket()
        
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        # Anchors/counters
        npc_search_fail_count = 0
        theft_count = 0
        no_pouch_count = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # Check if we should eat
            while self.get_hp() < 50:
                if not self.status_check_passed():
                    return
                food_indexes = api.get_inv_item_indices(item_ids.all_food)
                if food_indexes:
                    self.log_msg("Eating...")
                    self.mouse.move_to(self.win.inventory_slots[food_indexes[0]].random_point())
                    self.mouse.click()
                    if len(food_indexes) > 1:  # eat another if available
                        time.sleep(1)
                        self.mouse.move_to(self.win.inventory_slots[food_indexes[1]].random_point())
                        self.mouse.click()
                else:
                    self.__logout(f"Out of food. Bot ran for {(time.time() - start_time) / 60} minutes.")
                    return

            if not self.status_check_passed():
                return

            # Check if we should drop inventory
            if self.should_drop_inv and api.get_is_inv_full():
                skip_slots = api.get_inv_item_indices(item_ids.all_food)
                # Always drop the last row
                remove = range(24, 28)
                for index in remove:
                    if index in skip_slots:
                        skip_slots.remove(index)
                self.drop_inventory(skip_rows=self.protect_rows, skip_slots=skip_slots)

            if not self.status_check_passed():
                return

            # Steal from NPC
            npc_pos: RuneLiteObject = self.get_nearest_tag(clr.CYAN)
            if npc_pos is not None:
                self.mouse.move_to(npc_pos.random_point(), mouseSpeed='fastest')
                if self.pickpocket_option != 0:
                    pag.rightClick()
                    if self.pickpocket_option == 1:
                        delta_y = 41
                    elif self.pickpocket_option == 2:
                        delta_y = 56
                    self.mouse.move_rel(x=0, y=delta_y, x_var=5, y_var=2, mouseSpeed="fastest")
                red_click = self.mouse.click_with_check()
                if self.pickpocket_option == 0 and red_click:
                    # If we missclicked on a left-click pickpocket, wait for a second to recalculate position
                    time.sleep(1)
                elif self.pickpocket_option == 0:
                    time.sleep(0.3)
                npc_search_fail_count = 0
                theft_count += 1
            else:
                npc_search_fail_count += 1
                time.sleep(1)
                if npc_search_fail_count > 39:
                    self.__logout(f"No NPC found for {npc_search_fail_count} seconds. Bot ran for {(time.time() - start_time) / 60} minutes.")
                    return

            # Click coin pouch
            if self.should_click_coin_pouch and theft_count % 20 == 0:
                self.log_msg("Clicking coin pouch...")
                pouch = imsearch.search_img_in_rect(image=self.coin_pouch_path, rect=self.win.control_panel)
                if pouch:
                    self.mouse.move_to(pouch.random_point(), mouseSpeed='fast', tween=pytweening.easeInOutQuad)
                    pag.click()
                    time.sleep(0.2)
                    no_pouch_count = 0
                else:
                    no_pouch_count += 1
                    if no_pouch_count > 5:
                        self.log_msg("Could not find coin pouch...")
                        self.drop_inventory(skip_rows=self.protect_rows)
                        no_pouch_count = 0

            # Check for mods
            if self.logout_on_friends and self.friends_nearby():
                self.__logout(f"Friends detected nearby. Bot ran for {(time.time() - start_time) / 60} minutes.")
                return

            if not self.status_check_passed():
                return

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)
