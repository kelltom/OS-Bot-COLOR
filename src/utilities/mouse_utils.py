import pyautogui as pag
import numpy as np
import random as rd
import time
from pyclick import HumanCurve

class MouseUtils:

    # TODO: Change to kwargs to reduce number of parameters.
    def move_to(self, destination: tuple, target_points: int = rd.randint(20, 50), destination_variance: int = 0, knots_count=2):
        # sourcery skip: use-contextlib-suppress
        '''
        Use Bezier curve to simulate human-like mouse movements.
        Args:
            destination: x, y tuple of the destination point
            target_points: number of points to use in the curve - more points = slower/more realistic movement
                           (default rand(20, 50), min 10, max 100)
            destination_variance: pixel variance to add to the destination point (default 0)
            knots_count: number of knots to use in the curve - higher value = erratic movements (default 2)
        '''
        if target_points < 10:
            target_points = 10
        elif target_points > 100:
            target_points = 100

        if destination_variance != 0:
            destination[0] += np.random.randint(-destination_variance, destination_variance)
            destination[1] += np.random.randint(-destination_variance, destination_variance)

        start_x, start_y = pag.position()
        for curve_x, curve_y in HumanCurve((start_x, start_y),
                                            destination,
                                            targetPoints=target_points,
                                            distortionStdev=1,
                                            knotsCount=knots_count
                                            ).points:
            pag.moveTo((curve_x, curve_y))
            start_x, start_y = curve_x, curve_y

    # TODO: Change to kwargs to reduce number of parameters.
    def move_rel(self, x: int, y: int, target_points: int = rd.randint(10, 25), destination_variance: int = 0, knots_count=2):
        '''
        Use Bezier curve to simulate human-like relative mouse movements.
        Args:
            x: x distance to move
            y: y distance to move
            target_points: number of points to use in the curve (more points = slower/more realistic movement)
                           (default rand(10, 25), min 10, max 100)
            destination_variance: pixel variance to add to the destination point (default 0)
            knots_count: number of knots to use in the curve - higher value = erratic movements (default 2)
        '''
        self.move_to((pag.position()[0] + x, pag.position()[1] + y), target_points, destination_variance, knots_count)

    def click(self):
        pag.click()


if __name__ == '__main__':
    mouse = MouseUtils()
    from bot_cv import Point
    mouse.move_to(destination=Point(646, 213))
    time.sleep(1)
    mouse.move_to(destination=(180, 500))
    time.sleep(1)
    mouse.move_to(destination=(300, 350))
    time.sleep(1)
    mouse.move_to(destination=(300, 200), target_points=70)
    time.sleep(1)
    mouse.move_to(destination=(90, 80), target_points=100)
    time.sleep(1)
    mouse.move_rel(x=3, y=50)
    time.sleep(1)
    mouse.move_rel(x=60, y=2, target_points=40)
