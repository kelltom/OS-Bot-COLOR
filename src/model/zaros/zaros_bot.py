from abc import ABCMeta

from model.runelite_bot import RuneLiteBot, RuneLiteWindow


class ZarosBot(RuneLiteBot, metaclass=ABCMeta):
    win: RuneLiteWindow = None

    def __init__(self, bot_title, description) -> None:
        super().__init__("Zaros", bot_title, description, RuneLiteWindow("Zaros"))

    """
    In this file, you can add custom functions that are specific to the Zaros client. For example, you can add
    a function that teleports using the custom Zaros teleport interface (for that, consider using image search
    to locate icons in the spellbook -- 1 image per spellbook should work).
    """
