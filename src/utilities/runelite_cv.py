'''
A set of computer vision utilities for use with RuneLite-based bots.
'''

import cv2
import utilities.bot_cv as bcv
from utilities.bot_cv import Point
from typing import NamedTuple, List


# --- Custom Named Tuple ---
# Simplifies referencing color ranges by name.
# See runelite_bot.py for example usage.
Color = NamedTuple("Color", hsv_upper=tuple, hsv_lower=tuple)


def get_contours(path: str) -> list:
    '''
    Gets the contours of an image.
    Args:
        path: The path to the image.
        thresh: The threshold to use for the image.
    Returns:
        A list of contours.
    '''
    img = cv2.imread(path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = 1
    _, thresh = cv2.threshold(img_gray, thresh, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return contours


def get_contour_positions(contour) -> tuple:
    '''
    Gets the center and top pixel positions of a contour.
    Args:
        contour: The contour to get the positions of.
    Returns:
        A center and top pixel positions as Points.
    '''
    moments = cv2.moments(contour)
    center_x = int(moments["m10"] / moments["m00"])
    center_y = int(moments["m01"] / moments["m00"])
    top_x, top_y = contour[contour[..., 1].argmin()][0]
    return Point(center_x, center_y), Point(top_x, top_y)


def isolate_colors(path: str, colors: List[Color], filename: str) -> str:
    '''
    Isolates ranges of colors within an image and saves a new resulting image.
    Args:
        path: The path to the image to isolate colors.
        colors: A list of rcv Colors.
        filename: The name of the file to be saved in the temp images folder.
    Returns:
        The path to an image with only the desired color(s).
    '''
    img = cv2.imread(path)
    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Generate masks for each color
    masks = [cv2.inRange(hsv, color[0], color[1]) for color in colors]
    # Combine masks
    mask = masks[0]
    if len(masks) > 1:
        for i in range(1, len(masks)):
            mask = cv2.bitwise_or(mask, masks[i])
    masked_image = cv2.bitwise_and(img, img, mask=mask)
    # Save the image and return path
    color_path = f"{bcv.TEMP_IMAGES}/{filename}.png"
    cv2.imwrite(color_path, masked_image)
    return color_path


def is_point_obstructed(point: Point, im, span: int = 20) -> bool:
    '''
    This function determines if there are non-black pixels in an image around a given point.
    This is useful for determining if an NPC is in combat (E.g., given the mid point of an NPC contour
    and a masked image only showing HP bars, determine if the NPC has an HP bar around the contour).
    Args:
        point: The top point of a contour (NPC).
        im: A BGR CV image containing only HP bars.
        span: The number of pixels to search around the given point.
    Returns:
        True if the point is obstructed, False otherwise.
    '''
    try:
        crop = im[point.y-span:point.y+span, point.x-span:point.x+span]
        mean = crop.mean(axis=(0, 1))
        return str(mean) != "[0. 0. 0.]"
    except Exception:
        print("Cannot crop image. Disregarding...")
        return True
