import customtkinter
import os
from pathlib import Path
import pyautogui as pag
import shutil
from tkinter.filedialog import askopenfilename


class HomeView(customtkinter.CTkFrame):
    def __init__(self, parent, main):
        super().__init__(parent)
        self.main = main

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Spacing
        self.grid_rowconfigure(1, weight=0)  # - Title
        self.grid_rowconfigure(2, weight=0)  # - Note
        self.grid_rowconfigure(3, weight=0)  # - Warning
        self.grid_rowconfigure(4, weight=0)  # - File Loc
        self.grid_rowconfigure(5, weight=0)  # - Replace Btn
        self.grid_rowconfigure(6, weight=0)  # - Skip Btn
        self.grid_rowconfigure(7, weight=0)  # - Status
        self.grid_rowconfigure(8, weight=1)  # Spacing

        # Title label
        self.label_title = customtkinter.CTkLabel(master=self,
                                                  text="Welcome to OSRS Bot COLOR!",
                                                  text_font=("Roboto Medium", 18))
        self.label_title.grid(row=1, column=0, sticky="nwes", padx=15, pady=15)

        # Description label
        self.note = ("In order for these scripts to work, Runelite must be configured in a specific way. " +
                     "Use the buttons below to replace your current settings with our recommended ones, or skip this " +
                     "step if you know your settings are compatible.")
        self.label_note = customtkinter.CTkLabel(master=self,
                                                 text=self.note,
                                                 text_font=("Roboto", 12))
        self.label_note.bind('<Configure>', lambda e: self.label_note.configure(wraplength=self.label_note.winfo_width()-20))
        self.label_note.grid(row=2, column=0, sticky="nwes", padx=15, pady=(0, 15))

        # Warning label
        self.warning = ("WARNING: This will overwrite your current settings. If you'd like to save your settings, make " +
                        "a backup or log in to Runelite and sync your settings to the cloud. If you are already logged in, " +
                        "you are safe to ignore this warning.")
        self.label_warning = customtkinter.CTkLabel(master=self,
                                                    text=self.warning,
                                                    text_font=("Roboto", 10),
                                                    text_color="red")
        self.label_warning.bind('<Configure>', lambda e: self.label_warning.configure(wraplength=self.label_warning.winfo_width()-20))
        self.label_warning.grid(row=3, column=0, sticky="nwes", padx=15, pady=(0, 15))

        # File location label
        self.label_file_loc = customtkinter.CTkLabel(master=self,
                                                     text="Default location: C:/Users/[username]/.runelite/settings.properties")
        self.label_file_loc.bind('<Configure>', lambda e: self.label_file_loc.configure(wraplength=self.label_file_loc.winfo_width()-20))
        self.label_file_loc.grid(row=4, column=0, sticky="nwes", padx=15, pady=(0, 15))

        # Replace Btn
        self.btn_replace = customtkinter.CTkButton(master=self,
                                                   text="Replace Settings",
                                                   command=self.replace_settings)
        self.btn_replace.grid(row=5, column=0, sticky="nwes", padx=40, pady=(0, 15))

        # Skip Btn
        self.btn_skip = customtkinter.CTkButton(master=self,
                                                text="Skip",
                                                fg_color="gray40",
                                                hover_color="gray25",
                                                command=self.skip)
        self.btn_skip.grid(row=6, column=0, sticky="nwes", padx=40, pady=(0, 15))

        # Status label
        self.label_status = customtkinter.CTkLabel(master=self,
                                                   text="")
        self.label_status.grid(row=7, column=0, sticky="nwes")

        # TODO: Make a big frame to replace this view telling the user how to
        # configure their RS settings.

    def replace_settings(self):
        res = pag.confirm("Please close your game client before continuing.", title="Warning", buttons=["Done", "Cancel"])
        if res == "Cancel":
            return
        if loc := askopenfilename(initialdir=os.environ['USERPROFILE'],
                                  title="Select your Runelite settings file",
                                  filetypes=[("properties files", "*.properties")]):
            print(f"Replacing settings in {loc}...")
            try:
                settings_path = f"{str(Path().resolve())}\\src\\settings.properties"
                shutil.copyfile(settings_path, loc)
                self.label_status.configure(text="Settings replaced successfully.\nRestart Runelite client to apply changes.")
                self.main.enable_all_buttons()
            except Exception as e:
                self.label_status.configure(text="Error: Could not replace settings.", text_color="red")
                print(f"Could not replace settings: {e}")
        else:
            self.label_status.configure(text="No file selected.")

    def skip(self):
        self.label_status.configure(text="You may select a script from the menu.")
        self.main.enable_all_buttons()
