import threading
import tkinter

import customtkinter

from utilities.osrs_wiki_sprite_scraper import OSRSWikiSpriteScraper

scraper = OSRSWikiSpriteScraper()


class SpriteScraperView(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Title
        self.search_label = customtkinter.CTkLabel(self, text="Search OSRS wiki for Sprites", text_font=("Roboto Medium", 12))
        self.search_label.pack(pady=(10, 0))

        # Search instructions
        self.search_info = customtkinter.CTkLabel(self, text="Enter item names separated by commas.")
        self.search_info.pack()

        # Search entry
        self.search_entry = customtkinter.CTkEntry(self)
        self.search_entry.pack(padx=10, pady=10)

        # Submit button
        self.search_submit_button = customtkinter.CTkButton(self, text="Submit", command=self.on_submit)
        self.search_submit_button.pack(pady=(0, 10))

        # Radio buttons
        self.radio_var = tkinter.IntVar(self)
        self.radio_normal = customtkinter.CTkRadioButton(master=self, text="Normal only", variable=self.radio_var, value=0)
        self.radio_bank = customtkinter.CTkRadioButton(master=self, text="Bank only    ", variable=self.radio_var, value=1)
        self.radio_normal_bank = customtkinter.CTkRadioButton(master=self, text="Both             ", variable=self.radio_var, value=2)
        self.radio_normal.pack(padx=10, pady=10)
        self.radio_bank.pack(padx=10, pady=10)
        self.radio_normal_bank.pack(padx=10, pady=10)

        # Logs
        self.lbl_logs = customtkinter.CTkLabel(self, text="Logs:")
        self.lbl_logs.pack(pady=(10, 0))

        self.txt_logs = tkinter.Text(
            self,
            font=("Roboto", 10),
            bg="#343638",
            fg="#ffffff",
        )
        self.txt_logs.pack(padx=10, pady=10)

    def on_closing(self):
        self.parent.destroy()

    def on_submit(self):
        search_input = self.search_entry.get()
        thread = threading.Thread(target=scraper.search_and_download, args=(search_input, self.radio_var.get(), self.update_log), daemon=True)
        thread.start()

    def update_log(self, text: str):
        """
        Updates the log with the given text.
        """
        self.txt_logs.configure(state=tkinter.NORMAL)
        self.txt_logs.insert("end", "\n" + text)
        self.txt_logs.configure(state=tkinter.DISABLED)
