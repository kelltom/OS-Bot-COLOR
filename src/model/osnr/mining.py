from model.bot import BotStatus
from model.osnr.osnr_bot import OSNRBot
import pyautogui as pag
import time


class OSNRMining(OSNRBot):
    def __init__(self):
        title = "Mining"
        description = ("This bot mines rocks. Equip a pickaxe, empty your inventory, place your character " +
                       "between some rocks and mark (shift + right-click) the ones you want to mine. Your character " +
                       "must remain stationary.")
        super().__init__(title=title, description=description)
        self.running_time = 2
        self.logout_on_friends = False

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
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
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False
                self.log_msg("Failed to set options.")
                return
        self.options_set = True
        self.log_msg("Options set successfully.")

    def main_loop(self):  # sourcery skip: low-code-quality
        # Setup
        self.setup_osnr(zoom_percentage=90)

        if not self.status_check_passed():
            return

        # Set compass
        self.mouse.move_to(self.orb_compass)
        self.mouse.click()
        time.sleep(0.5)

        # Move camera up
        pag.keyDown('up')
        time.sleep(2)
        pag.keyUp('up')
        time.sleep(0.5)

        last_inventory_pos = self.inventory_slots[6][3]
        last_inventory_rgb = pag.pixel(last_inventory_pos.x, last_inventory_pos.y)
        mined = 0
        failed_searches = 0

        # Get the center pixel of each tagged rock, and it's color
        rocks = self.get_all_tagged_in_rect(self.rect_game_view, self.TAG_PINK)
        if len(rocks) == 0:
            self.log_msg("No tagged rocks found.")
            self.set_status(BotStatus.STOPPED)
            return
        rock_rgb = [pag.pixel(rock.x, rock.y) for rock in rocks]

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if not self.status_check_passed():
                return

            # Check to drop inventory
            if pag.pixel(last_inventory_pos.x, last_inventory_pos.y) != last_inventory_rgb:
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

            # Pick a rock to start whacking
            mine_success = None  # used to keep track of whether or not we successfully mined a rock
            for i, rock in enumerate(rocks):
                if not self.status_check_passed():
                    return
                if pag.pixel(rock.x, rock.y) == rock_rgb[i]:
                    self.mouse.move_to(rock)
                    self.mouse.click()
                    time.sleep(0.3)
                    # Wait until the rock is depleted
                    wait_time, timeout = 0, 15
                    while pag.pixel(rock.x, rock.y) == rock_rgb[i]:
                        time.sleep(0.6)
                        wait_time += 0.6
                        if wait_time > timeout:
                            self.log_msg("Timed out mining rock. Moving on.")
                            mine_success = False
                            break
                    if mine_success is None:
                        mine_success = True
                        mined += 1
                        self.log_msg(f"Rocks mined: {mined}")
                        failed_searches = 0
                        time.sleep(0.15)
                    break

            if not mine_success:
                failed_searches += 1
                self.log_msg("Failed to find rock. Waiting...")
                time.sleep(2)

            if failed_searches > 5:
                self.log_msg("Timed out looking for rocks. Stopping.")
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
