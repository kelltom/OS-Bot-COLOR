'''
Combat bot for OSNR. Attacks tagged monsters.
'''
from model.bot import BotStatus
from model.osnr.osnr_bot import OSNRBot
import time


class OSNRCombat(OSNRBot):
    def __init__(self):
        title = "Combat Bot"
        description = ("This bot attacks NPCs tagged using Runelite. Position your character in the viscinity of the tagged NPCs.")
        super().__init__(title=title, description=description)
        # Create any additional bot options here. 'iterations' and 'current_iter' exist by default.
        self.should_loot = False
        self.should_bank = False

    def create_options(self):
        self.options_builder.add_slider_option("iterations", "How many kills?", 1, 100)
        self.options_builder.add_checkbox_option("prefs", "Additional options", ["Loot", "Bank"])

    def save_options(self, options: dict):
        for option in options:
            if option == "iterations":
                self.iterations = options[option]
                self.log_msg(f"The bot will kill {self.iterations} NPCs.")
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

    def main_loop(self):
        self.setup_osnr()

        # Make sure auto retaliate is on
        self.toggle_auto_retaliate(toggle_on=True)
        time.sleep(0.5)

        # Reselect inventory
        self.mouse.move_to(self.cp_inventory, 0.2, variance=3)
        self.mouse.click()
        time.sleep(0.5)

        while self.current_iter < self.iterations:
            if not self.status_check_passed():
                return

            # Attack NPC
            timeout = 60  # check for up to 60 seconds
            while not self.is_in_combat():
                if not self.status_check_passed():
                    return
                if timeout <= 0:
                    self.log_msg("Timed out looking for NPC.")
                    self.set_status(BotStatus.STOPPED)
                    return
                if self.attack_nearest_tagged(self.rect_game_view):
                    self.log_msg("Attempting to attack NPC...")
                    time.sleep(3)
                    timeout -= 3
                else:
                    self.log_msg("No NPC found.")
                    time.sleep(2)
                    timeout -= 2

            if not self.status_check_passed():
                return

            # If combat is over, assume we killed the NPC.
            timeout = 60  # give our character 1 minute to kill the NPC
            while self.is_in_combat():
                if timeout <= 0:
                    self.log_msg("Timed out fighting NPC.")
                    self.set_status(BotStatus.STOPPED)
                    return
                time.sleep(0.5)
                timeout -= 0.5
                if not self.status_check_passed():
                    return
            self.increment_iter()
            self.log_msg(f"Enemy killed. {self.iterations - self.current_iter} to go!")

        self.log_msg("Bot has completed all of its iterations.")
        self.set_status(BotStatus.STOPPED)
