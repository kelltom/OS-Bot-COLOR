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
    
    
def object_list(color, trim=4, trim_iter=1):
    '''
    This function first grabs a screenshot of the screen then mask the color of the objects highlighted.
    Afterwards it finds all the countours from the mask image using Morphological Transformations to get rid of the
    of the border width in the runelite plugin settings. It has two options in the runelite highlighting plugin to work properly,
    you can have border width of 4 or greater and highlight only clickboxes or you can have 1 border and highlight outline only.
    Args:
        color: The color of the object highlight in a RGB list format([0, 0, 0])
        trim: The trim to cut off the border of the hightlighted object.
        trim_iter: The amount of times to trim.
    Returns:
        Returns a list of all the hightlighted objects. Each object is a list, first index is the center of the object, second is the
        object is width and height, third is the x and y axis of the start box of the object in the left top corner, lastly
        is all the click able pixel points in the object.
    '''
    image = bcv.grab_screen()
    main_list = []
    rgb = np.array(color[::-1])
    mask = cv2.inRange(image, rgb, rgb)
    count = np.count_nonzero(mask == 255)
    if count:
        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        for objects in range(len(contours)):
            if len(contours[objects]) > 10:
                mask_copy = mask.copy()
                cv2.drawContours(mask_copy, contours, objects, (255, 255, 255), -1)
                kernel = np.ones((trim, trim), np.uint8)
                init_object = cv2.morphologyEx(mask_copy, cv2.MORPH_OPEN, kernel)
                init_object = cv2.erode(init_object, kernel, iterations=trim_iter)
                # cv2.imshow('Mask', init_object)
                # cv2.waitKey(0)
                # cv2.destroyWindow('Mask')
                count = np.count_nonzero(init_object == 255)
                if count:
                    indices = np.where(init_object == [255])
                    if indices[0].size > 0:
                        x_min, x_max = np.min(indices[1]), np.max(indices[1])
                        y_min, y_max = np.min(indices[0]), np.max(indices[0])
                        width, height = x_max - x_min, y_max - y_min
                        center = [int(x_min + (width / 2)), int(y_min + (height / 2))]
                        axis = np.column_stack((indices[1], indices[0]))
                        list_main = [center, [width, height], [x_min, y_min], axis]
                        main_list.append(list_main)
        if main_list:
            return main_list
        else:
            return []
    else:
        return []
