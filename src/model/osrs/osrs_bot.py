from abc import ABCMeta

from model.runelite_bot import RuneLiteBot, RuneLiteWindow


class OSRSBot(RuneLiteBot, metaclass=ABCMeta):
    win: RuneLiteWindow = None

    def __init__(self, bot_title, description) -> None:
        super().__init__("OSRS", bot_title, description)
