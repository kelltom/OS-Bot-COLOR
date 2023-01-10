from pathlib import Path
from typing import Union

import cv2

from utilities.geometry import Point, Rectangle

# --- Paths to Image folders ---
__PATH = Path(__file__).parent.parent
IMAGES = __PATH.joinpath("images")
BOT_IMAGES = IMAGES.joinpath("bot")


def __imagesearcharea(template: Union[cv2.Mat, str, Path], im: cv2.Mat, confidence: float) -> Rectangle:
    """
    Locates an image within another image.
    Args:
        template: The image to search for.
        im: The image to search in.
        confidence: The confidence level of the search in range 0 to 1, where 0 is a perfect match.
    Returns:
        A Rectangle outlining the found template inside the image.
    """
    # If image doesn't have an alpha channel, convert it from BGR to BGRA
    if len(template.shape) < 3 or template.shape[2] != 4:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2BGRA)
    # Get template dimensions
    hh, ww = template.shape[:2]
    # Extract base image and alpha channel
    base = template[:, :, 0:3]
    alpha = template[:, :, 3]
    alpha = cv2.merge([alpha, alpha, alpha])

    correlation = cv2.matchTemplate(im, base, cv2.TM_SQDIFF_NORMED, mask=alpha)
    min_val, _, min_loc, _ = cv2.minMaxLoc(correlation)
    if min_val < confidence:
        return Rectangle.from_points(Point(min_loc[0], min_loc[1]), Point(min_loc[0] + ww, min_loc[1] + hh))
    return None


def search_img_in_rect(image: Union[cv2.Mat, str, Path], rect: Rectangle, confidence=0.15) -> Rectangle:
    """
    Searches for an image in a rectangle. This function works with images containing transparency (sprites).
    Args:
        image: The image to search for (can be a path or matrix).
        rect: The Rectangle to search in.
        confidence: The confidence level of the search in range 0 to 1, where 0 is a perfect match.
    Returns:
        A Rectangle outlining the found image relative to the container, or None.
    """
    if isinstance(image, str):
        image = cv2.imread(image, cv2.IMREAD_UNCHANGED)
    elif isinstance(image, Path):
        image = cv2.imread(str(image), cv2.IMREAD_UNCHANGED)
    im = rect.screenshot()
    if found_rect := __imagesearcharea(image, im, confidence):
        found_rect.left += rect.left
        found_rect.top += rect.top
        return found_rect
    else:
        return None
