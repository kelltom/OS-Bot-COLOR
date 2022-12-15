"""
A set tools for debugging scripts.
"""
import pathlib
import time

import cv2


def save_image(filename: str, im: cv2.Mat):
    """
    Saves an image to the temporary image directory.
    Args:
        filename: The filename to save the image as.
        im: The image to save (cv2.Mat).
    """
    path = pathlib.Path(__file__).parent.parent.joinpath("images", "temp", filename)
    cv2.imwrite(f"{path}.png", im)


def start_timer():
    """
    Starts a timer.
    Returns:
        The start time.
    """
    return time.time()


def stop_timer(start: float):
    """
    Ends a timer.
    Args:
        start: The start time.
    Returns:
        The time elapsed since the start time.
    """
    return time.time() - start
