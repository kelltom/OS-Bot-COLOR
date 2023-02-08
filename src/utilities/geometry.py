import math
from typing import List, NamedTuple

import cv2
import mss
import numpy as np

import utilities.random_util as rd

Point = NamedTuple("Point", x=int, y=int)

# TODO: Remove this global variable. This is a temporary fix for a bug in mss.
sct = mss.mss()


class Rectangle:

    """
    In very rare cases, we may want to exclude areas within a Rectangle (E.g., resizable game view).
    This should contain a list of dicts that represent rectangles {left, top, width, height} that
    will be subtracted from this Rectangle during screenshotting.
    """

    subtract_list: List[dict] = []
    reference_rect = None

    def __init__(self, left: int, top: int, width: int, height: int):
        """
        Defines a rectangle area on screen.
        Args:
            left: The leftmost x coordinate of the rectangle.
            top: The topmost y coordinate of the rectangle.
            width: The width of the rectangle.
            height: The height of the rectangle.
            offset: The offset to apply to the rectangle.
        Returns:
            A Rectangle object.
        """
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def set_rectangle_reference(self, rect):
        """
        Sets the rectangle reference of the object.
        Args:
            rect: A reference to the the rectangle that this object belongs in
                  (E.g., Bot.win.game_view).
        """
        self.reference_rect = rect

    @classmethod
    def from_points(cls, start_point: Point, end_point: Point):
        """
        Creates a Rectangle from two points.
        Args:
            start_point: The first point.
            end_point: The second point.
            offset: The offset to apply to the rectangle.
        Returns:
            A Rectangle object.
        """
        return cls(
            start_point.x,
            start_point.y,
            end_point.x - start_point.x,
            end_point.y - start_point.y,
        )

    def screenshot(self) -> cv2.Mat:
        """
        Screenshots the Rectangle.
        Returns:
            A BGR Numpy array representing the captured image.
        """
        # with mss.mss() as sct:  # TODO: When MSS bug is fixed, reinstate this.
        global sct  # TODO: When MSS bug is fixed, remove this.
        monitor = self.to_dict()
        res = np.array(sct.grab(monitor))[:, :, :3]
        if self.subtract_list:
            for area in self.subtract_list:
                res[
                    area["top"] : area["top"] + area["height"],
                    area["left"] : area["left"] + area["width"],
                ] = 0
        return res

    def random_point(self, custom_seeds: List[List[int]] = None) -> Point:
        """
        Gets a random point within the Rectangle.
        Args:
            custom_seeds: A list of custom seeds to use for the random point. You can generate
                            a seeds list using RandomUtil's random_seeds() function with args.
                            Default: A random seed list based on current date and object position.
        Returns:
            A random Point within the Rectangle.
        """
        if custom_seeds is None:
            center = self.get_center()
            custom_seeds = rd.random_seeds(mod=(center[0] + center[1]))
        x, y = rd.random_point_in(self.left, self.top, self.width, self.height, custom_seeds)
        return Point(x, y)

    def get_center(self) -> Point:
        """
        Gets the center point of the rectangle.
        Returns:
            A Point representing the center of the rectangle.
        """
        return Point(self.left + self.width // 2, self.top + self.height // 2)

    # TODO: Consider changing to this to accept a Point to check against; `distance_from(point: Point)`
    def distance_from_center(self) -> Point:
        """
        Gets the distance between the object and it's Rectangle parent center.
        Useful for sorting lists of Rectangles.
        Returns:
            The distance from the point to the center of the object.
        """
        if self.reference_rect is None:
            raise ReferenceError("A Rectangle being sorted is missing a reference to the Rectangle it's contained in and therefore cannot be sorted.")
        center: Point = self.get_center()
        rect_center: Point = self.reference_rect.get_center()
        return math.dist([center.x, center.y], [rect_center.x, rect_center.y])

    def get_top_left(self) -> Point:
        """
        Gets the top left point of the rectangle.
        Returns:
            A Point representing the top left of the rectangle.
        """
        return Point(self.left, self.top)

    def get_top_right(self) -> Point:
        """
        Gets the top right point of the rectangle.
        Returns:
            A Point representing the top right of the rectangle.
        """
        return Point(self.left + self.width, self.top)

    def get_bottom_left(self) -> Point:
        """
        Gets the bottom left point of the rectangle.
        Returns:
            A Point representing the bottom left of the rectangle.
        """
        return Point(self.left, self.top + self.height)

    def get_bottom_right(self) -> Point:
        """
        Gets the bottom right point of the rectangle.
        Returns:
            A Point representing the bottom right of the rectangle.
        """
        return Point(self.left + self.width, self.top + self.height)

    def to_dict(self):
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }

    def __str__(self):
        return f"Rectangle(x={self.left}, y={self.top}, w={self.width}, h={self.height})"

    def __repr__(self):
        return self.__str__()


class RuneLiteObject:
    rect = None

    def __init__(self, x_min, x_max, y_min, y_max, width, height, center, axis):
        """
        Represents an outlined object on screen.
        Args:
            x_min, x_max: The min/max x coordinates of the object.
            y_min, y_max: The min/max y coordinates of the object.
            width: The width of the object.
            height: The height of the object.
            center: The center of the object.
            axis: A 2-column stacked array of points that exist inside the object outline.
        """
        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max
        self._width = width
        self._height = height
        self._center = center
        self._axis = axis

    def set_rectangle_reference(self, rect: Rectangle):
        """
        Sets the rectangle reference of the object.
        Args:
            rect: A reference to the the rectangle that this object belongs in
                  (E.g., Bot.win.game_view).
        """
        self.rect = rect

    def center(self) -> Point:  # sourcery skip: raise-specific-error
        """
        Gets the center of the object relative to the containing Rectangle.
        Returns:
            A Point.
        """
        if self.rect is None:
            raise ReferenceError("The RuneLiteObject is missing a reference to the Rectangle it's contained in and therefore the center cannot be determined.")
        return Point(self._center[0] + self.rect.left, self._center[1] + self.rect.top)

    def distance_from_rect_center(self) -> float:
        """
        Gets the distance between the object and it's Rectangle parent center.
        Useful for sorting lists of RuneLiteObjects.
        Returns:
            The distance from the point to the center of the object.
        Note:
            Only use this if you're sorting a list of RuneLiteObjects that are contained in the same Rectangle.
        """
        center: Point = self.center()
        rect_center: Point = self.rect.get_center()
        return math.dist([center.x, center.y], [rect_center.x, rect_center.y])

    def random_point(self, custom_seeds: List[List[int]] = None) -> Point:
        """
        Gets a random point within the object.
        Args:
            custom_seeds: A list of custom seeds to use for the random point. You can generate
                          a seeds list using RandomUtil's random_seeds() function with args.
                          Default: A random seed list based on current date and object position.
        Returns:
            A random Point within the object.
        """
        if custom_seeds is None:
            custom_seeds = rd.random_seeds(mod=(self._center[0] + self._center[1]))
        x, y = rd.random_point_in(self._x_min, self._y_min, self._width, self._height, custom_seeds)
        return self.__relative_point([x, y]) if self.__point_exists([x, y]) else self.center()

    def __relative_point(self, point: List[int]) -> Point:
        """
        Gets a point relative to the object's container (and thus, the client window).
        Args:
            point: The point to get relative to the object in the format [x, y].
        Returns:
            A Point relative to the client window.
        """
        return Point(point[0] + self.rect.left, point[1] + self.rect.top)

    def __point_exists(self, p: list) -> bool:
        """
        Checks if a point exists in the object.
        Args:
            p: The point to check in the format [x, y].
        """
        return (self._axis == np.array(p)).all(axis=1).any()
