from model.bot import Bot, BotStatus
import time


class Firemaking(Bot):
    def __init__(self):
        title = "Firemaking"
        description = ("This bot automates the firemaking skill. The bot will automatically position the player " +
                       "character in a safe area and start the firemaking based on the options you select below.")
        super().__init__(title=title, description=description)

        self.iterations = 10

    def save_settings(self, settings: dict):
        pass

    def main_loop(self):
        '''
        Main bot loop. This function should be called on another thread. It will run according to the bot's status.
        This loop is protected by a timeout so that the bot will stop if it takes too long, preventing leaks.
        '''
        while self.current_iter < self.iterations and self.status != BotStatus.STOPPED:
            pause_limit = 10  # TODO: 10 second pause limit, remove later
            self.increment_iter()
            msg = f"main_loop() from firemaking.py - iteration: {self.current_iter} out of {self.iterations}"
            self.log_msg(msg)
            print(msg)
            # if status is stopped, break and print message
            if self.status == BotStatus.STOPPED:
                msg = "main_loop() from firemaking.py - bot is stopped, breaking..."
                self.log_msg(msg)
                print(msg)
                break
            # if status is paused, sleep for one second and continue until timeout
            while self.status == BotStatus.PAUSED:
                msg = "main_loop() from firemaking.py - bot is paused, sleeping..."
                self.log_msg(msg)
                print(msg)
                time.sleep(1)
                # if bot is stopped, break
                if self.status == BotStatus.STOPPED:
                    msg = "main_loop() from firemaking.py - bot is stopped, breaking from pause..."
                    self.log_msg(msg)
                    print(msg)
                    break
                pause_limit -= 1
                if pause_limit == 0:
                    msg = "main_loop() from firemaking.py - bot is paused, timeout reached, stopping..."
                    self.log_msg(msg)
                    print(msg)
                    self.current_iter = self.iterations
                    break
            time.sleep(1)
        msg = "main_loop() from firemaking.py - bot has terminated or reached the end of its iterations"
        self.log_msg(msg)
        print(msg)
        # if bot hasn't been stopped yet...
        if self.status != BotStatus.STOPPED:
            self.set_status(BotStatus.STOPPED)
            self.reset_iter()
