'''
A set of computer vision utilities for use with RuneLite-based bots.
'''
from typing import List
from utilities.geometry import Point, Shape
import cv2
import numpy as np
import utilities.bot_cv as bcv

def extract_shapes(image: cv2.Mat) -> List[Shape]:
    '''
    Given an image of enclosed outlines, this function will extract information
    from each outlined shape into a data structure.
    Args:
        image: The image to process.
    Returns:
        A list of Shape objects, or an empty list if no shapes are found.
    '''
    # Dilate the outlines
    kernel = np.ones((4, 4), np.uint8)
    mask = cv2.dilate(image, kernel, iterations=1)
    # If no shapes are found, return an empty list
    if not np.count_nonzero(mask == 255):
        return []
    # Find the contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    black_image = np.zeros(mask.shape, dtype="uint8")
    # Extract the shapes from each contoured object
    shapes: List[Shape] = []
    for objects in range(len(contours)):
        if len(contours[objects]) > 2:
            # Fill in the outline with white pixels
            black_copy = black_image.copy()
            cv2.drawContours(black_copy, contours, objects, (255, 255, 255), -1)
            kernel = np.ones((7, 7), np.uint8)
            black_copy = cv2.morphologyEx(black_copy, cv2.MORPH_OPEN, kernel)
            black_copy = cv2.erode(black_copy, kernel, iterations=2)
            if np.count_nonzero(black_copy == 255):
                indices = np.where(black_copy == [255])
                if indices[0].size > 0:
                    x_min, x_max = np.min(indices[1]), np.max(indices[1])
                    y_min, y_max = np.min(indices[0]), np.max(indices[0])
                    width, height = x_max - x_min, y_max - y_min
                    center = [int(x_min + (width / 2)), int(y_min + (height / 2))]
                    axis = np.column_stack((indices[1], indices[0]))
                    shapes.append(Shape(x_min, x_max, y_min, y_max, width, height, center, axis))
    return shapes or []

def isolate_colors(image: cv2.Mat, colors: List[List[int]]) -> cv2.Mat:
    '''
    Isolates ranges of colors within an image and saves a new resulting image.
    Args:
        image: The image to process.
        colors: A list of rcv Colors.
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
    bcv.save_image("isolate_colors.png", cv2.bitwise_and(image, image, mask=mask))
    return mask

def is_point_obstructed(point: Point, im: cv2.Mat, span: int = 30) -> bool:
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
        crop = im[point[1]-span:point[1]+span, point[0]-span:point[0]+span]
        mean = crop.mean(axis=(0, 1))
        return mean != 0.0
    except Exception as e:
        print(f"Error in is_point_obstructed(): {e}")
        return True
