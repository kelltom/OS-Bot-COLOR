'''
Work in progress.

This file contains a collection of general purpose bot functions that are used by the bot classes.
MPos was used to acquire hardcoded coordinates.

For more on ImageSearch, see: https://brokencode.io/how-to-easily-image-search-with-python/
For more on EasyOCR, see: https://github.com/JaidedAI/EasyOCR
For more on the anatomy of an OSRS interface, see: https://oldschool.runescape.wiki/w/Interface
For more on PyAutoGui, see: https://pyautogui.readthedocs.io/en/latest/
'''
import cv2
from easyocr import Reader
import pathlib
from PIL import Image, ImageGrab
import pyautogui as pag
import pygetwindow
from python_imagesearch.imagesearch import imagesearcharea, region_grabber
import time
from typing import NamedTuple
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# --- The path to this directory ---
PATH = pathlib.Path(__file__).parent.resolve()

# --- The path to the bot images directory ---
IMAGES_PATH = "./src/images/bot"

# --- Custom Named Tuples ---
# Simplifies accessing points and areas on the screen by name.
Point = NamedTuple("Point", x=int, y=int)
Rectangle = NamedTuple('Rectangle', start=Point, end=Point)

# --- Desired client position ---
# Size and position of the smallest possible fixed OSRS client in top left corner of screen.
window = Rectangle(start=Point(0, 0), end=Point(809, 534))

# ------- Rects of Interest -------
rect_current_action = Rectangle(start=Point(10, 52), end=Point(171, 93))  # combat/skilling plugin text
rect_game_view = Rectangle(start=Point(9, 31), end=Point(517, 362))  # gameplay area
rect_hp = Rectangle(start=Point(526, 80), end=Point(552, 100))  # contains HP text value
# TODO: Add more rectangles of interest (prayer, spec, etc.)

# ------- Points of Interest -------
# --- Orbs ---
orb_compass = Point(x=571, y=48)
orb_prayer = Point(x=565, y=119)
orb_spec = Point(x=597, y=178)

# --- Control Panel ---
h1 = 213  # top row height
h2 = 510  # bottom row height
cp_combat = Point(x=545, y=h1)
cp_inventory = Point(x=646, y=h1)
cp_equipment = Point(x=678, y=h1)
cp_prayer = Point(x=713, y=h1)
cp_spellbook = Point(x=744, y=h1)
cp_logout = Point(x=646, y=h2)
cp_settings = Point(x=680, y=h2)


# --- Inventory Slots ---
def __get_inventory_slots() -> list:
    '''
    Returns a 2D list of the inventory slots represented as Points.
    Inventory is 7x4.
    '''
    inv = []
    curr_y = 253
    for _ in range(7):
        curr_x = 583  # reset x
        row = []
        for _ in range(4):
            row.append(Point(x=curr_x, y=curr_y))
            curr_x += 42  # x delta
        inv.append(row)
        curr_y += 36  # y delta
    return inv


inventory_slots = __get_inventory_slots()


def __visit_points():
    '''
    Moves mouse to each defined point of interest.
    TODO: Remove. This is just for testing.
    '''
    pag.moveTo(orb_compass.x, orb_compass.y)
    time.sleep(0.5)
    pag.moveTo(orb_prayer.x, orb_prayer.y)
    time.sleep(0.5)
    pag.moveTo(orb_spec.x, orb_spec.y)
    time.sleep(0.5)
    pag.moveTo(cp_combat.x, cp_combat.y)
    time.sleep(0.5)
    pag.moveTo(cp_inventory.x, cp_inventory.y)
    time.sleep(0.5)
    pag.moveTo(cp_equipment.x, cp_equipment.y)
    time.sleep(0.5)
    pag.moveTo(cp_prayer.x, cp_prayer.y)
    time.sleep(0.5)
    pag.moveTo(cp_spellbook.x, cp_spellbook.y)
    time.sleep(0.5)
    pag.moveTo(cp_logout.x, cp_logout.y)
    time.sleep(0.5)
    pag.moveTo(cp_settings.x, cp_settings.y)
    time.sleep(0.5)
    for row in inventory_slots:
        for slot in row:
            pag.moveTo(slot.x, slot.y)
            time.sleep(0.5)
    pag.moveTo(inventory_slots[2][1].x, inventory_slots[2][1].y)


def __capture_screen(rect: Rectangle) -> str:
    '''
    Captures a given Rectangle and saves it to a file.
    Parameters:
        rect: The Rectangle area to capture.
    Returns:
        The path to the saved image.
    '''
    im = ImageGrab.grab(bbox=(rect.start.x, rect.start.y, rect.end.x, rect.end.y))
    path = f"{PATH}/screenshot.png"
    im.save(path)
    return path


# --- Image Search ---
def search_img_in_rect(img_path: str, rect: Rectangle, conf: float = 0.8) -> Point:
    '''
    Searches for an image in a rectangle.
    Parameters:
        rect: The rectangle to search in.
        img_path: The path to the image to search for.
        conf: The confidence level of the search.
    Returns:
        The coordinates of the image if found (as a Point), otherwise None.
    '''
    im = region_grabber((rect.start.x, rect.start.y, rect.end.x, rect.end.y))
    pos = imagesearcharea(img_path, rect.start.x, rect.start.y, rect.end.x, rect.end.y, conf, im)
    if pos == [-1, -1]:
        return None
    return Point(x=pos[0], y=pos[1])


# --- OCR ---
def search_text_in_rect(rect: Rectangle, expected: list, blacklist: list = None,) -> bool:
    '''
    Searches for text in a Rectangle.
    Parameters:
        rect: The rectangle to search in.
        expected: List of strings that are expected within the rectangle area.
        blacklist: List of strings that, if found, will cause the function to return False.
    Returns:
        False if ANY blacklist words are found, else True if ANY expected text exists,
        and None if the text is irrelevant.
    '''
    # Screenshot the rectangle and load the image
    path = __capture_screen(rect)
    image = cv2.imread(path)

    # OCR the input image using EasyOCR
    reader = Reader(['en'], gpu=-1)
    res = reader.readtext(image)

    # Loop through results
    word_found = False
    for (_, text, _) in res:
        if text is None or text == "":
            return None
        text = text.lower()
        print(f"OCR Result: {text}")
        # If any strings in blacklist are found in text, return false
        _result, _word = __any_in_str(blacklist, text)
        if _result:
            print(f"Blacklist word found: {_word}")
            return False
        # If any strings in expected are found in text, set flag true
        if not word_found:
            _result, _word = __any_in_str(expected, text)
            if _result:
                word_found = True
                print(f"Expected word found: {_word}")
    if word_found:
        return True
    return None


def get_text_in_rect(rect: Rectangle, is_low_res=False) -> str:
    '''
    Fetches text in a Rectangle.
    Parameters:
        rect: The rectangle to search in.
        is_low_res: Whether the text within the rectangle is low resolution/pixelated.
    Returns:
        The text found in the rectangle.
    '''
    # Screenshot the rectangle and load the image
    path = __capture_screen(rect)

    if is_low_res:
        __preprocess_low_res_text_at(path)

    image = cv2.imread(path)

    # OCR the input image using EasyOCR
    reader = Reader(['en'], gpu=-1)
    res = reader.readtext(image)

    # Loop through results
    text = ""
    for (_, _text, _) in res:
        if _text is None or _text == "":
            return None
        text += f"{_text} "
    return text


def __preprocess_low_res_text_at(path: str):
    '''
    Preprocesses an image at a given path and saves it back to the same path.
    This function improves text clarity for OCR by upscaling, antialiasing, and isolating text.
    Note:
        Only use for low-resolution images with pixelated text and a solid background.
    Parameters:
        path: The path to the image to preprocess.
    Reference: https://stackoverflow.com/questions/50862125/how-to-get-better-accurate-results-with-ocr-from-low-resolution-images
    '''
    im = Image.open(path)
    width, height = im.size
    new_size = width*6, height*6
    im = im.resize(new_size, Image.Resampling.LANCZOS)
    im = im.convert('L')
    im = im.point(lambda x: 0 if x < 120 else 255, '1')
    im.save(path)


def __any_in_str(words: list, str: str) -> bool:
    '''
    Checks if any of the words in the list are found in the string.
    Parameters:
        words: The list of words to search for.
        str: The string to search in.
    Returns:
        True if any of the words are found (also returns the word found), else False.
    '''
    return next(((True, word) for word in words if word.lower() in str), (False, None))


def setup_client_alora():
    '''
    Configures the client window of Alora.
    Alora private server is used for testing: https://www.alora.io/
    '''
    # Move window to top left corner
    try:
        win = pygetwindow.getWindowsWithTitle('Alora')[0]
    except Exception:
        print("Error: Could not find Alora window.")
        return

    # Move and resize to desired position
    win.moveTo(window.start.x, window.start.y)
    win.size = (window.end.x, window.end.y)

    # Search for settings button and click it
    time.sleep(1)


# Experimental code below -- this file is a work in progress

setup_client_alora()

# Search for the settings icon on the OSRS control panel and return its position.
pos = search_img_in_rect(f"{IMAGES_PATH}/cp_settings_icon.png", window)
print(pos)

# Returns true if player is fishing, false if they are not
res = search_text_in_rect(rect_current_action, ["fishing"], ["NOT", "nt"])
print(res)

# Returns the numeric value of the player's HP by using OCR on the area next to
# the HP orb.
res = get_text_in_rect(rect_hp, is_low_res=True)
print(res)
