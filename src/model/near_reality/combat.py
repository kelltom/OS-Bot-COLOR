import time

from model.bot import BotStatus
from model.near_reality.nr_bot import NRBot
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject


class NRCombat(NRBot):
    def __init__(self):
        title = "Combat"
        description = (
            "This bot attacks NPCs tagged using RuneLite. Position your character in the viscinity of the tagged NPCs. "
            + "In the 'Entity Hider' plugin, make sure 'Hide Local Player 2D' is OFF."
        )
        super().__init__(bot_title=title, description=description)
        self.running_time = 15
        self.should_loot = False
        self.should_bank = False

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
                self.log_msg(f"Running time: {self.running_time} minutes.")
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Bot will run for {self.running_time} minutes.")
        self.options_set = True

    def main_loop(self):  # sourcery skip: low-code-quality
        api = StatusSocket()

        # Client setup
        self.toggle_auto_retaliate(toggle_on=True)

        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # loot
            if not api.get_is_inv_full() and self.pick_up_loot("Cowhide"):
                inv_count = len(api.get_inv())
                self.log_msg("Looting...")
                loot_timeout = 5  # wait up to 5 seconds to finish picking it up
                while len(api.get_inv()) == inv_count and loot_timeout > 0:
                    time.sleep(1)
                    loot_timeout -= 1
                time.sleep(0.5)

            # Try to attack an NPC
            timeout = 60  # check for up to 60 seconds
            while not self.is_in_combat():
                if timeout <= 0:
                    self.log_msg("Timed out looking for NPC.")
                    self.stop()
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

            # If combat is over, assume we killed the NPC.
            timeout = 90  # give our character 90 seconds to kill the NPC
            while self.is_in_combat():
                if timeout <= 0:
                    self.log_msg("Timed out fighting NPC.")
                    self.stop()
                time.sleep(2)
                timeout -= 2

            # Update progress
            self.log_msg("NPC killed.")
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Bot has completed all of its iterations.")
        self.logout()
        self.stop()
