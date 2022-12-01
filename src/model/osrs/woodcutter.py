'''
Trains Runecrafting via Astral Runes.
'''
from model.runelite_bot import RuneLiteBot, BotStatus
from utilities.APIs.morg_http_client import MorgHTTPSocket
from utilities.APIs.status_socket import StatusSocket
import pyautogui as pag
import time

class OSRSWoodcutter(RuneLiteBot):
    def __init__(self):
        title = "Woodcutter"
        description = ("This bot power-chops wood. Position your character near some trees, tag them, and press the play button.")
        super().__init__(title=title, description=description)
        self.running_time = 1
        self.protect_slots = 0
        self.logout_on_friends = True

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_slider_option("protect_slots", "When dropping, protect first x slots:", 0, 4)

    def save_options(self, options: dict):
        self.options_set = True
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "protect_slots":
                self.protect_slots = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False
                self.log_msg("Failed to set options.")
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Protect slots: {self.protect_slots}.")
        self.log_msg("Options set successfully.")

    def main_loop(self):
        # Setup API
        api_morg = MorgHTTPSocket()
        api_status = StatusSocket()

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        logs = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if not self.status_check_passed():
                return

            # If inventory is full
            if api_status.get_is_inv_full():
                self.drop_inventory(skip_slots=list(range(self.protect_slots)))
                logs += 28 - self.protect_slots
                self.log_msg(f"Logs cut: ~{logs}")
                time.sleep(1)

            if not self.status_check_passed():
                return

            # Find a tree
            tree = self.get_nearest_tag(self.PINK)
            if tree is None:
                failed_searches += 1
                if failed_searches % 10 == 0:
                    self.log_msg("Searching for trees...")
                if failed_searches > 60:
                    # If we've been searching for a whole minute...
                    self.__logout("No tagged trees found. Logging out.")
                    return
                time.sleep(1)
                continue
            failed_searches = 0  # If code got here, a tree was found

            # Click tree and wait to start cutting
            self.mouse.move_to(tree.random_point())
            if self.mouse.click_with_check():
                if api_morg.get_is_player_idle():
                    # Sometimes, you can click a tree right as you level up and you'll stall out.
                    # This will click the tree again if that happens.
                    continue
                if api_morg.wait_til_gained_xp(skill="woodcutting", timeout=15) is None:
                    self.log_msg("Timed out waiting for player to gain xp. If this keeps " +
                                 "happening, either increase the wait timeout - or there may be a bug.")
                    continue
            else:
                self.log_msg("Misclicked tree.")
                while api_morg.get_is_player_idle():
                    self.log_msg("Waiting for player to stop moving...")
                    time.sleep(1)
                continue

            if not self.status_check_passed():
                return

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)
