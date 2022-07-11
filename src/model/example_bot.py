'''
This file demonstrates how to set up a simple bot. It demonstrates how to implement the functions for
capturing user configuration of the bot, and includes a simulated bot loop that does not have any
side affects during testing.

To better understand how to implement a bot, please see the documentation for the Bot class as well as
the README/Wiki.
'''

from model.bot import Bot, BotStatus
import time


class ExampleBot(Bot):
    def __init__(self):
        title = "Example Bot"
        description = ("This is where the description of the bot goes. Briefly describe how the bot works " +
                       "and any important information the user needs to know before starting it.")
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
            else:
                self.log_msg(f"Unknown option: {option}")
        self.options_set = True

        # TODO: if options are invalid, set options_set flag to false

        self.log_msg("Options set successfully.")

    def main_loop(self):
        '''
        When implementing this function, you have the following responsibilities:
        1. Frequently check the status of the bot throughout the loop using self.status_check_passed(). Call it
           before your bot makes any major moves to prevent unwanted side affects.
            1.1. If the status check fails, simply return. Log messages are already handled.
        2. The controller is not listening for changes, it must be told. If you need to halt the bot from
           within the main_loop() without the user having manually requested it, be sure to set the status
           to STOPPED by using self.set_status() before returning.
        3. Frequently log relevant messages to the controller to be delivered to the UI.
        4. Make sure to use self.increment_iter() to increment the current iteration counter. This will increment
           the iteration counter by 1 while notifying the controller.
        5. At the end of the main loop, make sure to set the status to STOPPED.

        Additional notes:
        1. By default, the current iterations (and progress bar) are reset upon MANUAL stops and starts. It's
           typically a good idea to NOT reset the iterations when the bot stops due to 'natural causes' (E.g.,
           reaching a timeout, naturally finishing, etc.). This way, if the user was AFK, they'll see where
           the progress bar left off before the bot stopped itself. If you want to reset the current iteration for
           any reason, use self.reset_iter().
        2. TODO: Make use of the BotUtils class. It has many functions to simplify commonly used bot commands.
        3. A bot's main_loop() is called on a daemon thread, so it will terminate when the program is closed.
        '''
        # This example bot loop simulates a character moving between Location A and B. Time.sleep() is used to
        # simulate the bot waiting for conditions.
        self.player_position = "A"
        while self.current_iter < self.iterations:
            time.sleep(1)
            # Character is at point A
            self.log_msg("Character is at point A")
            # Move character to B
            self.steps = 4  # Lets pretend it takes 3 steps to move from A to B
            while self.player_position != "B":
                # This function is best used within inner loops to check for status and keyboard interrupts
                if not self.status_check_passed():
                    return
                self.steps -= 1
                time.sleep(1.5)
                if self.steps == 3:
                    self.log_msg("Character is walking to point B...")
                elif self.steps == 2:
                    self.log_msg("Character is almost there...")
                elif self.steps == 1:
                    self.log_msg("Character is very close to B...")
                elif self.steps == 0:
                    self.log_msg("Character is at point B")
                    self.player_position = "B"
            time.sleep(1)
            self.log_msg("Character is teleporting back to point A...")
            time.sleep(1)
            self.increment_iter()
            self.player_position = "A"
            # Check once more for status and keyboard interrupts
            if not self.status_check_passed():
                return
        # If the bot reaches here it has completed all of its iterations.
        self.log_msg("Bot has completed all of its iterations.")
        self.set_status(BotStatus.STOPPED)
