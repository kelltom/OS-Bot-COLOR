from pathlib import Path
from PIL import ImageTk, Image
from subprocess import DETACHED_PROCESS, Popen
from tkinter.filedialog import askopenfilename
import customtkinter
import os
import shutil


class OSRSHomeView(customtkinter.CTkFrame):
    def __init__(self, parent, main):
        super().__init__(parent)
        self.main = main

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Spacing
        self.grid_rowconfigure(1, weight=0)  # - Title
        self.grid_rowconfigure(2, weight=0)  # - Note
        self.grid_rowconfigure(3, weight=0)  # - Warning
        self.grid_rowconfigure(5, weight=0)  # - Replace Btn
        self.grid_rowconfigure(6, weight=0)  # - Skip Btn
        self.grid_rowconfigure(7, weight=0)  # - Status
        self.grid_rowconfigure(8, weight=1)  # Spacing

        # # Logo
        # self.logo_path = Path(__file__).parent.parent.parent.resolve()
        # self.logo = ImageTk.PhotoImage(Image.open(f"{self.logo_path}/src/images/ui/osrs_logo.png").resize((268, 120), Image.LANCZOS))
        # self.label_logo = customtkinter.CTkLabel(self, image=self.logo)
        # self.label_logo.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=15, pady=15)

        # Title
        self.label_title = customtkinter.CTkLabel(self, text="Old School RuneScape", text_font=("Roboto", 24))
        self.label_title.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=15, pady=15)

        # Description label
        self.note = ("For these scripts to work, RuneLite must be configured in a specific way. " +
                     "Use the button below to launch RuneLite with pre-configured settings, or skip this " +
                     "step if you know your client is already configured.")
        self.label_note = customtkinter.CTkLabel(master=self,
                                                 text=self.note,
                                                 text_font=("Roboto", 12))
        self.label_note.bind('<Configure>', lambda e: self.label_note.configure(wraplength=self.label_note.winfo_width()-20))
        self.label_note.grid(row=2, column=0, sticky="nwes", padx=15, pady=(0, 15))

        # Warning label
        self.warning = ("Please only have one instance of RuneLite running at a time.")
        self.label_warning = customtkinter.CTkLabel(master=self,
                                                    text=self.warning,
                                                    text_font=("Roboto", 10),
                                                    text_color="orange")
        self.label_warning.bind('<Configure>', lambda e: self.label_warning.configure(wraplength=self.label_warning.winfo_width()-20))
        self.label_warning.grid(row=3, column=0, sticky="nwes", padx=15, pady=(0, 15))

        # Launch Btn
        self.btn_replace = customtkinter.CTkButton(master=self,
                                                   text="Launch RuneLite",
                                                   command=self.__launch_game_with_settings)
        self.btn_replace.grid(row=5, column=0, sticky="nwes", padx=40, pady=(0, 15))

        # Skip Btn
        self.btn_skip = customtkinter.CTkButton(master=self,
                                                text="Skip",
                                                fg_color="gray40",
                                                hover_color="gray25",
                                                command=self.__skip)
        self.btn_skip.grid(row=6, column=0, sticky="nwes", padx=40, pady=(0, 15))

        # Status label
        self.label_status = customtkinter.CTkLabel(master=self,
                                                   text="")
        self.label_status.grid(row=7, column=0, sticky="nwes")
        self.label_status.bind('<Configure>', lambda e: self.label_status.configure(wraplength=self.label_status.winfo_width()-20))

    def __launch_game_with_settings(self):
        '''
        Launches the game with the specified RuneLite settings file. If it fails to
        find the executable, it will prompt the user to locate the executable.
        '''
        # src path for our runelite bot settings
        PATH = Path(__file__).parent.parent.resolve()

        # currently logged in user <windows>
        currentUser = os.getlogin()

        # executable path for runelite
        EXECPATH = f"C:\\Users\\{currentUser}\\AppData\\Local\\RuneLite\\RuneLite.exe"

        if not os.path.exists(EXECPATH):
            # if the executable is not found, prompt the user to locate it
            self.label_status.configure(text="RuneLite not found. Please locate the executable.", text_color="orange")
            EXECPATH = askopenfilename(initialdir=os.environ['USERPROFILE'],
                                       title="RuneLite not found. Please locate the executable",
                                       filetypes=[("exe files", "*.exe")])
            if not EXECPATH:
                self.label_status.configure(text="Error: Could not launch RuneLite.", text_color="red")
                return

        # save settings file to temp
        shutil.copyfile(f"{PATH}\\runelite_settings\\settings.properties", f"{PATH}\\runelite_settings\\temp.properties")

        # executable args for runelite to direct the client to launch with bot settings
        EXECARG1 = "--clientargs"
        EXECARG2 = f"--config={PATH}\\runelite_settings\\temp.properties --sessionfile=bot_session"

        self.main.toggle_btn_state(enabled=True)
        # TODO: Try to verify this launched successfully, can't seem to get a return code
        Popen([EXECPATH, EXECARG1, EXECARG2], creationflags=DETACHED_PROCESS)
        self.label_status.configure(text="You may select a script from the menu.", text_color="green")

    def __skip(self):
        self.label_status.configure(text="You may select a script from the menu.", text_color="green")
        self.main.toggle_btn_state(enabled=True)
