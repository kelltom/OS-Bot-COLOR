import os
import pathlib
import time
from datetime import datetime

import pandas as pd
import pyautogui as pg
from pynput import mouse
from pynput.mouse import Listener as MouseListener

# Create folder to contain results
PATH = pathlib.Path(__file__).parent.resolve().joinpath(datetime.now().strftime("%Y_%m_%d - %I_%M_%S_%p"))
if not os.path.exists(PATH):
    os.makedirs(PATH)
    os.makedirs(f"{PATH}\\screenshots")
PATH = str(PATH).replace("\\", "/")


def on_click(x, y, button, pressed, terminate: bool = False):
    """
    This is a function to record repetitive click tasks in one go.
    This is meant to be run once during development in order to produce a csv that shouldn't need to be changed.
    Make sure you have your RuneScape environment set up to match what it will be in production.
    It also saves a screenshot of the region you clicked around in case you want to do some vision stuff later. If not,
    then those can be discarded.

    Run the script to START.
    """
    global curr_time
    if terminate:
        return False
    if pressed:
        s = time.time() - curr_time
        curr_time = time.time()
        mouse_loc = pg.position()
        try:
            df = pd.read_csv(f"{PATH}/click_log.csv", index_col=0)
        except FileNotFoundError:
            df = pd.DataFrame(columns=["x", "y", "button", "time"], index=[0])  # time is the relative number of seconds from last click
        # Create bounding box in 100px radius around mouse click
        frame_diff = 100
        box = (
            mouse_loc[0] - frame_diff,
            mouse_loc[1] - frame_diff,
            frame_diff * 2,
            frame_diff * 2,
        )
        if button == mouse.Button.left:
            button = "left"
        elif button == mouse.Button.right:
            button = "right"
        df = pd.concat(
            [
                df,
                pd.DataFrame({"x": x, "y": y, "button": button, "time": s}, index=[0]),
            ],
            axis=0,
        )
        pg.screenshot(f"{PATH}/screenshots/mouse_shot_{len(df.index)-1}.png", region=box)
        df.reset_index(inplace=True, drop=True)
        df.to_csv(f"{PATH}/click_log.csv")
        print(df)
        return True


def on_scroll(x, y, dx, dy):
    """
    Terminates the mouse_listener when the scroll wheel is used, thus ending the recording.
    """
    print("Stopping...")
    return False


print("Starting...")
curr_time = time.time()

# Set up log file
record = pd.DataFrame(columns=["x", "y", "button", "time"])
record.to_csv(f"{PATH}/click_log.csv")

# Setup the listener thread
mouse_listener = MouseListener(on_click=on_click, on_scroll=on_scroll)

# Start the thread and join so the script doesn't end early
mouse_listener.start()
mouse_listener.join()
