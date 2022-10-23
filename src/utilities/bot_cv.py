'''
A set of computer vision utilities for use with bots.
'''

import cv2
import mss
import numpy as np
from easyocr import Reader
import pathlib
from PIL import Image, ImageGrab
from python_imagesearch.imagesearch import imagesearcharea, region_grabber
import re
from typing import NamedTuple


# --- Paths to Image folders ---
PATH = pathlib.Path(__file__).parent.parent.resolve()
TEMP_IMAGES = f"{PATH}/images/temp"
BOT_IMAGES = f"{PATH}/images/bot"

# --- Custom Named Tuples ---
# Simplifies accessing points and areas on the screen by name.
Point = NamedTuple("Point", x=int, y=int)
Rectangle = NamedTuple('Rectangle', start=Point, end=Point)


# --- Screen Capture ---
ss = mss.mss()


def grab_screen(rect: Rectangle):
    '''
    Captures given Rectangle without saving into a file.
    Args:
        x and y is start of the of the resolution.
        xx: The width.
        yy: The height.
    Returns:
        RGB array image of the screen.
    '''
    monitor = {rect.start.y, rect.start.x, rect.end.x, rect.end.y}
    image = ss.grab(monitor)
    image = np.array(image.raw)
    image.shape = (yy, xx, 4)
    image = image[..., :3]
    return image


def capture_screen(rect: Rectangle) -> str:
    '''
    Captures a given Rectangle and saves it to a file.
    Args:
        rect: The Rectangle area to capture.
    Returns:
        The path to the saved image.
    '''
    im = ImageGrab.grab(bbox=(rect.start.x, rect.start.y, rect.end.x, rect.end.y))
    return __save_image('/screenshot.png', im)


def __save_image(filename, im):
    '''
    Saves an image to the temporary image directory.
    Args:
        filename: The filename to save the image as.
        im: The image to save.
    Returns:
        The path to the saved image.
    Example:
        path = __save_image('/screenshot.png', im)
    '''
    path = f"{TEMP_IMAGES}{filename}"
    im.save(path)
    return path


# --- Image Search ---
def search_img_in_rect(img_path: str, rect: Rectangle, conf: float = 0.8) -> Point:
    '''
    Searches for an image in a rectangle.
    Args:
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
    return Point(x=int(pos[0] + rect.start.x + width/2),
                 y=int(pos[1] + rect.start.y + height/2))


# --- OCR ---
def get_numbers_in_rect(rect: Rectangle, is_low_res=False) -> list:
    """
    Fetches numbers in a Rectangle.
    Args:
        rect: The rectangle to search in.
        is_low_res: Whether the text within the rectangle is low resolution/pixelated.
    Returns:
        The distinct numbers found in the rectangle.
        If no numbers were found, returns None.
    """
    text = get_text_in_rect(rect, is_low_res)
    string_nums = re.findall('\d+', text)  # TODO: Fix warning
    res = [int(numeric_string) for numeric_string in string_nums]
    return res or None


def get_text_in_rect(rect: Rectangle, is_low_res=False) -> str:
    # sourcery skip: class-extract-method
    '''
    Fetches text in a Rectangle.
    Args:
        rect: The rectangle to search in.
        is_low_res: Whether the text within the rectangle is low resolution/pixelated.
    Returns:
        The text found in the rectangle, space delimited.
    '''
    # Screenshot the rectangle and load the image
    path = capture_screen(rect)
    if is_low_res:
        path = __preprocess_low_res_text_at(path)
    image = cv2.imread(path)
    # OCR the input image using EasyOCR
    reader = Reader(['en'], gpu=-1)
    res = reader.readtext(image)
    return "".join(f"{_text} " for _, _text, _ in res)


def search_text_in_rect(rect: Rectangle, expected: list, blacklist: list = None) -> bool:
    """
    Searches for text in a Rectangle.
    Args:
        rect: The rectangle to search in.
        expected: List of strings that are expected within the rectangle area.
        blacklist: List of strings that, if found, will cause the function to return False.
    Returns:
        False if ANY blacklist words are found, else True if ANY expected text exists,
        and None if the text is irrelevant.
    """
    path = capture_screen(rect)
    image = cv2.imread(path)
    reader = Reader(['en'], gpu=-1)
    res = reader.readtext(image)
    word_found = False
    for _, text, _ in res:
        if text is None or text == "":
            return None
        text = text.lower()
        print(f"OCR Result: {text}")
        if blacklist is not None:
            _result, _word = __any_in_str(blacklist, text)
            if _result:
                print(f"Blacklist word found: {_word}")
                return False
        if not word_found:
            _result, _word = __any_in_str(expected, text)
            if _result:
                word_found = True
                print(f"Expected word found: {_word}")
    return True if word_found else None


# --- Pre-processing ---
def __preprocess_low_res_text_at(path: str) -> str:
    '''
    Preprocesses an image at a given path and saves it back to the same path.
    This function improves text clarity for OCR by upscaling, antialiasing, and isolating text.
    Note:
        Only use for low-resolution images with pixelated text and a solid background.
    Args:
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
    return __save_image('/low_res_text_processed.png', im)


# --- Misc ---
def __any_in_str(words: list, str: str) -> bool:
    '''
    Checks if any of the words in the list are found in the string.
    Args:
        words: The list of words to search for.
        str: The string to search in.
    Returns:
        True if any of the words are found (also returns the word found), else False.
    '''
    return next(((True, word) for word in words if word.lower() in str), (False, None))
