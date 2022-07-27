'''
Combat bot for Alora. Kills tagged NPCs.
'''
from model.bot import BotStatus
from model.alora_bot import AloraBot
import time


class AloraCombat(AloraBot):
    def __init__(self):
        title = "Combat Bot"
        description = ("This bot kills tagged NPCs in Alora RSPS. Make sure to tag all NPCS " +
                       "via Runelite before starting the bot!")
        super().__init__(title=title, description=description)
        # Create any additional bot options here. 'iterations' and 'current_iter' exist by default.

    def save_options(self, options: dict):
        '''
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False. No need to set bot status.
        '''
        for option in options:
            if option == "iterations":
                self.iterations = options[option]
                self.log_msg(f"Iterations set to: {self.iterations}")
            elif option == "multi_select_example":
                self.multi_select_example = options[option]
                self.log_msg(f"Multi-select example set to: {self.multi_select_example}")
            elif option == "menu_example":
                self.menu_example = options[option]
                self.log_msg(f"Menu example set to: {self.menu_example}")
            else:
                self.log_msg(f"Unknown option: {option}")
        self.options_set = True

        # TODO: if options are invalid, set options_set flag to false

        self.log_msg("Options set successfully.")

    def main_loop(self):
        '''
        TODO:
        This function should consider the following:
            - Should the bot bank?
            - Should the bot loot?
            - Should the bot heal?
            - Should the bot pray?
        '''
        self.log_msg("Configuring client window...")
        self.setup_alora()
        self.log_msg("Client window configured.")

        # Make sure auto retaliate is on
        self.log_msg("Enabling auto retaliate...")
        self.toggle_auto_retaliate(toggle_on=True)
        time.sleep(0.5)

        # Reselect inventory
        self.hc.move(self.cp_inventory, 0.2)
        self.hc.click()

        while self.current_iter < self.iterations:
            if not self.status_check_passed():
                return

            # Attack NPC
            timeout = 10  # check for up to 10 seconds
            while not self.is_in_combat():
                if not self.status_check_passed():
                    return
                if timeout <= 0:
                    self.log_msg("Timed out looking for NPC.")
                    self.set_status(BotStatus.STOPPED)
                    return
                self.log_msg("Attempting to attack NPC...")
                if self.attack_nearest_tagged(self.rect_game_view):
                    self.log_msg("NPC targetted.")
                    time.sleep(2)
                    timeout -= 2
                else:
                    self.log_msg("No NPC found.")
                    time.sleep(0.5)
                    timeout -= 0.5

            if not self.status_check_passed():
                return

            # If combat is over, assume we killed the NPC.
            timeout = 60  # give our character 1 minute to kill the NPC
            while self.is_in_combat():
                if timeout <= 0:
                    self.log_msg("Timed out fighting NPC.")
                    self.set_status(BotStatus.STOPPED)
                    return
                time.sleep(1)
                timeout -= 1
                if not self.status_check_passed():
                    return
            self.increment_iter()
            self.log_msg(f"Enemy killed. {self.iterations - self.current_iter} to go!")
            time.sleep(0.5)

        self.log_msg("Bot has completed all of its iterations.")
        self.set_status(BotStatus.STOPPED)