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

# Path to the folder containing the RuneLite settings files.
RL_SETTINGS_FOLDER_PATH: Path = Path(__file__).parent.parent.joinpath("runelite_settings")
# Path to default profile copy location.
TEMP_PROFILE_PATH = os.path.join(RL_SETTINGS_FOLDER_PATH, "temp.properties")
# Path to the file containing the paths to the executables for each game title.
EXECUTABLES_PATH: str = str(RL_SETTINGS_FOLDER_PATH.joinpath("executable_paths.json"))
# Path to the file containing the paths to the profile manager folders for each game title.
PM_PATH: str = str(RL_SETTINGS_FOLDER_PATH.joinpath("profile_manager_paths.json"))


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


def launch_runelite(properties_path: Path, game_title: str, use_profile_manager: bool, profile_name: str = "temp", callback: Callable = print) -> bool:
    """
    Launches the game with the specified RuneLite settings file. If it fails to find the executable, it will prompt the user to locate the executable.
    Args:
        properties_path: The path to the plugin properties file to use.
        game_title: The title of the game to launch. This value should be supplied by the bot's `game_title`
                    attribute.
        use_profile_manager: Whether to use the RuneLite Profile Manager to load the properties file.
                             Toggle True if using RuneLite v1.9.11 or newer.
        profile_name: The name of the profile to overwrite. This is only used if `use_profile_manager` is True. If you set this value, choose something
                      very specific & unique. If a profile is found with this name, it will be overwritten.
        callback: The function that is called with the output of the process. This function must accept a
                  string as its only positional argument. This may be called with keyword arguments (see notes).
    Returns:
        True if the game was launched successfully, False otherwise.
    Notes:
        The callback function may be called with keyword arguments. The following keyword arguments are
        passed to the callback function:
            - # TODO: ADD KEYWORD ARGS
    """
    # Try to read the file and parse the JSON data
    data = __read_json(path=EXECUTABLES_PATH, touch_file=True)

    # Check if the game's executable path exists in the JSON file
    game_title = game_title.lower()
    EXECPATH = data.get(game_title, "")

    # Check if executable file exists
    if not os.path.exists(EXECPATH):
        callback("Game executable not found. Please locate the executable.")
        EXECPATH = __locate_executable()
        if not EXECPATH:
            callback("File not selected.")
            return False
        data[game_title] = EXECPATH
        # Save the executable path to the JSON file
        with open(EXECUTABLES_PATH, "w") as f:
            json.dump(data, f)
            callback("Executable path saved.")

    # Alias the path to the properties file for readability
    src_path = properties_path

    """
    This conditional block decides how the plugin .properties file is loaded into the game.
    If `use_profile_manager` is True, a special profile is built and added directly to RuneLite.
    Otherwise, the legacy method takes place, where the properties file is copied within OSBC's
    filesystem and RuneLite is instructed to load the file from there.
    """
    if use_profile_manager:
        # Set up a new profile in the profile manager folder for the game
        dst_path = __configure_profile_manager(game_title, callback, profile_name)
        # Set the executable args to use the new profile manager command
        EXECARG1 = ""
        EXECARG2 = f"--profile={profile_name}"
    else:
        # Set the destination path to a temporary location in OSBC
        dst_path = TEMP_PROFILE_PATH
        # Set the executable args to use the legacy command
        EXECARG1 = "--clientargs"
        EXECARG2 = f"--config={dst_path} --sessionfile=bot_session"

    # If the destination path is None, the user failed to locate the profile manager folder.
    if dst_path is None:
        callback("Profile list not found. Reset and try again, or manually import a plugin profile into the RL Profile Manager.")
        return False

    shutil.copyfile(src_path, dst_path)

    # Launch the game
    if platform.system() == "Windows":
        subprocess.Popen([EXECPATH, EXECARG1, EXECARG2], creationflags=subprocess.DETACHED_PROCESS)
    else:
        subprocess.Popen([EXECPATH, EXECARG1, EXECARG2], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    callback("Game launched. Please wait until you've logged into the game before starting the bot.")
    return True


def reset_saved_paths(game_title: str, callback: Callable = print):
    """
    Resets the saved executable/profile storage paths for the specified game title.
    Args:
        game_title: The title of the game to reset the executable/profile storage paths for.
        callback: The function that is called with the output of the process. This function must accept a
                  string as its only positional argument.
    """
    try:
        key = game_title.lower()
        if os.path.exists(EXECUTABLES_PATH):
            __del_key_from_json(EXECUTABLES_PATH, key)
        if os.path.exists(PM_PATH):
            __del_key_from_json(PM_PATH, key)

        callback(text=f"{game_title} executable & profile storage paths has been reset.")
    except Exception as e:
        callback(text=f"An error occurred while resetting the storage paths: {str(e)}")


def __configure_profile_manager(game_title: str, callback: Callable, profile_name: str):
    """
    Sets up a new profile in the profile manager folder for the game. This function does the following:
        - If it is not saved in OSBC's settings, the user is prompted to locate the game's profile manager folder.
        - The `profiles.json` file is read from the folder. This file contains a list of all profiles that RuneLite
        is aware of. For each profile, we:
            - Save the ID to a list. This is used to generate a new unique ID for our new profile.
            - Set the `active` flag to False. This is so that the profile is not loaded when the game is launched.
            - Remove the profile if it has the same name as the profile we are creating. All profiles should have
            unique names and IDs in order to be launchable from the terminal.
        - A new profile is created with the specified name and a unique ID. If a profile with the same name already
        existed, we'll recycle its ID to prevent endless file creation. This profile is set to `active`.
        - The `profiles.json` file is saved back to the folder.
    Args:
        game_title: The title of the game to set up a new profile for.
        callback: The callback used by the parent function.
        profile_name: The name of the profile to create.
    Returns:
        The path (including its filename) that the new profile should be saved to.
    """
    # Get the profiles folder
    pm_data = __read_json(path=PM_PATH, touch_file=True)
    profiles_folder_path = pm_data.get(game_title, "")
    if not os.path.exists(profiles_folder_path):
        callback("Profile folder not found. Please locate the folder.")
        profiles_folder_path = __locate_folder(prompt="IMPORTANT: Select the Profile Manager folder (e.g., C:\\Users\\<user>\\.runelite\\profiles2).")
        if not profiles_folder_path:
            callback("Folder not selected.")
            return
        pm_data[game_title] = profiles_folder_path
        with open(PM_PATH, "w") as f:
            json.dump(pm_data, f)
            callback("Profile folder saved.")

    # Open the `profiles.json` file
    profiles_json_path = Path(profiles_folder_path).joinpath("profiles.json")
    if not os.path.exists(profiles_json_path):
        callback(
            "Profile list not found. You may have selected the wrong folder. Reset and try again, or manually import a plugin profile into the RL Profile"
            " Manager."
        )
        return
    with open(profiles_json_path, "r") as f:
        profiles: dict = json.load(f)

    # We need to record all IDs to ensure we don't create a duplicate
    # IDs span all profiles regardless of their name
    all_ids = []
    tmp_profile_id = None
    for profile in profiles["profiles"]:
        if profile["name"] == profile_name:
            tmp_profile_id = profile["id"]
            callback("Removing duplicate profile.")
            profiles["profiles"].remove(profile)
            continue
        profile["active"] = False
        all_ids.append(profile["id"])

    # Create a new profile record
    callback("Creating new profile.")
    if tmp_profile_id is None:
        tmp_profile_id = 0
    while tmp_profile_id in all_ids:
        tmp_profile_id += 1
    tmp_profile = {"id": tmp_profile_id, "name": profile_name, "sync": False, "active": True, "rev": -1}
    profiles["profiles"].append(tmp_profile)

    # Save the JSON file
    with open(profiles_json_path, "w") as f:
        json.dump(profiles, f)
        callback("Profile list updated.")

    # Append the id to the name of the new profile file
    tmp_filename = f"{profile_name}-{tmp_profile_id}.properties"
    return os.path.join(profiles_folder_path, tmp_filename)


def __del_key_from_json(filename: str, key: str):
    """
    Deletes the specified key from a JSON file.
    """
    try:
        with open(filename, "r") as f:
            data = json.load(f)

        if key in data:
            del data[key]
            with open(filename, "w") as f:
                json.dump(data, f)
            print(f"Key '{key}' deleted from file '{filename}'")
        else:
            print(f"Key '{key}' not found in file '{filename}'")

    except FileNotFoundError:
        print(f"File '{filename}' not found")
    except json.JSONDecodeError:
        print(f"File '{filename}' is not valid JSON")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


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


def __locate_folder(prompt: str) -> Union[str, None]:
    """
    Opens a folder dialog to allow the user to locate a folder path.
    """
    root = tk.Tk()
    root.withdraw()
    # TODO: May need to make separate prompts for Linux
    folder_path = filedialog.askdirectory(title=prompt)
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


def __read_json(path: str, touch_file: bool) -> dict:
    """
    Reads the JSON file at the specified path and returns the data as a dictionary.
    Args:
        path: The path to the JSON file.
        touch_file: Whether to create the file if it doesn't exist.
    Returns:
        The data from the JSON file as a dictionary.
    """
    # Try to read the file and parse the JSON data
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = {}
    if touch_file and not os.path.exists(path):
        Path(path).touch()
    return data
