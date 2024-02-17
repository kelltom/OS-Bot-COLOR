"""
The OSRSJagexAccountBot class for launching bots via Runelite for a Jagex Account
"""
from abc import ABCMeta
import wmi
import pywinctl
import pyautogui

from model.runelite_bot import RuneLiteBot, RuneLiteWindow

ACCOUNTS_FILE = "./account_names.txt"

def read_accounts_file_lines(file_path=ACCOUNTS_FILE):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        return lines
    except FileNotFoundError:
        print(f"Account Names '{file_path}' not found. Please ensure you execute OSBC.py from the root directory.")
        return []

class OSRSJagexAccountBot(RuneLiteBot, metaclass=ABCMeta):
    win: RuneLiteWindow = None

    def __init__(self, bot_title, description, account_name=None, debug=False) -> None:
        """
        account_name: Allows an override of the accounts file by specifying the exact account name
        debug: If True, prints additional information on processes if RuneLite was not found
        """
        try:
            super().__init__("OSRS", bot_title, description, window=RuneLiteWindow("RuneLite"))
        except:
            print("No default RuneLite process, looking for others.") if debug else ""

        if not account_name:
            print("Looking for a Runelite instance running for any listed account") if debug else ""
        else:
            super().__init__("OSRS", bot_title, description, window=window)
        
        accounts = read_accounts_file_lines()
        if not accounts:
            raise Exception("No accounts found. Cannot instantiate bot.")
        
        for account_name in accounts:
            window_name = f"RuneLite - {account_name}"
            print(f"Looking for '{window_name}'") if debug else ""
            if window := pywinctl.getWindowsWithTitle(window_name):
                super().__init__("OSRS", bot_title, description, window=RuneLiteWindow(window_name))
        if not window:
            if not debug:
                raise Exception("No runeline version found. Please ensure you're logged in.")
            else:
                print("Printing RuneLite processes... This may take some time")
                print("Please ensure the account you'd like to run is listed in your accounts")
                for window in pyautogui.getAllWindows():
                    if window.title and "runelite" in window.title.lower():  
                        print(window.title)


