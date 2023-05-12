import time

import pyautogui as pag

import utilities.color as clr
import utilities.random_util as rd
from model.bot import BotStatus
from model.zaros.zaros_bot import ZarosBot


class ZarosWoodcutter(ZarosBot):
    def __init__(self):
        title = "Woodcutter"
        description = (
            "This bot power-chops wood. Position your character near some trees, tag them. Make sure you have an empty last inventory slot. Press the play"
            " button."
        )
        super().__init__(bot_title=title, description=description)
        self.running_time = 1
        self.protect_slots = 0
        self.logout_on_friends = True

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_slider_option("protect_slots", "When dropping, protect first x slots:", 0, 4)
        self.options_builder.add_checkbox_option("logout_on_friends", "Logout on friends list?", ["Enable"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "protect_slots":
                self.protect_slots = options[option]
            elif option == "logout_on_friends":
                self.logout_on_friends = options[option] == ["Enable"]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Protect slots: {self.protect_slots}.")
        self.log_msg(f"Logout on friends: {self.logout_on_friends}.")
        self.options_set = True

    def main_loop(self):
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        first_loop = True
        logs = 0
        failed_searches = 0

        # Last inventory slot color when empty
        x, y = self.win.inventory_slots[-1].get_center()
        self.empty_slot_clr = pag.pixel(x, y)

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # If inventory is full
            if self.__inv_is_full():
                self.drop_all(skip_slots=list(range(self.protect_slots)))
                logs += 28 - self.protect_slots
                self.log_msg(f"Logs cut: ~{logs}")
                time.sleep(1)

            # Find a tree
            tree = self.get_nearest_tag(clr.PINK)
            if tree is None:
                failed_searches += 1
                if failed_searches % 10 == 0:
                    self.log_msg("Searching for trees...")
                if failed_searches > 60:
                    # If we've been searching for a whole minute...
                    self.__logout("No tagged trees found. Logging out.")
                time.sleep(1)
                continue
            failed_searches = 0  # If code got here, a tree was found

            # Click tree and wait to start cutting
            self.mouse.move_to(tree.random_point())
            if not self.mouseover_text(contains="Chop"):
                continue
            self.mouse.click()

            if first_loop:
                # Chop for a few seconds to get the Woodcutting plugin to show up
                time.sleep(5)
                first_loop = False

            time.sleep(rd.truncated_normal_sample(1, 10, 2, 2))

            # Wait until we're done chopping
            while self.is_player_doing_action("Woodcutting"):
                time.sleep(1)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def __inv_is_full(self):
        """
        Private method to check if inventory is full based on the color of the last inventory slot.
        """
        x, y = self.win.inventory_slots[-1].get_center()
        return pag.pixel(x, y) != self.empty_slot_clr
