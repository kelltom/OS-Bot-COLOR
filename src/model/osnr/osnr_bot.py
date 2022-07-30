'''
The OSNRBot class contains properties and functions that are specific to the OSNR client. This class should
be inherited by OSNR script classes.
'''
from abc import ABCMeta
from model.runelite_bot import RuneliteBot
from model.bot import Point
import pyautogui as pag
import time


class OSNRBot(RuneliteBot, metaclass=ABCMeta):

    def bank_at_home(self):
        pass

    def __disable_private_chat(self):
        '''
        Disables private chat in game.
        '''
        self.log_msg("Disabling private chat...")
        private_btn = Point(218, 517)
        show_none_btn = Point(225, 489)
        self.mouse.move_to(private_btn, duration=0.5, variance=3)
        pag.rightClick()
        time.sleep(0.05)
        self.mouse.move_to(show_none_btn, duration=0.2, variance=1)
        pag.click()

    def teleport_home(self):
        pass

    def setup_osnr(self):
        '''
        Sets up the OSNR client.
        '''
        self.setup_client(window_title="Near-Reality", logout_runelite=False, close_runelite_settings=True)
        self.__disable_private_chat()
