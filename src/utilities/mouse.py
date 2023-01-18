import random as rd
import time

import numpy as np
import pyautogui as pag
import pytweening
from deprecated import deprecated
from pyclick import HumanCurve

import utilities.color as clr
from utilities.geometry import Point, Rectangle
from utilities.random_util import truncated_normal_sample


class Mouse:
    click_delay = True

    def move_to(self, destination: tuple, **kwargs):
        """
        Use Bezier curve to simulate human-like mouse movements.
        Args:
            destination: x, y tuple of the destination point
            destination_variance: pixel variance to add to the destination point (default 0)
        Kwargs:
            knotsCount: number of knots to use in the curve, higher value = more erratic movements
                        (default determined by distance)
            mouseSpeed: speed of the mouse (options: 'slowest', 'slow', 'medium', 'fast', 'fastest')
                        (default 'fast')
            tween: tweening function to use (default easeOutQuad)
        """
        offsetBoundaryX = kwargs.get("offsetBoundaryX", 100)
        offsetBoundaryY = kwargs.get("offsetBoundaryY", 100)
        knotsCount = kwargs.get("knotsCount", self.__calculate_knots(destination))
        distortionMean = kwargs.get("distortionMean", 1)
        distortionStdev = kwargs.get("distortionStdev", 1)
        distortionFrequency = kwargs.get("distortionFrequency", 0.5)
        tween = kwargs.get("tweening", pytweening.easeOutQuad)
        mouseSpeed = kwargs.get("mouseSpeed", "fast")
        mouseSpeed = self.__get_mouse_speed(mouseSpeed)

        dest_x = destination[0]
        dest_y = destination[1]

        start_x, start_y = pag.position()
        for curve_x, curve_y in HumanCurve(
            (start_x, start_y),
            (dest_x, dest_y),
            offsetBoundaryX=offsetBoundaryX,
            offsetBoundaryY=offsetBoundaryY,
            knotsCount=knotsCount,
            distortionMean=distortionMean,
            distortionStdev=distortionStdev,
            distortionFrequency=distortionFrequency,
            tween=tween,
            targetPoints=mouseSpeed,
        ).points:
            pag.moveTo((curve_x, curve_y))
            start_x, start_y = curve_x, curve_y

    def move_rel(self, x: int, y: int, x_var: int = 0, y_var: int = 0, **kwargs):
        """
        Use Bezier curve to simulate human-like relative mouse movements.
        Args:
            x: x distance to move
            y: y distance to move
            x_var: maxiumum pixel variance that may be added to the x distance (default 0)
            y_var: maxiumum pixel variance that may be added to the y distance (default 0)
        Kwargs:
            knotsCount: if right-click menus are being cancelled due to erratic mouse movements,
                        try setting this value to 0.
        """
        if x_var != 0:
            x += round(truncated_normal_sample(-x_var, x_var))
        if y_var != 0:
            y += round(truncated_normal_sample(-y_var, y_var))
        self.move_to((pag.position()[0] + x, pag.position()[1] + y), **kwargs)

    def click(self, button="left", force_delay=False) -> bool:
        """
        Clicks on the current mouse position.
        Args:
            button: button to click (default left)
            with_delay: whether to add a random delay between mouse down and mouse up (default True)
        """
        pag.mouseDown(button=button)
        if force_delay or self.click_delay:
            LOWER_BOUND_CLICK = 0.03  # Milliseconds
            UPPER_BOUND_CLICK = 0.2  # Milliseconds
            AVERAGE_CLICK = 0.06  # Milliseconds
            time.sleep(truncated_normal_sample(LOWER_BOUND_CLICK, UPPER_BOUND_CLICK, AVERAGE_CLICK))
        pag.mouseUp(button=button)

    def right_click(self, force_delay=False):
        """
        Right-clicks on the current mouse position. This is a wrapper for click(button="right").
        Args:
            with_delay: whether to add a random delay between mouse down and mouse up (default True)
        """
        self.click(button="right", force_delay=force_delay)

    @deprecated(version="0.2.0", reason="Currently unreliable. Use click() instead.")
    def click_with_check(self) -> bool:
        """
        Clicks on the current mouse position and checks if the click was red.
        Returns:
            True if the click was red, False if the click was yellow.
        """
        self.click()
        return self.__is_red_click()

    @deprecated(version="0.2.0", reason="This function should instead perform image search using official click sprites.")
    def __is_red_click(self) -> bool:
        """
        Checks if a click was red, must be called directly after clicking.
        Returns:
            True if the click was red, False if the click was yellow.
        """
        mouse_x, mouse_y = pag.position()
        # Make rect around cursor for screenshot
        mouse_rect = Rectangle.from_points(Point(mouse_x - 5, mouse_y - 5), Point(mouse_x + 5, mouse_y + 5))
        # Isolate red click from screenshot
        mouse_red_click = clr.isolate_colors(mouse_rect.screenshot(), clr.RED)
        return np.any(mouse_red_click)

    def __calculate_knots(self, destination: tuple):
        """
        Calculate the knots to use in the Bezier curve based on distance.
        Args:
            destination: x, y tuple of the destination point
        """
        # Calculate the distance between the start and end points
        distance = np.sqrt((destination[0] - pag.position()[0]) ** 2 + (destination[1] - pag.position()[1]) ** 2)
        res = round(distance / 200)
        return min(res, 3)

    def __get_mouse_speed(self, speed: str) -> int:
        """
        Converts a text speed to a numeric speed for HumanCurve (targetPoints).
        """
        if speed == "slowest":
            min, max = 85, 100
        elif speed == "slow":
            min, max = 65, 80
        elif speed == "medium":
            min, max = 45, 60
        elif speed == "fast":
            min, max = 20, 40
        elif speed == "fastest":
            min, max = 10, 15
        else:
            raise ValueError("Invalid mouse speed. Try 'slowest', 'slow', 'medium', 'fast', or 'fastest'.")
        return round(truncated_normal_sample(min, max))


if __name__ == "__main__":
    mouse = Mouse()
    from geometry import Point

    mouse.move_to((1, 1))
    time.sleep(0.5)
    mouse.move_to(destination=Point(765, 503), mouseSpeed="slowest")
    time.sleep(0.5)
    mouse.move_to(destination=(1, 1), mouseSpeed="slow")
    time.sleep(0.5)
    mouse.move_to(destination=(300, 350), mouseSpeed="medium")
    time.sleep(0.5)
    mouse.move_to(destination=(400, 450), mouseSpeed="fast")
    time.sleep(0.5)
    mouse.move_to(destination=(234, 122), mouseSpeed="fastest")
    time.sleep(0.5)
    mouse.move_rel(0, 100)
    time.sleep(0.5)
    mouse.move_rel(0, 100)
