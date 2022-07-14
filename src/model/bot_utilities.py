'''
This file contains a collection of general purpose bot functions that are used by the bot classes.
MPos was used to acquire hardcoded coordinates.

For more on ImageSearch, see: https://brokencode.io/how-to-easily-image-search-with-python/
'''
from collections import namedtuple
import pathlib
import pyautogui as pag
import pygetwindow
from PIL import ImageGrab
from python_imagesearch.imagesearch import imagesearcharea, region_grabber
import time

# --- The path to this directory ---
PATH = pathlib.Path(__file__).parent.resolve()

# --- The path to the bot images directory ---
BOT_IMAGES = "./src/images/bot"

# --- Temporary screenshot filename ---
SCREENSHOT_NAME = "screenshot.png"

# --- Named Tuples ---
Point = namedtuple('Point', 'x y')
Rectangle = namedtuple('Rectangle', 'start end')

# --- Example usage of Point tuple ---
example_point = Point(x=100, y=100)

# --- Desired client position ---
WINDOW = Rectangle(start=(0, 0), end=(809, 534))


def capture_screen(rect: Rectangle):
    '''
    Captures a given Rectangle and saves it to a file.
    Parameters:
        x: The distance in pixels from the left side of the screen.
        y: The distance in pixels from the top of the screen.
    '''
    im = ImageGrab.grab(bbox=(rect.start[0], rect.start[1], rect.end[0], rect.end[1]))
    im.save(f"{PATH}/{SCREENSHOT_NAME}")


def search_img_in_rect(img_path: str, rect: Rectangle, conf: float = 0.8):
    '''
    Searches for an image in a rectangle.
    Parameters:
        rect: The rectangle to search in.
        img_path: The path to the image to search for.
    Returns:
        The coordinates of the image if found, otherwise None.
    '''
    im = region_grabber((rect.start[0], rect.start[1], rect.end[0], rect.end[1]))
    pos = imagesearcharea(img_path, rect.start[0], rect.start[1], rect.end[0], rect.end[1], conf, im)
    if pos == [-1, -1]:
        return None
    return pos


def search_text_in_rect(text: list, rect: Rectangle) -> bool:
    '''
    Searches for a text in a rectangle.
    Parameters:
        rect: The rectangle to search in.
        text: A list of text that is expected within the rectangle area.
    Returns:
        True if the text was found, otherwise False.
    '''


def setup_client_alora():
    '''
    Configures the client window of Alora.
    Experimental.
    '''
    # Move window to top left corner
    win = pygetwindow.getWindowsWithTitle('Alora')[0]
    win.moveTo(WINDOW.start[0], WINDOW.start[1])

    # Resize to desired size
    win.size = (WINDOW.end[0], WINDOW.end[1])

    # Search for settings button and click it
    time.sleep(1)
    pos = search_img_in_rect("./src/images/bot/cp_settings_icon.png", WINDOW)
    print(pos)
    if pos is None:
        print("it's none")
    else:
        pag.click(pos[0]+5, pos[1]+5)


setup_client_alora()
