"""
This file demonstrates how to set up a simple bot. It demonstrates how to implement the functions for
capturing user configuration of the bot, and includes a simulated bot loop that does not have any
side affects during testing.

To better understand how to implement a bot, please see the documentation for the Bot class as well as
the README/Wiki.
"""
import time

import utilities.debug as debug
from model.bot import Bot, BotStatus
from utilities.window import MockWindow


class ExampleBot(Bot):  # <-- if you're writing a bot for a RuneLite-based game, change "Bot" to "RuneLiteBot"
    def __init__(self):
        title = "Example Bot"
        description = (
            "This is where the description of the bot goes. Briefly describe how the bot works "
            + "and any important information the user needs to know before starting it."
        )
        # If you're writing a bot for a RuneLite-based game, change "MockWindow()" to "RuneLiteWindow("<name of your game>")" below
        # If your game uses a custom interface, you can also pass in a custom window class that inherits from Window or RuneLiteWindow
        super().__init__(title=title, description=description, window=MockWindow(), launchable=False)
        # This is where you should initialize any options/properties you want to use in the bot
        self.running_time = 1
        self.text_edit_example = None
        self.multi_select_example = None
        self.menu_example = None

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 180)  # max 180 minutes
        self.options_builder.add_text_edit_option("text_edit_example", "Text Edit Example", "Placeholder text here")
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        # Unpack the options dictionary received from the Options Menu UI
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "text_edit_example":
                self.text_edit_example = options[option]
            elif option == "multi_select_example":
                self.multi_select_example = options[option]
            elif option == "menu_example":
                self.menu_example = options[option]
            else:
                # Code will only ever reach this point if there is an issue with how the developer is dealing with options
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False

        # Let the user know what options were set
        self.log_msg(f"Bot will run for {self.running_time} minutes.")
        self.log_msg(f"Text edit example set to: {self.text_edit_example or 'None'}")
        self.log_msg(f"Multi-select example set to: {self.multi_select_example or 'None'}")
        self.log_msg(f"Menu example set to: {self.menu_example}")

        # --- OPTIONAL: LAUNCH GAME CLIENT ---
        # If your bot requires the game client to be launched with further-customized settings, let the user know here.
        # if self.launchable:
        #     self.log_msg("Please launch the game client using the button on the right.")

        # Set the `options_set` flag to True to allow underlying code to continue, and set the status to
        # CONFIGURED to indicate to the user that the bot is ready to run.
        self.options_set = True
        self.set_status(BotStatus.CONFIGURED)
        return

    def main_loop(self):
        """
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to set the status to STOPPED.

        Additional notes:
        Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
        Visit the Wiki for more.
        """

        # --- SCENARIO EXPLANATION ---
        """
        This ExampleBot script simulates a character moving between Location A and B. `time.sleep()` is used to
        simulate the bot waiting for conditions. Depending on your bot, it might be wise to add variables that
        keep track of progress, failed-attempts, etc.
        """
        player_position = "A"
        times_walked = 0

        # --- CLIENT SETUP ---
        """
        Before entering the bot loop, consider configuring the client window (E.g., setting auto-retaliate on/off,
        zooming to a certain percentage, making sure the inventory tab is open, etc.). This is not required, but it
        can be useful.
        """
        # self.set_camera_zoom(50) # <-- zooms the camera to 50%
        # self.set_auto_retaliate(True) # <-- turns on auto-retaliate
        # self.mouse.move_to(self.win.inventory_tabs[3].random_point()) # <-- moves the mouse to the inventory tab

        # --- MAIN LOOP ---
        """
        All bots should have a continous loop that runs until the some condition is met. In this case, we want to
        run the bot for a certain amount of time the user specified when they selected the bot's options.
        You may change this however you like (E.g., you may want to run the bot for a fixed number of iterations/kills instead).
        """
        start_time = time.time()  # get the current time in seconds
        end_time = self.running_time * 60  # convert the running time to seconds
        while time.time() - start_time < end_time:  # check if the elapsed time is less than the final running time
            # Character is at point A
            self.log_msg("Character is at point A")

            # Move character until it reachers point B
            steps_remaining = 4  # Lets pretend it takes 4 steps to move from A to B
            while player_position != "B":
                # We'll simulate the player getting one step closer by decrementing the `steps_remaining` by 1.
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
            self.log_msg(f"Player has walked from A to B  {times_walked}  time(s).")

            # We'll also update the progress bar on the UI.
            self.update_progress((time.time() - start_time) / end_time)  # value between 0 and 1

            # Now, the player teleports back to point `A`
            time.sleep(2)
            self.log_msg("Character is teleporting back to point A...")
            time.sleep(2)
            player_position = "A"

        # If the bot reaches here it has completed its running time.
        self.update_progress(1)
        self.log_msg("Bot has completed all of its iterations.")
        self.set_status(BotStatus.STOPPED)
