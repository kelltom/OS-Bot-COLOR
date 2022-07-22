'''
Work in progress.

This file contains a collection of general purpose bot functions that are used by the bot classes.
MPos was used to acquire hardcoded coordinates.

For more on ImageSearch, see: https://brokencode.io/how-to-easily-image-search-with-python/
For more on EasyOCR, see: https://github.com/JaidedAI/EasyOCR
For more on the anatomy of an OSRS interface, see: https://oldschool.runescape.wiki/w/Interface
For more on PyAutoGui, see: https://pyautogui.readthedocs.io/en/latest/
Guide for getting HSV mask colours: https://stackoverflow.com/a/48367205/16500201
'''

import cv2
from easyocr import Reader
import numpy as np
from PIL import Image, ImageGrab
import pyautogui as pag
import pygetwindow
from python_imagesearch.imagesearch import imagesearcharea, region_grabber
import time
from typing import NamedTuple
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# --- Paths to Image folders ---
TEMP_IMAGES = "./src/images/temp"
BOT_IMAGES = "./src/images/bot"

# --- Custom Named Tuples ---
# Simplifies accessing points and areas on the screen by name.
Point = NamedTuple("Point", x=int, y=int)
Rectangle = NamedTuple('Rectangle', start=Point, end=Point)

# --- Notable Colour Ranges (HSV lower, upper) ---
NPC_BLUE = ((90, 100, 255), (100, 255, 255))
NPC_HP_GREEN = ((40, 100, 255), (70, 255, 255))
NPC_HP_RED = ((0, 255, 255), (20, 255, 255))

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

# --- Control Panel (CP) ---
h1 = 213  # y-axis pixels to top of cp
h2 = 510  # y-axis pixels to bottom of cp
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
    time.sleep(0.2)
    pag.moveTo(orb_prayer.x, orb_prayer.y)
    time.sleep(0.2)
    pag.moveTo(orb_spec.x, orb_spec.y)
    time.sleep(0.2)
    pag.moveTo(cp_combat.x, cp_combat.y)
    time.sleep(0.2)
    pag.moveTo(cp_inventory.x, cp_inventory.y)
    time.sleep(0.2)
    pag.moveTo(cp_equipment.x, cp_equipment.y)
    time.sleep(0.2)
    pag.moveTo(cp_prayer.x, cp_prayer.y)
    time.sleep(0.2)
    pag.moveTo(cp_spellbook.x, cp_spellbook.y)
    time.sleep(0.2)
    pag.moveTo(cp_logout.x, cp_logout.y)
    time.sleep(0.2)
    pag.moveTo(cp_settings.x, cp_settings.y)
    time.sleep(0.2)
    for row in inventory_slots:
        for slot in row:
            pag.moveTo(slot.x, slot.y)
            time.sleep(0.2)
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
    path = f"{TEMP_IMAGES}/screenshot.png"
    im.save(path)
    return path


# --- Image Search ---
def search_img_in_rect(img_path: str, rect: Rectangle, conf: float = 0.8) -> Point:
    '''
    Searches for an image in a rectangle.
    Parameters:
        img_path: The path to the image to search for.
        rect: The rectangle to search in.
        conf: The confidence level of the search.
    Returns:
        The coordinates of the center of the image if found (as a Point) relative to display,
        otherwise None.
    '''
    width, height = Image.open(img_path).size
    im = region_grabber((rect.start.x, rect.start.y, rect.end.x, rect.end.y))
    pos = imagesearcharea(img_path, rect.start.x, rect.start.y, rect.end.x, rect.end.y, conf, im)
    if pos == [-1, -1]:
        return None
    return Point(x=pos[0] + rect.start.x + width/2,
                 y=pos[1] + rect.start.y + height/2)


# --- NPC Detection ---
def attack_nearest_tagged() -> bool:
    '''
    Attacks the nearest tagged NPC that is not already in combat.
    Returns:
        True if an NPC attack was attempted, False otherwise.
    '''
    path_game_view = __capture_screen(rect_game_view)
    # Isolate colors in image
    path_npcs, path_hp_bars = __isolate_tagged_NPCs_at(path_game_view)
    # Locate potential NPCs in image by determining contours
    contours = __get_contours(path_npcs)
    # Get center pixels of non-combatting NPCs
    centers = []
    img_bgr = cv2.imread(path_hp_bars)
    for cnt in contours:
        try:
            center, top = __get_contour_positions(cnt)
        except Exception:
            print("Cannot find moments of contour. Disregarding...")
            continue
        if not __in_combat(top, img_bgr):
            centers.append((center.x, center.y))
    if not centers:
        print("No tagged NPCs found.")
        return False
    # Attack nearest NPC
    dims = img_bgr.shape  # (height, width, channels)
    nearest = __get_nearest_point(Point(int(dims[1] / 2), int(dims[0] / 2)), centers)
    pag.click(nearest.x + rect_game_view.start.x, nearest.y + rect_game_view.start.y)
    print("Attacked nearest tagged NPC.")
    return True


def __get_contours(path: str) -> list:
    '''
    Gets the contours of an image.
    Parameters:
        path: The path to the image.
    Returns:
        A list of contours.
    '''
    img = cv2.imread(path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return contours


def __get_contour_positions(contour) -> tuple:
    '''
    Gets the center and top pixel positions of a contour.
    Parameters:
        contour: The contour to get the positions of.
    Returns:
        A tuple of the center and top pixel positions.
    '''
    moments = cv2.moments(contour)
    center_x = int(moments["m10"] / moments["m00"])
    center_y = int(moments["m01"] / moments["m00"])
    top_x, top_y = contour[contour[..., 1].argmin()][0]
    return Point(center_x, center_y), Point(top_x, top_y)


def __get_nearest_point(point: Point, points: list) -> Point:
    '''
    Returns the nearest point in a list of (x, y) coordinates.
    Parameters:
        point: The point to compare to.
        points: The list of (x, y) coordinates to compare.
    Returns:
        The closest point in the list.
    '''
    point = (point.x, point.y)
    nodes = np.asarray(points)
    dist_2 = np.sum((nodes - point) ** 2, axis=1)
    p = np.argmin(dist_2)
    return Point(points[p][0], points[p][1])


def __in_combat(point: Point, im) -> bool:
    '''
    Given a point and CV image of HP bars, determine if the NPC's point has a neighbouring HP bar.
    Parameters:
        point: The top point of a contour (NPC).
        im: A BGR CV image containing only HP bars.
    Returns:
        True if the point is in combat, False otherwise.
    '''
    # For 10 pixels above/below the point, check if the pixel is not black.
    for i in range(-10, 10):
        try:
            (b, g, r) = im[point.y + i, point.x]
        except Exception:
            continue
        if (b, g, r) != (0, 0, 0):
            print("Detected NPC in combat.")
            return True
    return False


def __isolate_tagged_NPCs_at(path: str) -> str:
    '''
    Isolates tagged NPCs, HP bars and hitsplats in an image.
    Parameters:
        path: The path to the image to isolate colors.
    Returns:
        The paths to an image with only tagged NPCs, and an image with only HP bars.
    '''
    img = cv2.imread(path)
    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image to get only blue color
    mask1 = cv2.inRange(hsv, NPC_BLUE[0], NPC_BLUE[1])
    only_blue = cv2.bitwise_and(img, img, mask=mask1)
    blue_path = f"{TEMP_IMAGES}/only_blue.png"
    cv2.imwrite(blue_path, only_blue)

    # Threshold the original image for green and red
    mask2 = cv2.inRange(hsv, NPC_HP_GREEN[0], NPC_HP_GREEN[1])
    mask3 = cv2.inRange(hsv, NPC_HP_RED[0], NPC_HP_RED[1])
    mask = cv2.bitwise_or(mask2, mask3)
    only_color = cv2.bitwise_and(img, img, mask=mask)
    # Save the image and return path
    color_path = f"{TEMP_IMAGES}/only_green_red.png"
    cv2.imwrite(color_path, only_color)
    return blue_path, color_path


# --- OCR ---
def get_text_in_rect(rect: Rectangle, is_low_res=False) -> str:
    '''
    Fetches text in a Rectangle.
    Parameters:
        rect: The rectangle to search in.
        is_low_res: Whether the text within the rectangle is low resolution/pixelated.
    Returns:
        The text found in the rectangle, space delimited.
    '''
    # Screenshot the rectangle and load the image
    path = __capture_screen(rect)

    if is_low_res:
        path = __preprocess_low_res_text_at(path)

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


def search_text_in_rect(rect: Rectangle, expected: list, blacklist: list = None) -> bool:
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


def __preprocess_low_res_text_at(path: str) -> str:
    '''
    Preprocesses an image at a given path and saves it back to the same path.
    This function improves text clarity for OCR by upscaling, antialiasing, and isolating text.
    Note:
        Only use for low-resolution images with pixelated text and a solid background.
    Parameters:
        path: The path to the image to preprocess.
    Returns:
        The path to the processed image.
    Reference: https://stackoverflow.com/questions/50862125/how-to-get-better-accurate-results-with-ocr-from-low-resolution-images
    '''
    im = Image.open(path)
    width, height = im.size
    new_size = width*6, height*6
    im = im.resize(new_size, Image.Resampling.LANCZOS)
    im = im.convert('L')  # Convert to grayscale
    intensity = 120  # Between 0 and 255, every pixel less than this value will be set to 0
    im = im.point(lambda x: 0 if x < intensity else 255, '1')
    # Save image and return path
    new_path = f"{TEMP_IMAGES}/low_res_text_processed.png"
    im.save(new_path)
    return new_path


# --- Setup Functions ---
def setup_client_alora():
    '''
    Configures the client window of Alora.
    Alora private server is used for testing: https://www.alora.io/
    '''
    # Get reference to the client window
    try:
        win = pygetwindow.getWindowsWithTitle('Alora')[0]
        win.activate()
    except Exception:
        print("Error: Could not find Alora window.")
        return

    # Set window to large initially
    temp_win = Rectangle(Point(0, 0), Point(1200, 1000))
    win.moveTo(0, 0)
    win.size = (temp_win.end[0], temp_win.end[1])
    time.sleep(1)

    # Ensure user is logged out of Runelite
    rl_login_icon = search_img_in_rect(f"{BOT_IMAGES}/runelite_logout.png", temp_win, conf=0.9)
    if rl_login_icon is not None:
        pag.click(rl_login_icon.x, rl_login_icon.y)
        time.sleep(0.2)
        pag.press('enter')
        time.sleep(1)

    # Ensure Runelite Settings pane is closed
    settings_icon = search_img_in_rect(f"{BOT_IMAGES}/runelite_settings_selected.png", temp_win)
    if settings_icon is not None:
        pag.click(settings_icon.x, settings_icon.y)
        time.sleep(1)

    # Move and resize to desired position
    win.moveTo(0, 0)
    win.size = (window.end.x, window.end.y)
    time.sleep(1)


# Experimental code below -- this file is a work in progress

setup_client_alora()

# # Search for the settings icon on the OSRS control panel and return its position.
# pos = search_img_in_rect(f"{BOT_IMAGES}/cp_settings_icon.png", window)
# print(f"Settings icon from Window: {pos}")
# pag.moveTo(pos.x, pos.y)

# # Returns true if player is fishing, false if they are not
# res = search_text_in_rect(rect_current_action, ["fishing"], ["NOT", "nt"])
# print(res)

# # Returns the numeric value of the player's HP by using OCR on the area next to
# # the HP orb.
# res = get_text_in_rect(rect_hp, is_low_res=True)
# print(res)


attack_nearest_tagged()
