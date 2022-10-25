'''
A set of computer vision utilities for use with RuneLite-based bots.
'''
from utilities.geometry import Point
from typing import List, NamedTuple
import cv2
import utilities.bot_cv as bcv

# --- Custom Named Tuple ---
# Simplifies referencing color ranges by name.
# See runelite_bot.py for example usage.
Color = NamedTuple("Color", hsv_upper=tuple, hsv_lower=tuple)

def get_contours(image: cv2.Mat) -> list:
    '''
    Gets the contours of an image.
    Args:
        image: The image to process (assume color has been isolated).
    Returns:
        A list of contours.
    '''
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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

def isolate_colors(image: cv2.Mat, colors: List[Color]) -> cv2.Mat:
    '''
    Isolates ranges of colors within an image and saves a new resulting image.
    Args:
        image: The image to process.
        colors: A list of rcv Colors.
    Returns:
        The image with the isolated colors.
    '''
    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Generate masks for each color
    masks = [cv2.inRange(hsv, color[0], color[1]) for color in colors]
    # Combine masks
    mask = masks[0]
    if len(masks) > 1:
        for i in range(1, len(masks)):
            mask = cv2.bitwise_or(mask, masks[i])
    #bcv.save_image("isolated.png", masked_image)
    return cv2.bitwise_and(image, image, mask=mask)

def is_point_obstructed(point: Point, im: cv2.Mat, span: int = 20) -> bool:
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
