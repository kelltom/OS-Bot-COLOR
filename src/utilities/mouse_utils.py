import pyautogui as pag
import numpy as np
import random as rd
from typing import Callable, Union


class MouseUtils:

    @staticmethod
    def move_to(point: tuple, duration: float = 0.3, duration_variance: float = 0, time_variance: float = 0,
                tween: Union[str, Callable] = None):
        '''
        Moves mouse to a point on screen with a random movement pattern.
        Args:
            point: x, y tuple of the destination point
            duration: duration of the movement
            duration_variance: maximum pixel variance in final x and y position
            time_variance: the variance absolute of duration. This number is always positive (gaussian with mean 0)
            tween: a mouse movement object from pyautogui.
                                If None, easeInOutSine is default.
                                If 'rand' then a selection of random movements will be used
                                else enter a callable pyautogui function
        '''
        if tween is None:
            tween = pag.easeInOutSine
        elif tween == 'rand':
            tween = rd.choice([pag.easeOutBounce, pag.easeInBounce, pag.easeInBack,
                               pag.easeInCirc, pag.easeInCubic, pag.easeInElastic,
                               pag.easeInExpo, pag.easeInOutBounce, pag.easeInOutQuad,
                               pag.easeInOutQuart, pag.easeInQuart, pag.easeInQuint,
                               pag.easeInOutBack, pag.easeOutSine])
        else:
            if not isinstance(tween, Callable):
                raise TypeError('mouse_movement must be a callable function. Use None for default or "rand" for random')
        x, y = point
        if duration_variance != 0:
            x += np.random.randint(-duration_variance, duration_variance)
            y += np.random.randint(-duration_variance, duration_variance)
        pag.moveTo(x, y, duration=duration + np.abs(rd.gauss(0, time_variance)), tween=tween)

    def move_rel(self, x: int, y: int, duration: float = 0.3, duration_variance: float = 0, time_variance: float = 0,
                 mouse_movement: Callable = None):
        '''
        Moves mouse relative to current position.
        Args:
            x: x distance to move
            y: y distance to move
            duration: duration of the movement
            duration_variance: maximum pixel variance in final x and y position
            time_variance: the variance absolute of duration. This number is always positive (gaussian with mean 0)
            mouse_movement: a mouse movement object from pyautogui.
                                If None, easeInOutSine is default.
                                If 'rand' then a selection of random movements will be used
                                else enter a callable pyautogui function
        '''
        self.move_to((pag.position()[0] + x, pag.position()[1] + y), duration, duration_variance, time_variance,
                     mouse_movement)

    @staticmethod
    def click():
        pag.click()


if __name__ == '__main__':
    # testing
    test_inst = MouseUtils()
    test_inst.move_to((100, 100), 0.5, 10, 0.1, 'rand')
    test_inst.move_to((500, 500), 0.5, 10, 0.1, pag.easeInQuart)
    test_inst.move_to((300, 300), 0.5, 10, 0.1)

    test_inst.move_rel(100, 100, 0.5, 10, 0.1, 'rand')
    test_inst.move_rel(-100, 100, 0.5, 10, 0.1, pag.easeInQuart)
    test_inst.move_rel(100, -100, 0.5, 10, 0.1)
