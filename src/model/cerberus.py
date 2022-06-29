from model.bot import Bot, BotStatus
from threading import Thread
import time


class Cerberus(Bot):
    def __init__(self):
        super().__init__()
        self.iterations = 10

    def play(self):
        if self.status == BotStatus.STOPPED:
            self.current_iter = 0
            self.status = BotStatus.RUNNING
            self.thread = Thread(target=self.main_loop)
            self.thread.start()
            print("play() from cerberus.py")
        # otherwise, if bot is paused, print message reporting failure
        elif self.status == BotStatus.PAUSED:
            print("play() from cerberus.py - bot is paused, haven't implemented resuming yet, try stopping first")

    def pause(self):
        if self.status == BotStatus.RUNNING:
            self.status = BotStatus.PAUSED
            print("pause() from cerberus.py")
        else:
            print("pause() from cerberus.py - bot is not running, cannot pause")

    def stop(self):
        # if bot isn't stopped, stop it
        if self.status != BotStatus.STOPPED:
            self.status = BotStatus.STOPPED
            print("stop() from cerberus.py")
            self.thread.join()
        else:
            print("stop() from cerberus.py - bot is already stopped")

    def main_loop(self):
        while self.current_iter < self.iterations:
            self.current_iter += 1
            print(f"main_loop() from cerberus.py - iteration: {self.current_iter} out of {self.iterations}")
            # print the status
            print(f"main_loop() from cerberus.py - status: {self.status}")
            # if status is stopped, break and print message
            if self.status == BotStatus.STOPPED:
                print("main_loop() from cerberus.py - bot is stopped, breaking")
                break
            time.sleep(1)
