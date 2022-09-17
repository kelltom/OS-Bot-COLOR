import pyautogui as pag
import numpy as np


class MouseUtils():

    def move_to(self, point: tuple, duration=0.3, variance=0):
        '''
        Moves mouse to a point on screen with a random movement pattern.
        Args:
            point: x, y tuple of the destination point
            duration: duration of the movement
            variance: maximum pixel variance in final x and y position
        '''
        # tweens = [pag.easeOutBounce, pag.easeInBounce, pag.easeInBack,
        #           pag.easeInCirc, pag.easeInCubic, pag.easeInElastic,
        #           pag.easeInExpo, pag.easeInOutBounce, pag.easeInOutQuad,
        #           pag.easeInOutQuart, pag.easeInQuart, pag.easeInQuint,
        #           pag.easeInOutBack, pag.easeOutSine]
        # tween = tweens[np.random.randint(0, len(tweens))]
        tween = pag.easeInOutSine
        x, y = point
        if variance != 0:
            x += np.random.randint(-variance, variance)
            y += np.random.randint(-variance, variance)
        pag.moveTo(x, y, duration=duration, tween=tween)

    def move_rel(self, x, y, duration=0.3, variance=0):
        '''
        Moves mouse relative to current position.
        Args:
            x: x distance to move
            y: y distance to move
            duration: duration of the movement
            variance: maximum pixel variance in final x and y position
        '''
        self.move_to((pag.position()[0] + x, pag.position()[1] + y), duration, variance)

    def click(self):
        pag.click()
