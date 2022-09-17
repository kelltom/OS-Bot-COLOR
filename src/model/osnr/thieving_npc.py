'''
Thieving bot for OSNR. Thieves from NPCs.
'''
from model.bot import BotStatus
from model.osnr.osnr_bot import OSNRBot
import pathlib
import pyautogui as pag
import time
from utilities.bot_cv import Point
import utilities.bot_cv as bcv


class OSNRThievingNPC(OSNRBot):
    def __init__(self):
        title = "Thieving NPC Bot"
        description = ("This bot thieves from NPCs in OSNR. Position your character near the NPC you wish to thieve from. " +
                       "If you have food, tag all in inventory as light-blue. Start bot with full HP, " +
                       "and empty last inventory slot. If you risk attacking nearby NPCs via misclick, turn NPC attack options to 'hidden'.")
        super().__init__(title=title, description=description)
        self.running_time = 0
        self.logout_on_friends = False
        self.pickpocket_option = 0
        self.compass_direction = 0
        self.should_click_coin_pouch = False
        self.should_drop_inv = False
        self.protect_rows = 0
        self.coin_pouch_path = f"{pathlib.Path(__file__).parent.parent.parent.resolve()}/images/bot/near_reality/coin_pouch.png"

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 200)
        self.options_builder.add_dropdown_option("logout_on_friends", "Logout when friends are nearby?", ["Yes", "No"])
        self.options_builder.add_dropdown_option("pickpocket_option", "Where is the pickpocket option?", ["Left-click", "2nd option", "3rd option"])
        self.options_builder.add_dropdown_option("compass_direction", "Compass direction?", ["North", "East", "South", "West"])
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
            elif option == "compass_direction":
                if res == "North":
                    self.compass_direction = 0
                    self.log_msg("Compass direction: North.")
                elif res == "East":
                    self.compass_direction = 1
                    self.log_msg("Compass direction: East.")
                elif res == "South":
                    self.compass_direction = 2
                    self.log_msg("Compass direction: South.")
                elif res == "West":
                    self.compass_direction = 3
                    self.log_msg("Compass direction: West.")
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
        self.setup_osnr(zoom_percentage=50)

        # Config camera
        if self.compass_direction == 0:
            self.set_compass_north()
        elif self.compass_direction == 1:
            self.set_compass_east()
        elif self.compass_direction == 2:
            self.set_compass_south()
        elif self.compass_direction == 3:
            self.set_compass_west()
        
        self.move_camera_up()

        # Anchors/counters
        hp_threshold_pos = Point(541, 394)  # TODO: implement checking health threshold
        hp_threshold_rgb = pag.pixel(hp_threshold_pos.x, hp_threshold_pos.y)
        last_inventory_pos = self.inventory_slots[6][3]  # TODO: or [-1][-1]?
        last_inventory_rgb = pag.pixel(last_inventory_pos.x, last_inventory_pos.y)
        npc_search_fail_count = 0
        theft_count = 0
        no_pouch_count = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # Check if we should eat
            while pag.pixel(hp_threshold_pos.x, hp_threshold_pos.y) != hp_threshold_rgb:
                if not self.status_check_passed():
                    return
                foods = self.get_all_tagged_in_rect(rect=self.rect_inventory, color=self.TAG_BLUE)
                if len(foods) > 0:
                    self.log_msg("Eating...")
                    self.mouse.move_to(foods[0])
                    time.sleep(0.3)
                    pag.click()
                    if len(foods) > 1:  # eat another if available
                        time.sleep(1)
                        self.mouse.move_to(foods[1])
                        time.sleep(0.3)
                        pag.click()
                else:
                    self.log_msg("Out of food. Aborting...")
                    self.logout()
                    self.set_status(BotStatus.STOPPED)
                    return

            if not self.status_check_passed():
                return

            # Check if we should drop inventory
            if self.should_drop_inv and pag.pixel(last_inventory_pos.x, last_inventory_pos.y) != last_inventory_rgb:
                self.drop_inventory(skip_rows=self.protect_rows)

            if not self.status_check_passed():
                return

            # Steal from NPC
            npc_pos = self.get_nearest_tagged_NPC(game_view=self.rect_game_view)
            if npc_pos is not None:
                self.mouse.move_to(npc_pos, duration=0.1)
                if self.pickpocket_option != 0:
                    pag.rightClick()
                    if self.pickpocket_option == 1:
                        delta_y = 41
                    elif self.pickpocket_option == 2:
                        delta_y = 56
                    self.mouse.move_rel(x=0, y=delta_y, duration=0.2)
                pag.click()
                if self.pickpocket_option == 0:
                    time.sleep(0.3)
                npc_search_fail_count = 0
                theft_count += 1
            else:
                npc_search_fail_count += 1
                time.sleep(1)
                if npc_search_fail_count > 39:
                    self.log_msg(f"No NPC found for {npc_search_fail_count} seconds. Aborting...")
                    self.logout()
                    self.set_status(BotStatus.STOPPED)
                    return

            # Click coin pouch
            if self.should_click_coin_pouch and theft_count % 10 == 0:
                self.log_msg("Clicking coin pouch...")
                pouch = bcv.search_img_in_rect(img_path=self.coin_pouch_path, rect=self.rect_inventory, conf=0.9)
                if pouch:
                    self.mouse.move_to(pouch)
                    time.sleep(0.5)
                    pag.click()
                    no_pouch_count = 0
                else:
                    no_pouch_count += 1
                    if no_pouch_count > 5:
                        self.log_msg("Could not find coin pouch...")
                        self.drop_inventory(skip_rows=self.protect_rows)
                        no_pouch_count = 0

            # Check for mods
            if self.logout_on_friends and self.friends_nearby():
                self.log_msg("Friends detected nearby...")
                self.logout()
                self.set_status(BotStatus.STOPPED)
                return

            if not self.status_check_passed():
                return

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.set_status(BotStatus.STOPPED)
