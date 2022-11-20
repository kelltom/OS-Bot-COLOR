from typing import NamedTuple, Callable
import math

Point = NamedTuple("Point", x=int, y=int)

class Rectangle:
    def __init__(self, left: int, top: int, width: int, height: int, offset: Point = (0, 0)):
        '''
        Defines a rectangle area on screen.
        Args:
            left: The leftmost x coordinate of the rectangle.
            top: The topmost y coordinate of the rectangle.
            width: The width of the rectangle.
            height: The height of the rectangle.
            offset: The offset to apply to the rectangle.
        Returns:
            A Rectangle object.
        '''
        self.left = left + offset[0]
        self.top = top + offset[1]
        self.width = width
        self.height = height
    
    @classmethod
    def from_points(cls, start_point: Point, end_point: Point, offset: Point = Point(0, 0)):
        '''
        Creates a Rectangle from two points.
        Args:
            start_point: The first point.
            end_point: The second point.
        Returns:
            A Rectangle object.
        '''
        start_point = Point(start_point.x + offset.x, start_point.y + offset.y)
        end_point = Point(end_point.x + offset.x, end_point.y + offset.y)
        return cls(start_point.x, start_point.y, end_point.x - start_point.x, end_point.y - start_point.y)

    def get_center(self) -> Point:
        '''
        Gets the center point of the rectangle.
        Returns:
            A Point representing the center of the rectangle.
        '''
        return Point(self.left + self.width // 2, self.top + self.height // 2)

    def get_top_left(self) -> Point:
        '''
        Gets the top left point of the rectangle.
        Returns:
            A Point representing the top left of the rectangle.
        '''
        return Point(self.left, self.top)

    def get_top_right(self) -> Point:
        '''
        Gets the top right point of the rectangle.
        Returns:
            A Point representing the top right of the rectangle.
        '''
        return Point(self.left + self.width, self.top)

    def get_bottom_left(self) -> Point:
        '''
        Gets the bottom left point of the rectangle.
        Returns:
            A Point representing the bottom left of the rectangle.
        '''
        return Point(self.left, self.top + self.height)

    def get_bottom_right(self) -> Point:
        '''
        Gets the bottom right point of the rectangle.
        Returns:
            A Point representing the bottom right of the rectangle.
        '''
        return Point(self.left + self.width, self.top + self.height)

    def to_dict(self):
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height
        }

    def __str__(self):
        return f"Rectangle(x={self.left}, y={self.top}, w={self.width}, h={self.height})"

    def __repr__(self):
        return self.__str__()


class Shape:

    rect_ref = None

    def __init__(self, x_min, x_max, y_min, y_max, width, height, center, axis):
        '''
        Represents a shape on screen, typically used to represent tagged/outlined objects.
        Args:
            x_min, x_max: The min/max x coordinates of the shape.
            y_min, y_max: The min/max y coordinates of the shape.
            width: The width of the shape.
            height: The height of the shape.
            center: The center of the shape.
            axis: A 2-column stacked array of points that make up the shape.
        '''
        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max
        self._width = width
        self._height = height
        self._center = center
        self._axis = axis
    
    def set_rectangle_reference(self, rect_function: Callable):
        '''
        Sets the rectangle reference of the shape.
        Args:
            rect_function: A reference to the function used to get info for the rectangle
                           that this shape belongs in (E.g., Bot.win.rect_game_view).
        '''
        self.rect_ref = rect_function
        
    def __point_exists(self, p: tuple) -> bool:
        '''
        Checks if a point exists in the shape.
        '''
        pass

    def center(self) -> Point:  # sourcery skip: raise-specific-error
        '''
        Gets the center of the shape relative to the client.
        Returns:
            A Point.
        '''
        if self.rect_ref is None:
            raise Exception("Rectangle reference not set for shape.")
        rect: Rectangle = self.rect_ref()
        return Point(self._center[0] + rect.left, self._center[1] + rect.top)

    def distance_from_rect_center(self) -> float:
        '''
        Gets the distance between the shape and it's Rectangle parent center.
        Useful for sorting lists of Shapes.
        Returns:
            The distance from the point to the center of the shape.
        '''
        center: Point = self.center()
        rect: Rectangle = self.rect_ref()
        rect_center: Point = rect.get_center()
        return math.dist([center.x, center.y], [rect_center.x, rect_center.y])
