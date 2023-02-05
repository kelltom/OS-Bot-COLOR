
import customtkinter
from utilities.osrs_wiki_sprite_scraper import OSRSWikiSpriteScraper
import tkinter

scraper = OSRSWikiSpriteScraper()

class SpriteScraperView(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.search_label = customtkinter.CTkLabel(self, text="Search OSRS wiki for Sprites.", text_font=("Roboto Medium", 12))
        self.search_label.pack()

        self.search_info = customtkinter.CTkLabel(self, text="Supports multiple searchs by adding a ',' and another query")
        self.search_info.pack()

        self.search_entry = customtkinter.CTkEntry(self)
        self.search_entry.pack(padx=10, pady=10)

        self.search_submit_button = customtkinter.CTkButton(self, text="Submit", command=self.on_submit)
        self.search_submit_button.pack()

        self.bank_image_checkbox = customtkinter.CTkCheckBox(self, text="Bank and Sprite")
        self.bank_image_checkbox.pack(pady=10)

        self.bank_only_checkbox = customtkinter.CTkCheckBox(self, text="Bank Only")
        self.bank_only_checkbox.pack(pady=(10, 0))

        self.bank_only_warning = customtkinter.CTkLabel(
            self, text="This option will delete previously downloaded sprites of the same name", text_color="#FF0000", wraplength=250
        )
        self.bank_only_warning.pack(pady=(0, 10))

        self.search_log_label = customtkinter.CTkLabel(self, text="Logs:")
        self.search_log_label.pack()

        self.search_feedback_label = tkinter.Text(
            self,
            font=("Roboto", 10),
            bg="#343638",
            fg="#ffffff",
        )
        self.search_feedback_label.pack(padx=10, pady=10)

    def on_closing(self):
        self.parent.destroy()

    def on_submit(self):
        if len(scraper.logs) >= 1:
            self.search_feedback_label.configure(state=tkinter.NORMAL)
            self.search_feedback_label.delete(1.0, tkinter.END)
            self.search_feedback_label.configure(state=tkinter.DISABLED)
        currentLogs = scraper.logs
        search_input = self.search_entry.get()
        bank_checkbox_input = self.bank_image_checkbox.get()
        bank_only_checkbox_input = self.bank_only_checkbox.get()
        scraper.search_and_download(search_input, bank_checkbox_input, bank_only_checkbox_input)
        self.search_feedback_label.configure(state=tkinter.NORMAL)
        for log in currentLogs:
            self.search_feedback_label.insert("end", "\n" + log)
        self.search_feedback_label.configure(state=tkinter.DISABLED)