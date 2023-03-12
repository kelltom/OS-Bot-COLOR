import pickle
from pathlib import Path

import pynput.keyboard as keyboard

SETTINGS_PATH = Path(__file__).parent.parent.joinpath("settings.pickle")


def set(key, value):
    """
    Writes a value to the settings file based on a key. The value can be any type.
    """
    # Open the file and load the data
    try:
        with open(SETTINGS_PATH, "rb") as f:
            data = pickle.load(f)
    except FileNotFoundError:
        data = {}
    # Update the value in the given key
    data[key] = value
    # Save the data back to the file
    with open(SETTINGS_PATH, "wb") as f:
        pickle.dump(data, f)


def get(key):
    """
    Retrieves a value from the settings file based on a key.
    """
    # Open the file and load the data
    try:
        with open(SETTINGS_PATH, "rb") as f:
            data: dict = pickle.load(f)
    except FileNotFoundError:
        return None
    # Return the value at the given key
    return data.get(key)


def delete(key):
    """
    Deletes a value from the settings file based on a key.
    """
    # Open the file and load the data
    try:
        with open(SETTINGS_PATH, "rb") as f:
            data = pickle.load(f)
    except FileNotFoundError:
        return
    # Delete the given key
    del data[key]
    # Save the data back to the file
    with open(SETTINGS_PATH, "wb") as f:
        pickle.dump(data, f)


default_keybind = {keyboard.Key.shift, keyboard.Key.enter}


def keybind_to_text(current_keys):
    hotkeys = []
    for key in current_keys:
        match key:
            case keyboard.Key.enter:
                hotkeys.append("↵")
            case keyboard.Key.space:
                hotkeys.append("␣")
            case keyboard.Key.ctrl | keyboard.Key.ctrl_l | keyboard.Key.ctrl_r:
                hotkeys.append("^")
            case keyboard.Key.alt | keyboard.Key.alt_l | keyboard.Key.alt_r:
                hotkeys.append("⌥")
            case keyboard.Key.shift | keyboard.Key.shift_l | keyboard.Key.shift_r:
                hotkeys.append("⇧")
            case keyboard.Key.cmd | keyboard.Key.cmd_l | keyboard.Key.cmd_r:
                hotkeys.append("⌘")
            case keyboard.Key.caps_lock:
                hotkeys.append("⇪")
            case keyboard.Key.tab:
                hotkeys.append("⇥")
            case keyboard.Key.backspace:
                hotkeys.append("⌫")
            case _:
                hotkeys.append(key)

    return " + ".join(map(str, hotkeys)).replace("'", "")
