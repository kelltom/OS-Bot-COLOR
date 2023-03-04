import json
import os
import platform
import shutil
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Callable, Union

import psutil

runelite_settings_folder: Path = Path(__file__).parent.parent.joinpath("runelite_settings")
executable_paths: str = str(runelite_settings_folder.joinpath("executable_paths.json"))


class Launchable:
    """
    Classes that inherit from this class must implement the launch_game() method.
    """

    def launch_game():
        raise NotImplementedError()


def is_program_running(program_name):
    for proc in psutil.process_iter():
        try:
            proc_name = proc.name().split(".")[0]
            if proc_name == program_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            print("Failed to check if program is running: ", e)
            print("Please report this error to the developer.")
    return False


def launch_runelite_with_settings(settings_file: Path, game_title: str, use_profile_manager: bool, callback: Callable=print, verbose: bool=True) -> Union[bool, None]:
    """
    Launches the game with the specified RuneLite settings file. If it fails to
    find the executable, it will prompt the user to locate the executable.
    Args:
        settings_file: The path to the settings file to use. If not specified, the default
                       settings file will be selected according to the bot's game_title.
                       E.g., if the game title is "OSRS", the default settings file
                       will be "osrs_settings.properties".
        game_title: The title of the game to launch. This is used to determine which game client to launch.
        use_profile_manager: Whether to use the RuneLite Profile Manager to load the settings file.
                             Toggle True if using RuneLite v1.9.11 or newer.
        callback: The function that is called with the output of the process. This function must accept a
                  string as its only positional argument.
        verbose: Sets the verbosity of the output sent to the callback function. If True, all details of
                 the process will be sent to the callback function. If False, only the final output will
                 be sent to the callback function.
    Returns:
        True if the game was launched successfully.
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
    game_title = game_title.lower()
    EXECPATH = data.get(game_title, "")

    # Check if executable file exists
    if not os.path.exists(EXECPATH):
        callback("Game executable not found. Please locate the executable.")
        EXECPATH = __locate_executable()
        if not EXECPATH:
            callback("File not selected.")
            return
        data[game_title] = EXECPATH
        with open(executable_paths, "w") as f:
            json.dump(data, f)
            callback("Executable path saved.")

    # Save settings file to temp
    if not settings_file:
        settings_file = runelite_settings_folder.joinpath(f"{game_title}_settings.properties")
    src_path = settings_file
    if use_profile_manager:
        # TODO: CLEAN THIS UP

        # Get the profiles folder
        profiles_folder = data.get(f"{game_title}_profiles", "")
        if not os.path.exists(profiles_folder):
            callback("Profile folder not found. Please locate the folder.")
            profiles_folder = __locate_folder()
            if not profiles_folder:
                callback("Folder not selected.")
                return
            data[f"{game_title}_profiles"] = profiles_folder
            with open(executable_paths, "w") as f:
                json.dump(data, f)
                callback("Profile folder saved.")

        # Open the `profiles.json` file
        profiles_json = Path(profiles_folder).joinpath("profiles.json")
        if not os.path.exists(profiles_json):
            callback("Profile list not found. Please create a profile in the Profile Manager.")
            return
        with open(profiles_json, "r") as f:
            profiles: dict = json.load(f)

        # In the key called "profiles" is a list of dictionaries. Each dictionary contains the name of the profile and an id. Iterate through all profiles and record the ids to a list. If the name of the profile is "temp", record the id in another variable.
        profile_ids = []
        tmp_profile_id = None
        for profile in profiles["profiles"]:
            profile["active"] = False
            profile_ids.append(profile["id"])
            if profile["name"] == "temp":
                callback("Found temp profile. Recording id and activating profile.")
                tmp_profile_id = profile["id"]
                profile["active"] = True

        # If tmp_profile_id is None, generate an ID and create a new record in the JSON file. Else, do nothing
        if tmp_profile_id is None:
            callback("Temp profile not found. Creating new profile...")
            tmp_profile_id = "123456" # TODO: Generate a random ID that is not in the list of profile ids
            # Create a new profile record
            tmp_profile = {
                "id": tmp_profile_id,
                "name": "temp",
                "sync": False,
                "active": True,
                "rev": -1
            }
            profiles["profiles"].append(tmp_profile)

        # Save the JSON file
        with open(profiles_json, "w") as f:
            json.dump(profiles, f)
            callback("Profile list updated.")

        # Append the id to the name of the temp file
        tmp_filename = f"temp-{tmp_profile_id}.properties"
        dst_path = os.path.join(profiles_folder, tmp_filename)
        EXECARG2 = "--profile=temp"
    else:
        dst_path = os.path.join(runelite_settings_folder, "temp.properties")
        EXECARG2 = f"--config={dst_path} --sessionfile=bot_session"
    shutil.copyfile(src_path, dst_path)

    # Executable args for runelite to direct the client to launch with bot settings
    EXECARG1 = "--clientargs"

    # Launch the game
    if platform.system() == "Windows":
        subprocess.Popen([EXECPATH, EXECARG1, EXECARG2], creationflags=subprocess.DETACHED_PROCESS)
    else:
        subprocess.Popen([EXECPATH, EXECARG1, EXECARG2], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    callback("Game launched. Please wait until you've logged into the game before starting the bot.")
    return True


def reset_saved_path(game_title: str, callback: Callable = print):
    """
    Resets the saved executable/profile storage paths for the specified game title.
    Args:
        game_title: The title of the game to reset the executable/profile storage paths for.
        callback: The function that is called with the output of the process. This function must accept a
                  string as its only positional argument.
    """
    try:
        with open(executable_paths, "r") as f:
            data = json.load(f)
            key = game_title.lower()
            if key in data:
                del data[key]
            if f"{key}_profiles" in data:
                    del data[f"{key}_profiles"]
            callback(text=f"{game_title} executable & profile storage paths has been reset.")
    except (FileNotFoundError):
        callback(text="No recorded paths found. Nothing to reset.")
        return
    except (json.decoder.JSONDecodeError, KeyError):
        callback(text="Executable path file may be corrupted. Please delete it and try again.")
        return

    with open(executable_paths, "w") as f:
        json.dump(data, f)


def __locate_executable() -> Union[str, None]:
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


def __locate_folder() -> Union[str, None]:
    """
    Opens a folder dialog to allow the user to locate the game executable.
    """
    root = tk.Tk()
    root.withdraw()
    # TODO: May need to make separate prompts for Linux
    folder_path = filedialog.askdirectory(title="Locate the `profile2` folder")
    try:
        if not folder_path:
            root.destroy()
            return None
        folder_path = Path(folder_path)
    except TypeError:
        root.destroy()
        return None
    path_str = str(folder_path)
    root.destroy()
    return path_str
