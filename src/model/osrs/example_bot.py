'''
This file demonstrates how to set up a simple bot. It demonstrates how to implement the functions for
capturing user configuration of the bot, and includes a simulated bot loop that does not have any
side affects during testing.

To better understand how to implement a bot, please see the documentation for the Bot class as well as
the README/Wiki.
'''
from model.bot import Bot, BotStatus
from utilities.window import MockWindow
import time

class ExampleBot(Bot):  # <-- if you're writing a bot for a RuneLite-based game, change "Bot" to "RuneLiteBot"
    def __init__(self):
        title = "Example Bot"
        description = ("This is where the description of the bot goes. Briefly describe how the bot works " +
                       "and any important information the user needs to know before starting it.")
        # If you're writing a bot for a RuneLite-based game, change "MockWindow()" to "RuneLiteWindow("<name of your game>")" below
        super().__init__(title=title, description=description, window=MockWindow())
        # This is where you should initialize any options/properties you want to use in the bot
        self.running_time = 1
        self.multi_select_example = None
        self.menu_example = None

    def create_options(self):
        '''
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        '''
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 180)  # max 180 minutes
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])

    def save_options(self, options: dict):
        '''
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False. No need to set bot status.
        '''
        self.options_set = True
        # Unpack the options dictionary received from the Options Menu UI
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "multi_select_example":
                self.multi_select_example = options[option]
            elif option == "menu_example":
                self.menu_example = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False
        if not self.options_set:
            self.log_msg("Failed to set options.")
            print("Developer: ensure option keys are correct, and that the option values are being accessed correctly.")
            return
        # Let the user know what options were set
        self.log_msg(f"Bot will run for {self.running_time} minutes.")
        self.log_msg(f"Multi-select example set to: {self.multi_select_example}")
        self.log_msg(f"Menu example set to: {self.menu_example}")
        return

    def main_loop(self):
        '''
        When implementing this function, you have the following responsibilities:
        1. Frequently check the status of the bot throughout the loop using self.status_check_passed(). Call it
           before your bot makes any major moves to prevent unwanted side affects.
            1.1. If the status check fails, simply return. Log messages are already handled.
        2. The controller is not listening for changes, it must be told. If you need to halt the bot from
           within the main_loop() without the user having manually requested it, be sure to set the status
           to STOPPED by using 'self.set_status(BotStatus.STOPPED)' before returning. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        3. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        5. At the end of the main loop, make sure to set the status to STOPPED.

        Additional notes:
        1. Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
           Visit the Wiki for more.
        2. A bot's main_loop() is called on a daemon thread, so it will terminate when the program is closed.
           If things ever get weird, closing the program will terminate the bot.
        '''

        # --- SCENARIO EXPLANATION ---
        '''
        This ExampleBot script simulates a character moving between Location A and B. Time.sleep() is used to
        simulate the bot waiting for conditions. Depending on your bot, it might be wise to add variables that
        keep track of progress, failed-attempts, etc.
        '''
        player_position = "A"
        times_walked = 0

        # --- CLIENT SETUP ---
        '''
        Before entering the bot loop, consider configuring the client window (E.g., setting auto-retaliate on/off,
        zooming to a certain percentage, making sure the inventory tab is open, etc.). This is not required, but it
        can be useful.
        '''
        # self.set_camera_zoom(50) # <-- zooms the camera to 50%

        # --- MAIN LOOP ---
        '''
        This program runs until the time elapsed exceeds the user-defined time limit.
        You may change this however you like (E.g., you may want to run the bot for a fixed number of iterations/kills).
        '''
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            # Character is at point A
            self.log_msg("Character is at point A")

            # Move character until it reachers point B
            steps_remaining = 4  # Lets pretend it takes 4 steps to move from A to B
            while player_position != "B":

                # When you enter a nested loop like this, it's wise to add a status check call.
                # You want to do this so that the bot is listening for user commands to pause/stop
                # while in the loop. Otherwise, it'll ignore the user's requests to pause/stop.
                if not self.status_check_passed():
                    return

                # We have traversed one step, so we will decrement the steps remaining by 1.
                steps_remaining -= 1
                time.sleep(2)

                # Inform the user where the character is
                if steps_remaining == 0:
                    self.log_msg("Character is at point B")
                    player_position = "B"
                elif steps_remaining == 1:
                    self.log_msg("Character is very close to B...")
                elif steps_remaining == 2:
                    self.log_msg("Character is still walking...")
                elif steps_remaining == 3:
                    self.log_msg("Character is walking to point B...")
            
            time.sleep(2)
            # Since the loop has terminated, we know the character is at point B.
            # We'll inform the user how many times the character has walked from A to B so far.
            times_walked += 1
            self.log_msg(f"Player has walked from A to B  {times_walked}  time(s).")  # UI log section
            
            # We'll also update the progress bar on the UI.
            self.update_progress((time.time() - start_time) / end_time)  # value betwee 0 and 1

            # Teleport back to A
            time.sleep(2)
            self.log_msg("Character is teleporting back to point A...")
            time.sleep(2)
            player_position = "A"

            # Check once more for status and keyboard interrupts
            if not self.status_check_passed():
                return

        # If the bot reaches here it has completed its running time.
        self.update_progress(1)
        self.log_msg("Bot has completed all of its iterations.")
        self.set_status(BotStatus.STOPPED)
