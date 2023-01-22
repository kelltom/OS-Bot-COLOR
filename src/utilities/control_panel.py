from typing import Union

from pyautogui import keyDown, keyUp

import utilities.imagesearch as imsearch
from model.osrs.osrs_bot import OSRSBot
from utilities.random_util import random_chance


class InvOpen(object):
    def __init__(self, osrs_bot: OSRSBot):
        self.osrs_bot = osrs_bot

    def __enter__(self):
        return _ensure_inventory_open(self.osrs_bot)

    def __exit__(self, *args, **kwargs):
        pass


class MagicOpen(object):
    def __init__(self, osrs_bot: OSRSBot):
        self.osrs_bot = osrs_bot

    def __enter__(self):
        return _ensure_magic_tab_open(self.osrs_bot)

    def __exit__(self, *args, **kwargs):
        pass


def get_active_tab(osrs_bot: OSRSBot) -> Union[int, None]:
    """
    Searches through the tabs in the player control panel and returns the index of the active tab or None if none was found

    osrs_bot: Reference to an OSRSBot instance
    """
    return next(
        (i for i in range(14) if _check_if_tab_active(osrs_bot=osrs_bot, tab=i)),
        None,
    )


def _check_if_tab_active(osrs_bot: OSRSBot, tab: int) -> bool:
    """
    Checks a specific tab to see if it is open

    osrs_bot: Reference to an OSRSBot instance
    tab: integer value of the control panel tab you would like to check if is open
    """

    inventory_path = imsearch.BOT_IMAGES.joinpath("control_panel", "selected.png")
    inv = imsearch.search_img_in_rect(image=inventory_path, rect=osrs_bot.win.cp_tabs[tab], confidence=0.35)

    return bool(inv)


def _ensure_inventory_open(osrs_bot: OSRSBot) -> bool:
    """
    Ensure a specific tab is open, if not open it

    return: True/False whether the tab has been succesfully opened
    """

    inv_open = _check_if_tab_active(osrs_bot, 3)

    if inv_open:
        osrs_bot.log_msg("Inventory not detected as open")

        if random_chance(0.1):
            osrs_bot.mouse.move_to(osrs_bot.win.cp_tabs[3].random_point())
            osrs_bot.mouse.click()

        else:
            keyDown("esc")
            keyUp("esc")

        inv_open = _check_if_tab_active(osrs_bot, 3)

    return inv_open


def _ensure_magic_tab_open(osrs_bot: OSRSBot):
    """
    Ensure a specific tab is open, if not open it

    return: True/False whether the tab has been succesfully opened
    """

    spellbook_open = _check_if_tab_active(osrs_bot, 6)

    if not spellbook_open:
        osrs_bot.log_msg("Spellbook not detected as open")

        if random_chance(0.1):
            osrs_bot.mouse.move_to(osrs_bot.win.cp_tabs[6].random_point())
            osrs_bot.mouse.click()

        else:
            keyDown("f6")
            keyUp("f6")

        spellbook_open = _check_if_tab_active(osrs_bot, 6)

    return spellbook_open
