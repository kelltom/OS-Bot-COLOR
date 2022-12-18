import contextlib
import json
import os
import platform
import shutil
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from tkinter.filedialog import askopenfilename

import customtkinter


class RuneLiteHomeView(customtkinter.CTkFrame):
    def __init__(self, parent, main, game_title: str, game_abbreviation: str):
        """
        Creates a new RuneLiteHomeView object.
        Args:
            parent: The parent window.
            main: The main window.
            game_title: The title of the game (E.g., "Old School RuneScape").
            game_abbreviation: The abbreviation of the game (E.g., "OSRS").
        """
        super().__init__(parent)
        self.main = main
        self.__game_abbreviation = game_abbreviation

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Spacing
        self.grid_rowconfigure(1, weight=0)  # - Title
        self.grid_rowconfigure(2, weight=0)  # - Note
        self.grid_rowconfigure(3, weight=0)  # - Warning
        self.grid_rowconfigure(5, weight=0)  # - Replace Btn
        self.grid_rowconfigure(6, weight=0)  # - Skip Btn
        self.grid_rowconfigure(7, weight=0)  # - Reset Btn
        self.grid_rowconfigure(8, weight=0)  # - Status
        self.grid_rowconfigure(9, weight=1)  # Spacing

        # Logo
        # self.logo_path = Path(__file__).parent.parent.parent.resolve()
        # self.logo = ImageTk.PhotoImage(Image.open(f"{self.logo_path}/src/images/ui/osrs_logo.png").resize((268, 120), Image.LANCZOS))
        # self.label_logo = customtkinter.CTkLabel(self, image=self.logo)
        # self.label_logo.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=15, pady=15)

        # Title
        self.label_title = customtkinter.CTkLabel(self, text=f"{game_title}", text_font=("Roboto", 24))
        self.label_title.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=15, pady=15)

        # Description label
        self.note = (
            "For these scripts to work, RuneLite must be configured in a specific way. "
            + "Use the button below to launch RuneLite with pre-configured settings, or skip this "
            + "step if you know your client is already configured."
        )
        self.label_note = customtkinter.CTkLabel(master=self, text=self.note, text_font=("Roboto", 12))
        self.label_note.bind(
            "<Configure>",
            lambda e: self.label_note.configure(wraplength=self.label_note.winfo_width() - 20),
        )
        self.label_note.grid(row=2, column=0, sticky="nwes", padx=15, pady=(0, 15))

        # Warning label
        self.warning = (
            "Please only have one instance of RuneLite running at a time. \nIn your game settings, ensure that "
            + "UI elements are NOT trasparent, orbs are enabled, shift-drop is enabled, and XP display is "
            + "set to 'permanent'."
        )
        self.label_warning = customtkinter.CTkLabel(
            master=self,
            text=self.warning,
            text_font=("Roboto", 10),
            text_color="orange",
        )
        self.label_warning.bind(
            "<Configure>",
            lambda e: self.label_warning.configure(wraplength=self.label_warning.winfo_width() - 20),
        )
        self.label_warning.grid(row=3, column=0, sticky="nwes", padx=15, pady=(0, 15))

        # Launch Btn
        self.btn_replace = customtkinter.CTkButton(
            master=self,
            text=f"Launch {game_title}",
            command=self.__launch_game_with_settings,
        )
        self.btn_replace.grid(row=5, column=0, sticky="nwes", padx=40, pady=(0, 15))

        # Skip Btn
        self.btn_skip = customtkinter.CTkButton(
            master=self,
            text="Skip",
            fg_color="gray40",
            hover_color="gray25",
            command=self.__skip,
        )
        self.btn_skip.grid(row=6, column=0, sticky="nwes", padx=40, pady=(0, 15))

        # Reset Btn
        self.btn_skip = customtkinter.CTkButton(
            master=self,
            text="Reset Saved Paths",
            fg_color="DarkRed",
            hover_color="red",
            command=self.__reset_saved_paths,
        )
        self.btn_skip.grid(row=7, column=0, sticky="ns", padx=10, pady=(0, 15))

        # Status label
        self.label_status = customtkinter.CTkLabel(master=self, text="")
        self.label_status.grid(row=8, column=0, sticky="nwes")
        self.label_status.bind(
            "<Configure>",
            lambda e: self.label_status.configure(wraplength=self.label_status.winfo_width() - 20),
        )

    def __launch_game_with_settings(self):
        """
        Launches the game with the specified RuneLite settings file. If it fails to
        find the executable, it will prompt the user to locate the executable.
        """
        # Load the JSON file
        executable_paths = str(Path(__file__).parent.joinpath("executable_paths.json"))
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
        key = self.__game_abbreviation.lower()
        EXECPATH = data.get(key, "")

        # Check if executable file exists
        if not os.path.exists(EXECPATH):
            self.label_status.configure(
                text="RuneLite not found. Please locate the executable.",
                text_color="orange",
            )
            EXECPATH = self.__locate_executable()
            if not EXECPATH:
                self.label_status.configure(text="File not selected.", text_color="orange")
                return
            data[key] = EXECPATH
            with open(executable_paths, "w") as f:
                json.dump(data, f)

        # Save settings file to temp
        PATH = Path(__file__).parent.parent.resolve()
        src_path = os.path.join(PATH, "runelite_settings", f"{key}_settings.properties")
        dst_path = os.path.join(PATH, "runelite_settings", "temp.properties")
        shutil.copyfile(src_path, dst_path)

        # Executable args for runelite to direct the client to launch with bot settings
        EXECARG1 = "--clientargs"
        EXECARG2 = f"--config={dst_path} --sessionfile=bot_session"

        # Launch the game
        if platform.system() == "Windows":
            print(f"Executing: {EXECPATH} {EXECARG1} {EXECARG2}")
            subprocess.Popen([EXECPATH, EXECARG1, EXECARG2], creationflags=subprocess.DETACHED_PROCESS)
        else:
            subprocess.Popen([EXECPATH, EXECARG1, EXECARG2], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.label_status.configure(text="You may select a script from the menu.", text_color="green")
        self.main.toggle_btn_state(enabled=True)

    def __locate_executable(self):
        """
        Opens a file dialog to allow the user to locate the game executable.
        """
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title="Select game executable file", filetypes=[("exe files", "*.exe"), ("AppImage files", "*.AppImage")])
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

    def __skip(self):
        self.label_status.configure(text="You may select a script from the menu.", text_color="green")
        self.main.toggle_btn_state(enabled=True)

    def __reset_saved_paths(self):
        executable_paths = str(Path(__file__).parent.joinpath("executable_paths.json"))
        with contextlib.suppress(FileNotFoundError):
            Path(executable_paths).unlink()
        self.label_status.configure(text="Saved game executable paths have been reset.", text_color="green")
