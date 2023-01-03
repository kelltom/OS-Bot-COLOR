import sys
import json
import os
import platform
import shutil
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

runelite_settings_folder: Path = Path(__file__).parent.parent.joinpath("runelite_settings")
executable_paths: str = str(runelite_settings_folder.joinpath("executable_paths.json"))

# TODO: add function for building a settings file


class Launchable:
    """
    Classes that inherit from this class must implement the launch_game() method.
    """

    def launch_game():
        raise NotImplementedError()


def launch_runelite_with_settings(bot, settings_file: Path):
    """
    Launches the game with the specified RuneLite settings file. If it fails to
    find the executable, it will prompt the user to locate the executable.
    Args:
        bot: The bot object.
        settings_file: The path to the settings file to use. If not specified, the default
                       settings file will be selected according to the bot's game_title.
                       E.g., if the game title is "OSRS", the default settings file
                       will be "osrs_settings.properties".
    """
    # Try to read the file and parse the JSON data
    try:
        with open(executable_paths, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = {}

    # If the file doesn't exist, create it
    if not os.path.exists(executable_paths):
        Path(executable_paths).touch()

    # Check if the game's executable path exists in the JSON file
    key = bot.game_title.lower()
    EXECPATH = data.get(key, "")

    if not os.path.exists(EXECPATH) and sys.platform == 'darwin':
        bot.log_msg('''
        Macos specific: path to executable not found, please manually replace the content 
        of the file OSRS-Bot-COLOR/src/runelite_settings/executable_paths.json

        with
        
        {"osrs": "/Applications/RuneLite.app/Contents/MacOS/RuneLite"}
        
        ''')

    # Check if executable file exists
    elif not os.path.exists(EXECPATH):
        bot.log_msg("Game executable not found. Please locate the executable.")
        EXECPATH = __locate_executable()
        if not EXECPATH:
            bot.log_msg("File not selected.")
            return
        data[key] = EXECPATH
        with open(executable_paths, "w") as f:
            json.dump(data, f)
            bot.log_msg("Executable path saved.")

    # Save settings file to temp
    if settings_file:
        bot.log_msg("Launching with custom settings.")
    else:
        bot.log_msg(f"Launching with base {bot.game_title} settings file.")
        settings_file = runelite_settings_folder.joinpath(f"{bot.game_title}_settings.properties")
    src_path = settings_file
    dst_path = os.path.join(runelite_settings_folder, "temp.properties")
    shutil.copyfile(src_path, dst_path)

    # Executable args for runelite to direct the client to launch with bot settings
    EXECARG1 = "--clientargs"
    EXECARG2 = f"--config={dst_path} --sessionfile=bot_session"

    # Launch the game
    if platform.system() == "Windows":
        subprocess.Popen([EXECPATH, EXECARG1, EXECARG2], creationflags=subprocess.DETACHED_PROCESS)
    else:
        subprocess.Popen([EXECPATH, EXECARG1, EXECARG2], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    bot.log_msg("Game launched. Please wait until you've logged into the game before starting the bot.")


def __locate_executable():
    """
    Opens a file dialog to allow the user to locate the game executable.
    """
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select game executable file", filetypes=[("exe files", "*.exe"), ("AppImage files", "*.AppImage"), ("Java files", "*.jar")]
    )
    try:
        if not file_path:
            root.destroy()
            return None
        file_path = Path(file_path)
    except TypeError:
        root.destroy()
        return None
    path_str = str(file_path)
    root.destroy()
    return path_str
