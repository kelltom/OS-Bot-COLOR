'''
A set of computer vision utilities for use with bots.

Image Search References:
- https://stackoverflow.com/questions/71302061/how-do-i-find-an-image-on-screen-ignoring-transparent-pixels/71302306#71302306
- https://stackoverflow.com/questions/61779288/how-to-template-match-a-simple-2d-shape-in-opencv/61780200#61780200
- https://stackoverflow.com/questions/74594219/template-matching-with-transparent-image-templates-using-opencv-python?noredirect=1#comment131674563_74594219
'''
from deprecated import deprecated
from easyocr import Reader
from PIL import Image
from typing import List, Union
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
        A BGR Numpy array representing the captured image.
    '''
    with mss.mss() as sct:
        monitor = rect.to_dict()
        res = np.array(sct.grab(monitor))
        return cv2.cvtColor(res, cv2.COLOR_RGB2BGR)

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

# --- Color Isolation ---
def isolate_colors(image: cv2.Mat, colors: List[List[int]]) -> cv2.Mat:
    '''
    Isolates ranges of colors within an image and saves a new resulting image.
    Args:
        image: The image to process.
        colors: A list of colors in [R, G, B] format.
    Returns:
        The image with the isolated colors (all shown as white).
    '''
    # Convert to BGR
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    # Change each color to RGB
    for i, color in enumerate(colors):
        colors[i] = np.array(color[::-1])
    # Generate masks for each color
    masks = [cv2.inRange(image, color, color) for color in colors]
    # Combine masks
    mask = masks[0]
    if len(masks) > 1:
        for i in range(1, len(masks)):
            mask = cv2.bitwise_or(mask, masks[i])
    save_image("isolate_colors.png", cv2.bitwise_and(image, image, mask=mask))
    return mask

# --- Image Search ---
def __imagesearcharea(template: cv2.Mat, im: cv2.Mat, confidence: float) -> Rectangle:
    '''
    Locates an image within another image.
    Args:
        template: The image to search for.
        im: The image to search in.
        confidence: The confidence level of the search in range 0 to 1, where 0 is a perfect match.
    Returns:
        A Rectangle outlining the found template inside the image.
    '''
    # Get template dimensions
    hh, ww = template.shape[:2]

    # Extract base image and alpha channel
    base = template[:,:,0:3]
    alpha = template[:,:,3]
    alpha = cv2.merge([alpha,alpha,alpha])

    correlation = cv2.matchTemplate(im, base, cv2.TM_SQDIFF_NORMED, mask=alpha)
    min_val, _, min_loc, _ = cv2.minMaxLoc(correlation)
    if min_val < confidence:
        return Rectangle.from_points(Point(min_loc[0], min_loc[1]), Point(min_loc[0]+ww, min_loc[1]+hh))
    return None

def search_img_in_rect(image: Union[cv2.Mat, str], rect: Rectangle, confidence=0.15) -> Rectangle:
    '''
    Searches for an image in a rectangle. This function works with images containing transparency (sprites).
    Args:
        image: The path to the image to search for, or the image itself.
        rect: The Rectangle to search in.
        confidence: The confidence level of the search in range 0 to 1, where 0 is a perfect match.
    Returns:
        A Rectangle outlining the found image relative to the container, or None.
    '''
    if isinstance(image, str):
        image = cv2.imread(image, cv2.IMREAD_UNCHANGED)
    im = screenshot(rect)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    if found_rect := __imagesearcharea(image, im, confidence):
        found_rect.left += rect.left
        found_rect.top += rect.top
        return found_rect
    else:
        return None

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
