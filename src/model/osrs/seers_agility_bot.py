from model.runelite_bot import RuneLiteBot
import time
from utilities.runelite_cv import isolate_colors, get_contour_positions, Color, get_contours
import pyautogui as pag
import numpy as np
import random as rd
import pandas as pd
from model.bot import BotStatus
import cv2


class SeersAgilityBot(RuneLiteBot):
    def __init__(self, mouse_csv='src/files/agility/click_log.csv'):
        title = "Seers Agility Bot"
        description = ("This bot will complete the Seers' Village Agility Course. Put your character on the first"
                       " roof to begin. Marks will only be collected every 8 laps to save on time.")
        super().__init__(title=title, description=description)
        self.running_time = 0
        self.multi_select_example = None
        self.menu_example = None
        self.version = "1.0.0"
        self.author = "Travis Barton"
        self.author_email = "travisdatabarton@gmail.com"
        self.mouse_info = pd.read_csv(mouse_csv)
        self.mouse_info.time = self.mouse_info.time.diff().iloc[1:].tolist() + [3]

    def create_options(self):
        '''
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        '''
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 360)  # max 180 minutes

    def save_options(self, options: dict):
        '''
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False. No need to set bot status.
        '''
        self.options_set = True
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
                self.log_msg(f"Bot will run for {self.running_time} rounds.")
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False

        if self.options_set:
            self.log_msg("Options set successfully.")
        else:
            self.log_msg("Failed to set options.")
            print("Developer: ensure option keys are correct, and that the option values are being accessed correctly.")

    def main_loop(self, runs=250, color=None):
        # setup the bot
        if color is None:
            color = self.TAG_PURPLE
        self.setup_client('RuneLite', True, True, True)
        self.set_camera_zoom(43)
        self.set_status(BotStatus.RUNNING)
        self.vision_run(color)
        # start the bot
        while self.running_time > 0:
            self.log_msg(f'starting run {self.running_time}')
            if not self.status_check_passed():
                return
            if self.running_time % 8 == 0:
                self.vision_run(color)
            else:
                self.fast_rout()
            if not self.check_for_fall():
                self.running_time -= 1
                continue
            else:
                self.log_msg('something went wrong on reset, logging out')
                self.logout()
                self.set_status(BotStatus.STOPPED)

        return

    def check_for_mark(self, region=None, confidence=.6):
        LOC = pag.locateOnScreen(f'src/files/agility/seers_templates/mark_of_grace.png', confidence=confidence, region=region)
        if LOC is not None:
            # self.log_msg(f'Grace mark found')
            mid = pag.center(LOC)
            self.mouse.move_to((mid.x + rd.gauss(0, 3), mid.y + rd.gauss(0, 3)), .2, 1, .005, 'rand')
            self.mouse.click()
            time.sleep(3.4 + np.abs(rd.gauss(0, .1)))
            return True
        else:
            return False

    def check_for_fall(self):
        min_map = (self.rect_minimap.start.x, self.rect_minimap.start.y,
                   self.rect_minimap.end.x - self.rect_minimap.start.x,
                   self.rect_minimap.end.y - self.rect_minimap.start.y)
        shot = pag.screenshot(imageFilename='src/images/temp/temp_screenshot_fall.png', region=min_map)
        hist = shot.histogram()
        if hist[0] > 1500:  # if black pixels are more than 500
            return False
        else:
            return True

    def fast_rout(self):
        self.log_msg('starting speed run..')
        for idx, row in self.mouse_info.iterrows():
            loc = (row.x, row.y)
            if idx < 5:
                jitter = 3
            else:
                jitter = 0
            self.mouse.move_to((loc), .2, jitter, .005, 'rand')
            self.mouse.click()
            time.sleep(row.time + rd.gauss(0, .005))
            if idx == 0:
                if self.check_for_fall():
                    self.log_msg('fall 1 detected')
                    self.mouse.move_to((710, 109), .2, 0, .001)
                    self.mouse.click()
                    time.sleep(5)
                    self.mouse.move_to((320, 81), .2, 0, .001)
                    self.mouse.click()
                    time.sleep(7)

            if idx == 1:
                if self.check_for_fall():
                    self.log_msg('fall 2 detected')
                    self.mouse.move_to((710, 109), .2, 0, .001)
                    self.mouse.click()
                    time.sleep(6)
                    self.mouse.move_to((344, 92), .2, 0, .001)
                    self.mouse.click()
                    time.sleep(7)
            if not self.status_check_passed():
                return
        time.sleep(5)

    def click_on_color(self, color):
        map = self.rect_game_view
        map = (map.start.x, map.start.y, map.end.x-map.start.x, map.end.y-map.start.y)
        pag.screenshot(imageFilename='src/images/temp/temp_screenshot.png', region=map)
        path_tagged = isolate_colors('src/images/temp/temp_screenshot.png', [color], "get_all_tagged_in_rect")
        contours = get_contours(path_tagged)
        # coords = get_contour_positions(contours)
        coords = rd.choice(contours[0])[0]
        print(contours[0])
        self.mouse.move_to((coords[0], coords[1]), .2, 0, .001)
        self.mouse.click()
        # cv2.imshow('mask', mask)
        # cv2.imshow('result', result)
        # cv2.waitKey()
        return (coords[0], coords[1])

    def vision_run(self, color):
        self.log_msg('Starting vision run...')
        while True:
            self.check_for_mark()
            cen = self.get_nearest_tag(color)
            if cen is not None:
                self.mouse.move_to(cen, .2, 3, .001, 'rand')
                self.mouse.click()
                time.sleep(5 + rd.gauss(0, .05))
            if self.check_for_fall():
                if pag.locateCenterOnScreen('src/files/agility/seers_templates/starting_map.png',
                                            confidence=.8) is not None:
                    self.mouse.move_to((704, 80), .2, 0, .001)
                    self.mouse.click()
                    time.sleep(9.691993 + np.abs(rd.gauss(0, .001)))
                    self.mouse.move_to((684, 60), .2, 0, .001)
                    self.mouse.click()
                    time.sleep(6.759854 + np.abs(rd.gauss(0, .001)))
                    self.mouse.move_to((262, 92), .2, 0, .001)
                    self.mouse.click()
                    time.sleep(7 + np.abs(rd.gauss(0, .001)))
                    break
                elif pag.locateCenterOnScreen('src/files/agility/seers_templates/fall_2_map.png',
                                            confidence=.8) is not None:
                    self.mouse.move_to((710, 109), .2, 0, .001)
                    self.mouse.click()
                    time.sleep(5)
                    self.mouse.move_to((344, 92), .2, 0, .001)
                    self.mouse.click()
                    time.sleep(7)
                elif pag.locateCenterOnScreen('src/files/agility/seers_templates/fall_1_map.png',
                                            confidence=.7) is not None:
                    self.log_msg('fall 1 detected')
                    self.mouse.move_to((710, 109), .2, 0, .001)
                    self.mouse.click()
                    time.sleep(5)
                    self.mouse.move_to((320, 81), .2, 0, .001)
                    self.mouse.click()
                    time.sleep(7)
                else:
                    raise Exception('none of the fall maps connected')


if __name__ == '__main__':
    ab = SeersAgilityBot(mouse_csv='C:\\Users\\sivar\\PycharmProjects\\OSRS-Bot-COLOR\\src\\files\\agility\\click_log.csv')
    # col = Color(hsv_upper=(90, 100, 255), hsv_lower=(100, 255, 255))
    #
    # time.sleep(2)
    # # agility_bot.main_loop()
    ab.check_for_mark()
    # cen = ab.get_nearest_tag(ab.TAG_BLUE)
    # ab.mouse.move_to(cen, .2, 1, .001, 'rand')
    # ab.mouse.click()
    # # cen = ab.get_all_tagged_in_rect(ab.rect_game_view, ab.TAG_BLUE)
    # ab.mouse.move_to(cen, destination_variance=1, time_variance=.05, tween='rand')
    # ab.mouse.click()
    # print(cen)
    # time.sleep(2)
    # ab.fast_rout()
    # ab.check_for_fall()
    ab.vision_run()
    # time.sleep(3)
    # pag.screenshot('la.png')
    # isolate_colors('la.png', [ab.TAG_BLUE], 'laa')
    # la = ab.click_on_color(ab.TAG_PURPLE)
    # len(la[0])
    # la[0][2][0]
    # ab.mouse.move_to(ab.get_nearest_tag(ab.TAG_PURPLE))
    # ab.mouse.click()
