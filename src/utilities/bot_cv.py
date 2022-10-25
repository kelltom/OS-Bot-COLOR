'''
A set of computer vision utilities for use with bots.
'''
from deprecated import deprecated
from easyocr import Reader
from PIL import Image
from utilities.geometry import Point, Rectangle
import cv2
import mss
import numpy as np
import pathlib
import re

# --- Paths to Image folders ---
PATH = pathlib.Path(__file__).parent.parent.resolve()
TEMP_IMAGES = f"{PATH}/images/temp"
BOT_IMAGES = f"{PATH}/images/bot"

# --- Screen Capture ---
def screenshot(rect: Rectangle) -> cv2.Mat:
    '''
    Captures given Rectangle without saving into a file.
    Args:
        rect: Rectangle area to capture.
    Returns:
        A BGRA Numpy array representing the captured image.
    '''
    with mss.mss() as sct:
        monitor = rect.to_dict()
        return np.array(sct.grab(monitor))

def save_image(filename, im) -> str:
    '''
    Saves an image to the temporary image directory.
    Args:
        filename: The filename to save the image as.
        im: The image to save (cv2.Mat).
    Returns:
        The path to the saved image.
    Example:
        path = __save_image('screenshot.png', im)
    '''
    path = f"{TEMP_IMAGES}/{filename}"
    cv2.imwrite(path, im)
    return path

# --- Image Search ---
def __imagesearcharea(template, im, precision=0.8):
    '''
    Locates an image within another image.
    Args:
        template: The path to the image to search for.
        im: The image to search in (MSS ScreenShot or cv2.Mat).
        precision: The precision of the search.
    '''
    img_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(template, 0)
    if template is None:
        raise FileNotFoundError(f'Image file not found: {template}')

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    return [-1, -1] if max_val < precision else max_loc

def search_img_in_rect(img_path, rect: Rectangle, precision=0.8) -> Point:
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
    im = screenshot(rect)
    pos = __imagesearcharea(img_path, im, precision)

    if pos == [-1, -1]:
        return None
    return Point(x=int(pos[0] + width / 2), y=int(pos[1] + height / 2))

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

@deprecated(version='0.0.1', reason="get_text_in_rect may not work as expected. New solution in development.")
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
    image = screenshot(rect)
    if is_low_res:
        image = __preprocess_low_res(image)
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
    image = screenshot(rect)
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
def __preprocess_low_res(image: cv2.Mat) -> cv2.Mat:
    '''
    Preprocesses an image at a given path and saves it back to the same path.
    This function improves text clarity for OCR by upscaling and isolating text.
    Note:
        Only use for low-resolution images with pixelated text and a solid background.
    Args:
        image: The image to preprocess.
    Returns:
        The upscaled image.
    '''
    height, width, _ = image.shape
    new_size = (width*6, height*6)
    image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(image, 120, 255, cv2.THRESH_TOZERO)
    return thresh

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
