from model.bot import Bot, BotStatus


class Cerberus(Bot):
    def __init__(self, name, status: BotStatus = BotStatus.STOPPED, iterations: int = 0, breaks: bool = False):
        super().__init__(name, status, iterations, breaks)

    def play(self):
        self.status = BotStatus.RUNNING
        print("play() from cerberus.py")

    def pause(self):
        self.status = BotStatus.PAUSED
        print("pause() from cerberus.py")

    def stop(self):
        self.status = BotStatus.STOPPED
        print("stop() from cerberus.py")

    def main_loop(self):
        pass
