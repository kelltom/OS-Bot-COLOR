'''
A set tools for debugging scripts.
'''
import cv2
import pathlib

def save_image(filename: str, im: cv2.Mat):
    '''
    Saves an image to the temporary image directory.
    Args:
        filename: The filename to save the image as.
        im: The image to save (cv2.Mat).
    '''
    path = pathlib.Path(__file__).parent.parent.joinpath('images', 'temp', filename)
    cv2.imwrite(f"{path}.png", im)
