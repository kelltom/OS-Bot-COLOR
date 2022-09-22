import pandas as pd
import time
from pynput import mouse
import pyautogui as pg
import os

if not os.path.exists('auto_screenshots'):
    os.mkdir('auto_screenshots')


def on_click(x, y, button, pressed):
    """
    This is a function to record repetitive click tasks in one go.
    This is meant to be run once during development in order to produce a csv that shouldn't need to be changed.
    Make sure you have your RuneScape environment set up to match what it will be in production.
    It also saves a screenshot of the region you clicked around in case you want to do some vision stuff later. If not,
    then those can be discarded.

    Run the script to START and left click anywhere to END. The ending click will not be recorded.
    """

    if button == mouse.Button.left and pressed:
        s = time.time()
        mouse_loc = pg.position()
        try:
            df = pd.read_csv('click_log.csv', index_col=0)
        except FileNotFoundError:
            df = pd.DataFrame(columns=[x, y, time])
        frame_diff = 100
        box = (mouse_loc[0] - frame_diff, mouse_loc[1] - frame_diff,
               frame_diff * 2, frame_diff * 2)
        pg.screenshot(f'auto_screenshots/mouse_shot_{df.index[-1] + 1}.png', region=box)
        df = df.append({
                           'x': x,
                           'y': y,
                           'time': s}, ignore_index=True)
        df.to_csv('click`_log.csv')
        print(df)
        return True  # Returning False if you need to stop the program when Left clicked.
    elif button == mouse.Button.right and pressed:
        print('stopping')
        return False


listener = mouse.Listener(on_click=on_click)
listener.start()
listener.join()
