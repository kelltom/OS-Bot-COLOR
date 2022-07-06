'''
This file demonstrates how to set up a simple bot. It demonstrates how to implement the functions for
capturing user configuration of the bot, and includes a simulated bot loop that does not have any
side affects during testing.

To better understand how to implement a bot, please see the documentation for the Bot class as well as
the README/Wiki.
'''

from model.bot import Bot, BotStatus
import time


class Example(Bot):
    def __init__(self):
        title = "Example Bot"
        description = ("This is where the description of the bot goes. Briefly describe how the bot works " +
                       "and any important information the user needs to know before starting it.")
        super().__init__(title=title, description=description)

    def set_options_gui(self):
        # TODO: implement disabling the UI buttons when the options menu is open.
        self.options_set = False

        # TODO: implement this
        self.iterations = 10
        self.options_set = True

        if self.options_set:
            msg = "set_options() from example.py - options set successfully"
        else:
            msg = "set_options() from example.py - failed to set options"

        self.log_msg(msg)
        print(msg)

    def main_loop(self):
        if not self.options_set:
            self.log_msg("Options not set. Please set options before starting.")
            self.set_status(BotStatus.STOPPED)
            return
        self.reset_iter()
        while self.current_iter < self.iterations and self.status != BotStatus.STOPPED:
            pause_limit = 10  # TODO: 10 second pause limit, remove later
            self.increment_iter()
            msg = f"main_loop() from example.py - iteration: {self.current_iter} out of {self.iterations}"
            self.log_msg(msg)
            print(msg)
            # if status is stopped, break and print message
            if self.status == BotStatus.STOPPED:
                msg = "main_loop() from example.py - bot is stopped, breaking..."
                self.log_msg(msg)
                print(msg)
                return
            # if status is paused, sleep for one second and continue until timeout
            while self.status == BotStatus.PAUSED:
                msg = "main_loop() from example.py - bot is paused, sleeping..."
                self.log_msg(msg)
                print(msg)
                time.sleep(1)
                # if bot is stopped, break
                if self.status == BotStatus.STOPPED:
                    msg = "main_loop() from example.py - bot is stopped, breaking from pause..."
                    self.log_msg(msg)
                    print(msg)
                    return
                pause_limit -= 1
                if pause_limit == 0:
                    msg = "main_loop() from example.py - bot is paused, timeout reached, stopping..."
                    self.log_msg(msg)
                    print(msg)
                    self.set_status(BotStatus.STOPPED)
                    return
            time.sleep(1)
        # if the bot was stopped manually, reset iterations
        if self.current_iter < self.iterations:
            self.reset_iter()
        msg = "main_loop() from example.py - bot has reached the end of its iterations"
        self.log_msg(msg)
        print(msg)
        # if bot hasn't been stopped yet...
        if self.status != BotStatus.STOPPED:
            self.set_status(BotStatus.STOPPED)
