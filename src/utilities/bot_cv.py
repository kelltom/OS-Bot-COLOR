'''
A set of computer vision utilities for use with bots.
'''
from deprecated import deprecated
from easyocr import Reader
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
    TODO: Consider moving to Rectangle as class method, since only Rectangles are ever screenshotted.
    Args:
        rect: Rectangle area to capture.
    Returns:
        A BGR Numpy array representing the captured image.
    '''
    with mss.mss() as sct:
        monitor = rect.to_dict()
        res = np.array(sct.grab(monitor))
        res = cv2.cvtColor(res, cv2.COLOR_RGB2BGR)
        if rect.subtract_list:
            for area in rect.subtract_list:
                res[area['top']:area['top']+area['height'], area['left']:area['left']+area['width']] = 0
        return res

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
