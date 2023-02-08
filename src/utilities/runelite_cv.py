"""
A set of computer vision utilities for use with RuneLite-based bots.

TODO: Similarly to OCR, should these functions accept the Rect as an argument and do
the screenshotting/color manipulation here? It would allow each RL Object to be created
with its Rectangle reference property.
"""
from typing import List

import cv2
import numpy as np

from utilities.geometry import Point, RuneLiteObject


def extract_objects(image: cv2.Mat) -> List[RuneLiteObject]:
    """
    Given an image of enclosed outlines, this function will extract information
    from each outlined object into a data structure.
    Args:
        image: The image to process.
    Returns:
        A list of RuneLiteObjects, or an empty list if no objects are found.
    """
    # Dilate the outlines
    kernel = np.ones((4, 4), np.uint8)
    mask = cv2.dilate(image, kernel, iterations=1)
    # If no objects are found, return an empty list
    if not np.count_nonzero(mask == 255):
        return []
    # Find the contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    black_image = np.zeros(mask.shape, dtype="uint8")
    # Extract the objects from each contoured object
    objs: List[RuneLiteObject] = []
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
                    objs.append(RuneLiteObject(x_min, x_max, y_min, y_max, width, height, center, axis))
    return objs or []


def is_point_obstructed(point: Point, im: cv2.Mat, span: int = 30) -> bool:
    """
    This function determines if there are non-black pixels in an image around a given point.
    This is useful for determining if an NPC is in combat (E.g., given the mid point of an NPC contour
    and a masked image only showing HP bars, determine if the NPC has an HP bar around the contour).
    Args:
        point: The top point of a contour (NPC).
        im: A BGR CV image containing only HP bars.
        span: The number of pixels to search around the given point.
    Returns:
        True if the point is obstructed, False otherwise.
    """
    try:
        crop = im[point[1] - span : point[1] + span, point[0] - span : point[0] + span]
        mean = crop.mean(axis=(0, 1))
        return mean != 0.0
    except Exception as e:
        print(f"Error in is_point_obstructed(): {e}")
        return True
