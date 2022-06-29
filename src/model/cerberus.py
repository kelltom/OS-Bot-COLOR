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
            self.current_iter = 0
            self.status = BotStatus.RUNNING
            print("play() from cerberus.py - running bot fresh")
            self.thread = Thread(target=self.main_loop)
            self.thread.start()
        # otherwise, if bot is already running, pause it and return status
        elif self.status == BotStatus.RUNNING:
            self.status = BotStatus.PAUSED
            print("play() from cerberus.py - pausing bot")
        # otherwise, if bot is paused, resume it and return status
        elif self.status == BotStatus.PAUSED:
            self.status = BotStatus.RUNNING
            print("play() from cerberus.py - resuming bot")

    def stop(self):
        # if bot isn't stopped, stop it
        if self.status != BotStatus.STOPPED:
            self.status = BotStatus.STOPPED
            if self.thread.is_alive():
                self.thread.join()
                print("stop() from cerberus.py - joined thread")

    def restart(self):
        self.stop()
        self.play_pause()
        print("restart() from cerberus.py - bot restarted")

    def main_loop(self):
        '''
        Main bot loop. This will be run in a separate thread. It will run according to the bot's status.
        This loop is protected by a timeout so that the bot will stop if it takes too long, preventing leaks.
        '''
        while self.current_iter < self.iterations:
            self.current_iter += 1
            print(f"main_loop() from cerberus.py - iteration: {self.current_iter} out of {self.iterations}")
            # if status is stopped, break and print message
            if self.status == BotStatus.STOPPED:
                print("main_loop() from cerberus.py - bot is stopped, breaking")
                break
            # while bot is paused, sleep for 1 second
            while self.status == BotStatus.PAUSED:
                print("main_loop() from cerberus.py - bot is paused, sleeping")
                time.sleep(1)
                if self.status == BotStatus.STOPPED:
                    print("main_loop() from cerberus.py - bot is stopped, breaking")
                    break
            time.sleep(1)
        # if bot is stopped, break and print message
        print("main_loop() from cerberus.py - stopping...")
        self.status = BotStatus.STOPPED
