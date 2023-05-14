import customtkinter

from view.fonts.fonts import *


class HomeView(customtkinter.CTkFrame):
    def __init__(self, parent, main, game_title: str):
        """
        Creates a new HomeView object.
        Args:
            parent: The parent window.
            main: The main window.
            game_title: The title of the game.
        """
        super().__init__(parent)
        self.main = main

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Spacing
        self.grid_rowconfigure(1, weight=0)  # - Title
        self.grid_rowconfigure(2, weight=0)  # - Note
        self.grid_rowconfigure(3, weight=0)  # - Warning
        self.grid_rowconfigure(5, weight=0)  # - Skip Btn
        self.grid_rowconfigure(6, weight=0)  # - Status
        self.grid_rowconfigure(9, weight=1)  # Spacing

        # Title
        self.label_title = customtkinter.CTkLabel(self, text=f"{game_title}", font=title_font())
        self.label_title.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=15, pady=15)

        # Description label
        self.note = (
            "Basic HomeViews are not fully implemented yet. Once support for non-RuneLite games is added to OSBC, this will be updated. <Game description and"
            " user instructions here>. Click the button below to unlock the scripts."
        )
        self.label_note = customtkinter.CTkLabel(master=self, text=self.note, font=body_med_font())
        self.label_note.bind(
            "<Configure>",
            lambda e: self.label_note.configure(wraplength=self.label_note.winfo_width() - 20),
        )
        self.label_note.grid(row=2, column=0, sticky="nwes", padx=15, pady=(0, 15))

        # Warning label
        self.warning = "Warning message here for extra important instructions."
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

        # Skip Btn
        self.btn_skip = customtkinter.CTkButton(
            master=self,
            text="I Understand",
            font=button_med_font(),
            fg_color="gray40",
            hover_color="gray25",
            command=self.__skip,
        )
        self.btn_skip.grid(row=5, column=0, sticky="nwes", padx=40, pady=(0, 15))

        # Status label
        self.label_status = customtkinter.CTkLabel(master=self, text="", font=body_med_font())
        self.label_status.grid(row=6, column=0, sticky="nwes")
        self.label_status.bind(
            "<Configure>",
            lambda e: self.label_status.configure(wraplength=self.label_status.winfo_width() - 20),
        )

    def __skip(self):
        self.label_status.configure(text="You may select a script from the menu.", text_color="green")
        self.main.toggle_btn_state(enabled=True)
