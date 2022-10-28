from pyclick import HumanCurve
import numpy as np
import pyautogui as pag
import pytweening
import time
import random as rd

class MouseUtils:

    def move_to(self, destination: tuple, destination_variance: int = 0, **kwargs):
        # sourcery skip: use-contextlib-suppress
        '''
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
        '''
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

        if destination_variance != 0:
            dest_x += np.random.randint(-destination_variance, destination_variance)
            dest_y += np.random.randint(-destination_variance, destination_variance)

        start_x, start_y = pag.position()
        for curve_x, curve_y in HumanCurve((start_x, start_y),
                                           (dest_x, dest_y),
                                           offsetBoundaryX=offsetBoundaryX,
                                           offsetBoundaryY=offsetBoundaryY,
                                           knotsCount=knotsCount,
                                           distortionMean=distortionMean,
                                           distortionStdev=distortionStdev,
                                           distortionFrequency=distortionFrequency,
                                           tween=tween,
                                           targetPoints=mouseSpeed
                                           ).points:
            pag.moveTo((curve_x, curve_y))
            start_x, start_y = curve_x, curve_y

    def move_rel(self, x: int, y: int, destination_variance: int = 0, **kwargs):
        '''
        Use Bezier curve to simulate human-like relative mouse movements.
        Args:
            x: x distance to move
            y: y distance to move
            destination_variance: pixel variance to add to the destination point (default 0)
        Kwargs:
            knotsCount: default 0 to prevent movement from closing right-click menus in game.
            See MouseUtils.move_to()
        '''
        self.move_to((pag.position()[0] + x, pag.position()[1] + y),
                      destination_variance, **kwargs, knotsCount=0)
    
    def click(self):
        pag.click()
    
    def right_click(self):
        pag.rightClick()
    
    def __calculate_knots(self, destination: tuple):
        '''
        Calculate the knots to use in the Bezier curve based on distance.
        Args:
            destination: x, y tuple of the destination point
        '''
        # calculate the distance between the start and end points
        distance = np.sqrt((destination[0] - pag.position()[0]) ** 2 + (destination[1] - pag.position()[1]) ** 2)
        res = round(distance / 200)
        return min(res, 3)
    
    def __get_mouse_speed(self, speed: str) -> int:
        '''
        Converts a text speed to a numeric speed for HumanCurve (targetPoints).
        '''
        if speed == "slowest":
            return rd.randint(85, 100)
        elif speed == "slow":
            return rd.randint(65, 80)
        elif speed == "medium":
            return rd.randint(45, 60)
        elif speed == "fast":
            return rd.randint(20, 40)
        elif speed == "fastest":
            return rd.randint(10, 15)
        else:
            raise ValueError("Invalid mouse speed. Try 'slowest', 'slow', 'medium', 'fast', or 'fastest'.")


if __name__ == '__main__':
    mouse = MouseUtils()
    from geometry import Point
    mouse.move_to((1,1))
    time.sleep(1)
    mouse.move_to(destination=Point(765, 503), mouseSpeed="slowest")
    time.sleep(1)
    mouse.move_to(destination=(1, 1), mouseSpeed='slow')
    time.sleep(1)
    mouse.move_to(destination=(300, 350), mouseSpeed='medium')
    time.sleep(1)
    mouse.move_to(destination=(400, 450), mouseSpeed='fast')
    time.sleep(1)
    mouse.move_to(destination=(234, 122), mouseSpeed='fastest')
    time.sleep(1)
    mouse.move_rel(0, 100)
    time.sleep(1)
    mouse.move_rel(0, 100)