"""
Combat bot for OSNR. Attacks tagged monsters.
"""
import time

from model.bot import BotStatus
from model.osnr.osnr_bot import OSNRBot
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject


class OSNRCombat(OSNRBot):
    def __init__(self):
        title = "Combat Bot"
        description = (
            "This bot attacks NPCs tagged using RuneLite. Position your character in the viscinity of the tagged NPCs. "
            + "In the 'Entity Hider' plugin, make sure 'Hide Local Player 2D' is OFF."
        )
        super().__init__(title=title, description=description)
        self.running_time = 15
        self.should_loot = False
        self.should_bank = False

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_checkbox_option("prefs", "Additional options", ["Loot", "Bank"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
                self.log_msg(f"Running time: {self.running_time} minutes.")
            elif option == "prefs":
                if "Loot" in options[option]:
                    self.should_loot = True
                    # self.log_msg("Looting enabled.")
                    self.log_msg("Note: Looting is not yet implemented.")
                if "Bank" in options[option]:
                    self.should_bank = True
                    # self.log_msg("Banking enabled.")
                    self.log_msg("Note: Banking is not yet implemented.")
            else:
                self.log_msg(f"Unknown option: {option}")
        self.options_set = True
        # TODO: if options are invalid, set options_set flag to false
        self.log_msg("Options set successfully.")

    def main_loop(self):  # sourcery skip: low-code-quality

        api = StatusSocket()

        # Client setup
        self.toggle_auto_retaliate(toggle_on=True)

        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if not self.status_check_passed():
                return

            # loot
            if not api.get_is_inv_full() and self.pick_up_loot("Cowhide"):
                inv_count = len(api.get_inv())
                self.log_msg("Looting...")
                loot_timeout = 5  # wait up to 5 seconds to finish picking it up
                while len(api.get_inv()) == inv_count and loot_timeout > 0:
                    if not self.status_check_passed():
                        return
                    time.sleep(1)
                    loot_timeout -= 1
                time.sleep(0.5)

            # Try to attack an NPC
            timeout = 60  # check for up to 60 seconds
            while not self.is_in_combat():
                if not self.status_check_passed():
                    return
                if timeout <= 0:
                    self.log_msg("Timed out looking for NPC.")
                    self.set_status(BotStatus.STOPPED)
                    return
                npc: RuneLiteObject = self.get_nearest_tagged_NPC()
                if npc is not None:
                    self.log_msg("Attacking NPC...")
                    self.mouse.move_to(npc.random_point())
                    self.mouse.click()
                    time.sleep(3)
                    timeout -= 3
                else:
                    self.log_msg("No NPC found.")
                    time.sleep(2)
                    timeout -= 2

            if not self.status_check_passed():
                return

            # If combat is over, assume we killed the NPC.
            timeout = 90  # give our character 90 seconds to kill the NPC
            while self.is_in_combat():
                if timeout <= 0:
                    self.log_msg("Timed out fighting NPC.")
                    self.set_status(BotStatus.STOPPED)
                    return
                time.sleep(2)
                timeout -= 2
                if not self.status_check_passed():
                    return

            # Update progress
            self.log_msg("NPC killed.")
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Bot has completed all of its iterations.")
        self.logout()
        self.set_status(BotStatus.STOPPED)
