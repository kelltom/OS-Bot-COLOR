'''
Combat bot for Alora. Kills tagged NPCs.
'''
from model.bot import BotStatus
from model.alora.alora_bot import AloraBot
import time


class AloraCombat(AloraBot):
    def __init__(self):
        title = "Combat Bot"
        description = ("This bot kills tagged NPCs in Alora RSPS. Make sure to tag all NPCS " +
                       "via RuneLite before starting the bot!")
        super().__init__(title=title, description=description)
        # Create any additional bot options here. 'iterations' and 'current_iter' exist by default.
        self.iterations = 0
        self.multi_select_example = None
        self.menu_example = None

    def create_options(self):
        self.options_builder.add_slider_option("iterations", "Iterations", 1, 100)
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])

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
        self.setup_alora()

        # Make sure auto retaliate is on
        self.toggle_auto_retaliate(toggle_on=True)
        time.sleep(0.5)

        # Reselect inventory
        self.mouse.move_to(self.cp_inventory, 0.2, variance=3)
        self.mouse.click()

        self.current_iter = 0
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
                if self.attack_first_tagged(self.rect_game_view):
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
            self.current_iter += 1
            self.update_progress(self.current_iter / self.iterations)
            self.log_msg(f"Enemy killed. {self.iterations - self.current_iter} to go!")
        self.update_progress(1)
        self.log_msg("Bot has completed all of its iterations.")
        self.set_status(BotStatus.STOPPED)
