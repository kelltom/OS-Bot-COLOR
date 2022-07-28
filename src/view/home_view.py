import customtkinter


class HomeView(customtkinter.CTkFrame):
    def __init__(self, parent, main):
        super().__init__(parent)
        self.main = main

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Spacing
        self.grid_rowconfigure(1, weight=0)  # - Title
        self.grid_rowconfigure(2, weight=0)  # - Logo
        self.grid_rowconfigure(2, weight=0)  # - Note
        self.grid_rowconfigure(3, weight=1)  # Spacing

        # Title label
        self.label_title = customtkinter.CTkLabel(master=self,
                                                  text="Welcome to OSRS Bot COLOR!",
                                                  text_font=("Roboto Medium", 18))
        self.label_title.grid(row=1, column=0, sticky="nwes", padx=15, pady=15)

        # Description label
        self.note = ("Select a game on the left to start. Explain some more about the bot. Add a logo here if possible.")
        self.label_note = customtkinter.CTkLabel(master=self,
                                                 text=self.note,
                                                 text_font=("Roboto", 12))
        self.label_note.bind('<Configure>', lambda e: self.label_note.configure(wraplength=self.label_note.winfo_width()-20))
        self.label_note.grid(row=3, column=0, sticky="nwes", padx=15, pady=(0, 15))
