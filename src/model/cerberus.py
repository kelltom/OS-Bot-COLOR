from model.bot import Bot, BotStatus
from threading import Thread
import time


class Cerberus(Bot):
    def __init__(self):
        super().__init__()
        self.iterations = 10

    def play_pause(self):
        # if the bot is stopped, start it
        if self.status == BotStatus.STOPPED:
            print("play() from cerberus.py - starting bot")
            self.set_status(BotStatus.RUNNING)
            self.thread = Thread(target=self.main_loop)
            self.thread.start()
        # otherwise, if bot is already running, pause it and return status
        elif self.status == BotStatus.RUNNING:
            print("play() from cerberus.py - pausing bot")
            self.set_status(BotStatus.PAUSED)
        # otherwise, if bot is paused, resume it and return status
        elif self.status == BotStatus.PAUSED:
            print("play() from cerberus.py - resuming bot")
            self.set_status(BotStatus.RUNNING)

    def stop(self):
        # if bot isn't stopped, stop it
        if self.status != BotStatus.STOPPED:
            self.set_status(BotStatus.STOPPED)
            self.reset_iter()
            if self.thread.is_alive():
                self.thread.join()
                print("stop() from cerberus.py - joined thread, bot stopped")

    def restart(self):
        print("restart() from cerberus.py - bot restarted")
        self.stop()
        self.play_pause()

    def main_loop(self):
        '''
        Main bot loop. This will be run in a separate thread. It will run according to the bot's status.
        This loop is protected by a timeout so that the bot will stop if it takes too long, preventing leaks.
        '''
        while self.current_iter < self.iterations and self.status != BotStatus.STOPPED:
            pause_limit = 10  # TODO: 10 second pause limit, remove later
            self.increment_iter()
            print(f"main_loop() from cerberus.py - iteration: {self.current_iter} out of {self.iterations}")
            # if status is stopped, break and print message
            if self.status == BotStatus.STOPPED:
                print("main_loop() from cerberus.py - bot is stopped, breaking...")
                break
            # if status is paused, sleep for one second and continue until timeout
            while self.status == BotStatus.PAUSED:
                print("main_loop() from cerberus.py - bot is paused, sleeping...")
                time.sleep(1)
                # if bot is stopped, break
                if self.status == BotStatus.STOPPED:
                    print("main_loop() from cerberus.py - bot is stopped, breaking from pause...")
                    break
                pause_limit -= 1
                if pause_limit == 0:
                    print("main_loop() from cerberus.py - bot is paused, timeout reached, stopping...")
                    self.set_status(BotStatus.STOPPED)
                    break
            time.sleep(1)
        # bot has reached the end of its iterations
        print("main_loop() from cerberus.py - bot has reached the end of its iterations")
        if self.status != BotStatus.STOPPED:
            self.set_status(BotStatus.STOPPED)
