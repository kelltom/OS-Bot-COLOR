import customtkinter

import utilities.game_launcher as launcher
from view.fonts.fonts import *


class RuneLiteHomeView(customtkinter.CTkFrame):
    def __init__(self, parent, main, game_title: str):
        """
        Creates a new RuneLiteHomeView object.
        Args:
            parent: The parent window.
            main: The main window.
            game_title: The title of the game (E.g., "OSRS").
        """
        super().__init__(parent)
        self.main = main
        self.__game_title = game_title

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
        self.label_title = customtkinter.CTkLabel(self, text=f"{game_title}", font=title_font())
        self.label_title.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=15, pady=15)

        # Description label
        self.note = (
            "For these scripts to work, RuneLite must be configured in a specific way. "
            + "Use the button below to launch RuneLite with pre-configured settings, or skip this "
            + "step if you know your client is already configured. If a script has a rocket icon next to its name, RuneLite should instead be launched using"
            " the dedicated button provided by the script."
        )
        self.label_note = customtkinter.CTkLabel(master=self, text=self.note, font=body_med_font())
        self.label_note.bind(
            "<Configure>",
            lambda e: self.label_note.configure(wraplength=self.label_note.winfo_width() - 20),
        )
        self.label_note.grid(row=2, column=0, sticky="nwes", padx=15, pady=(0, 15))

        # Warning label
        self.warning = "In your game settings, ensure that status orbs are enabled, shift-drop is enabled, and XP display is set to 'permanent'."
        self.label_warning = customtkinter.CTkLabel(
            master=self,
            text=self.warning,
            font=body_med_font(),
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
            font=button_med_font(),
            command=self.__launch,
        )
        self.btn_replace.grid(row=5, column=0, sticky="nwes", padx=40, pady=(0, 15))

        # Skip Btn
        self.btn_skip = customtkinter.CTkButton(
            master=self,
            text="Skip",
            font=button_med_font(),
            fg_color="gray40",
            hover_color="gray25",
            command=self.__skip,
        )
        self.btn_skip.grid(row=6, column=0, sticky="nwes", padx=40, pady=(0, 15))

        # Reset Btn
        self.btn_skip = customtkinter.CTkButton(
            master=self,
            text="Reset Saved Path",
            font=button_med_font(),
            fg_color="DarkRed",
            hover_color="red",
            command=self.__reset_saved_path,
        )
        self.btn_skip.grid(row=7, column=0, sticky="ns", padx=10, pady=(0, 15))

        # Status label
        self.label_status = customtkinter.CTkLabel(master=self, text="", font=body_med_font())
        self.label_status.grid(row=8, column=0, sticky="nwes")
        self.label_status.bind(
            "<Configure>",
            lambda e: self.label_status.configure(wraplength=self.label_status.winfo_width() - 20),
        )

    def __launch(self):
        """
        Launches the game with the default RuneLite settings file.
        """
        path = launcher.RL_SETTINGS_FOLDER_PATH.joinpath(f"{self.__game_title.lower()}_settings.properties")
        use_profile_manager = self.__game_title.lower() in ["osrs"]  # TODO: This is a weak solution for identifying games that use the profile manager.
        success = launcher.launch_runelite(
            properties_path=path,
            game_title=self.__game_title,
            use_profile_manager=use_profile_manager,
            callback=self.__update_label,
        )
        if not success:
            return
        self.label_status.configure(text="You may select a script from the menu.", text_color="green")
        self.main.toggle_btn_state(enabled=True)

    def __reset_saved_path(self):
        launcher.reset_saved_paths(self.__game_title, self.__update_label)

    def __skip(self):
        """
        Handler for the 'skip' button. This will simply update the status label and enable the script selection buttons,
        bypassing the need to launch RuneLite.
        """
        self.label_status.configure(text="You may select a script from the menu.", text_color="green")
        self.main.toggle_btn_state(enabled=True)

    def __update_label(self, text: str):
        self.label_status.configure(text=text, text_color="white")
