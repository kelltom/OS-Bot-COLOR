import utilities.imagesearch as imsearch
from model.osrs.osrs_bot import OSRSBot
from typing import Union

def _get_active_tab(osrs_bot: OSRSBot) -> Union[int, None]:
    """
    Searches through the tabs in the player control panel and returns the index of the active tab or None if none was found

    osrs_bot: Reference to an OSRSBot instance
    """
    for i in range(0,14):
        inventory_path = imsearch.BOT_IMAGES.joinpath("control_panel","selected.png")
        inv = imsearch.search_img_in_rect(image=inventory_path, rect=osrs_bot.win.cp_tabs[i], confidence = 0.35)
        if inv is not None:
            return i
    return None

