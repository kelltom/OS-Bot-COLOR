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


def timer(func):
    """
    A decorator that prints the time taken to execute a function.
    Args:
        func: The function to time.
    """

    def wrapper(*args, **kwargs):
        start = time.time_ns() // 1_000_000
        result = func(*args, **kwargs)
        end = time.time_ns() // 1_000_000
        print(f"`{func.__name__}` took {round(end - start, 2)} ms.")
        return result

    return wrapper


def current_time():
    """
    Gets the current time in the format HH:MM:SS.
    Returns:
        The current time.
    """
    return time.strftime("%H:%M:%S", time.localtime())
