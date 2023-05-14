import threading
import tkinter

import customtkinter

from utilities.sprite_scraper import SpriteScraper
from view.fonts.fonts import *

scraper = SpriteScraper()


class SpriteScraperView(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # - Title
        self.grid_rowconfigure(1, weight=0)  # - Label
        self.grid_rowconfigure(2, weight=0)  # - Entry
        self.grid_rowconfigure(3, weight=0)  # - Submit
        self.grid_rowconfigure(5, weight=0)  # - Radio Group
        self.grid_rowconfigure(6, weight=1)  # - Logs

        # Title
        self.search_label = customtkinter.CTkLabel(self, text="Search OSRS Wiki for Sprites")
        self.search_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Search instructions
        self.search_info = customtkinter.CTkLabel(self, text="Enter sprite names separated by commas")
        self.search_info.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Search entry
        self.search_entry = customtkinter.CTkEntry(self, placeholder_text="Ex: molten glass, bucket of sand")
        self.search_entry.grid(row=2, column=0, sticky="nsew", padx=40, pady=10)

        # Submit button
        self.search_submit_button = customtkinter.CTkButton(self, text="Submit", command=self.on_submit)
        self.search_submit_button.grid(row=3, column=0, sticky="nsew", padx=40, pady=(0, 20))

        # Radio Group
        self.radio_group = customtkinter.CTkFrame(self)
        self.radio_group.grid_columnconfigure(0, weight=1)
        self.radio_group.grid_columnconfigure(1, weight=1)
        self.radio_group.grid_rowconfigure(0, weight=1)
        self.radio_group.grid_rowconfigure(1, weight=1)
        self.radio_group.grid_rowconfigure(2, weight=1)
        self.radio_group.grid_rowconfigure(3, weight=1)

        # -- Radio Group Label
        self.lbl_radio_group = customtkinter.CTkLabel(master=self.radio_group, text="Select the type of sprites to download")
        self.lbl_radio_group.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=(10, 0))

        self.radio_var = tkinter.IntVar(self)

        # -- Radio Buttons
        self.radio_normal = customtkinter.CTkRadioButton(master=self.radio_group, text="", variable=self.radio_var, value=0)
        self.radio_bank = customtkinter.CTkRadioButton(master=self.radio_group, text="", variable=self.radio_var, value=1)
        self.radio_both = customtkinter.CTkRadioButton(master=self.radio_group, text="", variable=self.radio_var, value=2)
        self.radio_normal.grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.radio_bank.grid(row=2, column=0, sticky="e", padx=10, pady=10)
        self.radio_both.grid(row=3, column=0, sticky="e", padx=10, pady=(10, 20))

        # -- Radio Button Labels
        self.lbl_radio_normal = customtkinter.CTkLabel(master=self.radio_group, text="Normal")
        self.lbl_radio_bank = customtkinter.CTkLabel(master=self.radio_group, text="Bank")
        self.lbl_radio_both = customtkinter.CTkLabel(master=self.radio_group, text="Normal + Bank")
        self.lbl_radio_normal.grid(row=1, column=1, sticky="w", padx=10)
        self.lbl_radio_bank.grid(row=2, column=1, sticky="w", padx=10)
        self.lbl_radio_both.grid(row=3, column=1, sticky="w", padx=10)

        self.radio_group.grid(row=5, column=0, sticky="nsew", padx=10)

        # Logs
        self.log_frame = customtkinter.CTkFrame(self)
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=0)
        self.log_frame.grid_rowconfigure(1, weight=1)

        self.lbl_logs = customtkinter.CTkLabel(master=self.log_frame, text="Logs:")
        self.lbl_logs.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.txt_logs = tkinter.Text(
            master=self.log_frame,
            font=log_font(),
            bg="#343638",
            fg="#ffffff",
        )
        self.txt_logs.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.txt_logs.configure(state=tkinter.DISABLED)
        self.log_frame.grid(row=6, column=0, sticky="nsew", padx=10, pady=10)

    def on_closing(self):
        self.parent.destroy()

    def on_submit(self):
        search_string = self.search_entry.get()
        thread = threading.Thread(
            target=scraper.search_and_download,
            kwargs={"search_string": search_string, "image_type": self.radio_var.get(), "notify_callback": self.update_log},
            daemon=True,
        )
        self.search_entry.delete(0, "end")
        self.txt_logs.configure(state=tkinter.NORMAL)
        self.txt_logs.delete("1.0", "end")
        self.txt_logs.configure(state=tkinter.DISABLED)
        thread.start()

    def update_log(self, text: str):
        """
        Updates the log with the given text.
        """
        self.txt_logs.configure(state=tkinter.NORMAL)
        self.txt_logs.insert("end", "\n" + text)
        self.txt_logs.configure(state=tkinter.DISABLED)
        self.txt_logs.see(tkinter.END)
