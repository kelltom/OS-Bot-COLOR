'''
This file contains a collection of general purpose bot functions that work for any client type (Runelite or custom).

For more on ImageSearch, see: https://brokencode.io/how-to-easily-image-search-with-python/
For more on EasyOCR, see: https://github.com/JaidedAI/EasyOCR
For more on the anatomy of an OSRS interface, see: https://oldschool.runescape.wiki/w/Interface
For more on PyAutoGui, see: https://pyautogui.readthedocs.io/en/latest/
Guide for getting HSV mask colours: https://stackoverflow.com/a/48367205/16500201
For getting pixel coordinates on screen, use MPos: https://sourceforge.net/projects/mpos/
'''
import cv2
from easyocr import Reader
from PIL import Image, ImageGrab
from python_imagesearch.imagesearch import imagesearcharea, region_grabber
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


def capture_screen(rect: Rectangle) -> str:
    '''
    Captures a given Rectangle and saves it to a file.
    Args:
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
    return Point(x=pos[0] + rect.start.x + width/2,
                 y=pos[1] + rect.start.y + height/2)


# --- OCR ---
def get_text_in_rect(rect: Rectangle, is_low_res=False) -> str:
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
    Args:
        rect: The rectangle to search in.
        expected: List of strings that are expected within the rectangle area.
        blacklist: List of strings that, if found, will cause the function to return False.
    Returns:
        False if ANY blacklist words are found, else True if ANY expected text exists,
        and None if the text is irrelevant.
    '''
    # Screenshot the rectangle and load the image
    path = capture_screen(rect)
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
        if blacklist is not None:
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
    Args:
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
    # Save image and return path
    new_path = f"{TEMP_IMAGES}/low_res_text_processed.png"
    im.save(new_path)
    return new_path
