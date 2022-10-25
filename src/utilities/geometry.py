from typing import NamedTuple

Point = NamedTuple("Point", x=int, y=int)

class Rectangle:
    def __init__(self, left: int, top: int, width: int, height: int, offset: Point = Point(0, 0)):
        '''
        Defines a rectangle area on screen.
        Args:
            left: The leftmost x coordinate of the rectangle.
            top: The topmost y coordinate of the rectangle.
            width: The width of the rectangle.
            height: The height of the rectangle.
            offset: The offset of the rectangle from the left and top coordinates.
        Returns:
            A Rectangle object.
        '''
        self.left = left + offset.x
        self.top = top + offset.y
        self.width = width
        self.height = height
    
    @classmethod
    def from_points(cls, start_point: Point, end_point: Point, offset: Point = Point(0, 0)):
        '''
        Creates a Rectangle from two points.
        Args:
            start_point: The first point.
            end_point: The second point.
            offset: The offset of the rectangle from the left and top coordinates.
                    (e.g., top-left pixel of game window)
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


def Shape():
    # Should have a color, and all the properties required to draw it and figure out points.
    # Then, it would be passed to a cv function to find those points.

    # A RuneLiteBot function would be the one to fetch the shapes - prob using a cv function.
    pass