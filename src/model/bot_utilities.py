'''
This file contains a collection of general purpose bot functions that are used by the bot classes.
MPos was used to acquire hardcoded coordinates.

For more on ImageSearch, see: https://brokencode.io/how-to-easily-image-search-with-python/
'''
from collections import namedtuple
import pathlib
import pyautogui as pag
import pygetwindow
from PIL import Image, ImageGrab
from python_imagesearch.imagesearch import imagesearch, imagesearcharea, region_grabber
import time

# --- The path to this directory ---
PATH = pathlib.Path(__file__).parent.resolve()

# --- Temporary screenshot filename ---
SCREENSHOT_NAME = "screenshot.png"

# --- Named Tuples ---
Point = namedtuple('Point', 'x y')
Rectangle = namedtuple('Rectangle', 'start end')


example_point = Point(x=100, y=100)
WINDOW = Rectangle(start=(0, 0), end=(850, 800))


# TODO: Figure out if I need this
def capture_screen(left, top, right, bottom):
    '''
    Captures the screen and saves it to a file.
    Parameters:
        x: The distance in pixels from the left side of the screen.
        y: The distance in pixels from the top of the screen.
    '''
    # capture the screen
    im = ImageGrab.grab(bbox=(left, top, right, bottom))
    im.save(f"{PATH}/{SCREENSHOT_NAME}")


def search_img_in_rect(rect: Rectangle, img_path: str, conf: float = 0.8):
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


def setup_client_alora():
    # Move window to top left corner
    win = pygetwindow.getWindowsWithTitle('Alora')[0]
    win.moveTo(WINDOW.start[0], WINDOW.start[1])

    # Resize to desired size
    win.size = (WINDOW.end[0], WINDOW.end[1])

    # Capture window
    time.sleep(1)
    pos = search_img_in_rect(WINDOW, "./src/images/bot/cp_settings_icon.png")
    print(pos)
    if pos is None:
        print("it's none")
    else:
        pag.click(pos[0]+5, pos[1]+5)


setup_client_alora()
