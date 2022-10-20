import pyautogui as pag
import pytweening
import numpy as np
import random as rd
import time
from pyclick import HumanCurve

class MouseUtils:

    def move_to(self, destination: tuple, destination_variance: int = 0, **kwargs):
        # sourcery skip: use-contextlib-suppress
        '''
        Use Bezier curve to simulate human-like mouse movements.
        Args:
            destination: x, y tuple of the destination point
            destination_variance: pixel variance to add to the destination point (default 0)
        Kwargs:
            knotsCount: number of knots to use in the curve, higher value = more erratic movements (default 2)
            tween: tweening function to use (default easeOutQuad)
            targetPoints: number of points to use in the curve, where more points = slower/smoother movement
                          (default rand(20, 50), min 10, max 100)
        '''
        offsetBoundaryX = kwargs.get("offsetBoundaryX", 100)
        offsetBoundaryY = kwargs.get("offsetBoundaryY", 100)
        knotsCount = kwargs.get("knotsCount", 2)
        distortionMean = kwargs.get("distortionMean", 1)
        distortionStdev = kwargs.get("distortionStdev", 1)
        distortionFrequency = kwargs.get("distortionFrequency", 0.5)
        tween = kwargs.get("tweening", pytweening.easeOutQuad)
        targetPoints = kwargs.get("targetPoints", rd.randint(20, 50))

        if targetPoints < 10:
            targetPoints = 10
        elif targetPoints > 100:
            targetPoints = 100

        if destination_variance != 0:
            destination[0] += np.random.randint(-destination_variance, destination_variance)
            destination[1] += np.random.randint(-destination_variance, destination_variance)

        start_x, start_y = pag.position()
        for curve_x, curve_y in HumanCurve((start_x, start_y),
                                            destination,
                                            offsetBoundaryX=offsetBoundaryX,
                                            offsetBoundaryY=offsetBoundaryY,
                                            knotsCount=knotsCount,
                                            distortionMean=distortionMean,
                                            distortionStdev=distortionStdev,
                                            distortionFrequency=distortionFrequency,
                                            tween=tween,
                                            targetPoints=targetPoints
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
            kwargs: see move_to()
        '''
        self.move_to((pag.position()[0] + x, pag.position()[1] + y), destination_variance, **kwargs)

    def click(self):
        pag.click()


if __name__ == '__main__':
    mouse = MouseUtils()
    from bot_cv import Point
    mouse.move_to(destination=Point(646, 213), targetPoints=100)
    time.sleep(1)
    mouse.move_to(destination=(180, 500), knotsCount=4)
    time.sleep(1)
    mouse.move_to(destination=(300, 350), distortionStdev=2)
    time.sleep(1)
    mouse.move_to(destination=(300, 200))
    time.sleep(1)
    mouse.move_to(destination=(90, 80), targetPoints=10)
    time.sleep(1)
    mouse.move_rel(x=3, y=50, targetPoints=10)
    time.sleep(1)
    mouse.move_rel(x=60, y=2)
