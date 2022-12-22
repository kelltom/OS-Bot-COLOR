"""
The OSRS Bot class is the base class for all OSRS bots. It inherits from the RuneLiteBot class, which
pretty much provides all of the functionality for OSRS bots as it is. The only thing this class is doing,
is setting the game title to "OSRS". Now, when you create a new bot for Old School Runescape, you can
simply inherit from this class instead of the RuneLiteBot class and not have to worry about setting
the game title. This is just a convenience class in this case, but for private servers, this is where you'd
implement any custom functionality that is specific to the private server you're writing a bot for.
"""
from abc import ABCMeta

from model.runelite_bot import RuneLiteBot, RuneLiteWindow


class OSRSBot(RuneLiteBot, metaclass=ABCMeta):
    win: RuneLiteWindow = None

    def __init__(self, bot_title, description) -> None:
        super().__init__("OSRS", bot_title, description)
