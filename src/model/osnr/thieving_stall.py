'''
Thieving bot for OSNR. Thieves from stalls.
'''
from model.bot import BotStatus
from model.osnr.osnr_bot import OSNRBot


class OSNRThievingStall(OSNRBot):
    def __init__(self):
        title = "Thieving Stall Bot"
        description = ("This bot thieves at stalls in OSNR. Position your character south of the stall you wish to thieve at. " +
                       "Use the options menu to choose how long to run the bot, and whether to drop items or not.")
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
    
    def create_options(self):
        self.options_builder.add_slider_option("iterations", "Iterations", 1, 100)
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])

    def main_loop(self):
        '''
        TODO:
        This function should consider the following:
            - Should the bot bank?
            - Should the bot loot?
            - Should the bot heal?
            - Should the bot pray?
        '''
        self.setup_osnr()
        self.set_status(BotStatus.STOPPED)
