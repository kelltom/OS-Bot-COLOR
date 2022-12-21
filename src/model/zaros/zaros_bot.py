"""
The OSNRBot class contains properties and functions that are specific to the OSNR client. This class should
be inherited by OSNR script classes.
"""
import time
from abc import ABCMeta

import pyautogui as pag

from model.runelite_bot import RuneLiteBot, RuneLiteWindow
from utilities.geometry import Point


class ZarosBot(RuneLiteBot, metaclass=ABCMeta):
    win: RuneLiteWindow = None

    def __init__(self, bot_title, description) -> None:
        super().__init__("Zaros", bot_title, description, RuneLiteWindow("Zaros"))

    """
    In this file, you can add custom functions that are specific to the Zaros client. For example, you can add
    a function that teleports using the custom Zaros teleport interface (for that, consider using image search
    to locate icons in the spellbook -- 1 image per spellbook should work).
    """

    def launch_game(self):
        return super().launch_game()
