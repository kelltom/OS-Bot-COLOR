import pathlib
import webbrowser as wb

import customtkinter
from PIL import Image, ImageTk
from utilities.osrs_wiki_sprite_scraper import OSRSWikiSpriteScraper

scraper = OSRSWikiSpriteScraper()

class TitleView(customtkinter.CTkFrame):
    def __init__(self, parent, main):
        super().__init__(parent)
        self.main = main
        self.search_window = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Spacing
        self.grid_rowconfigure(1, weight=0)  # - Logo
        self.grid_rowconfigure(2, weight=0)  # - Note
        self.grid_rowconfigure(3, weight=0)  # - Buttons
        self.grid_rowconfigure(4, weight=0)  # - Buttons
        self.grid_rowconfigure(5, weight=1)  # Spacing

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)


        # Logo
        self.logo_path = pathlib.Path(__file__).parent.parent.resolve()
        self.logo = ImageTk.PhotoImage(
            Image.open(f"{self.logo_path}/images/ui/logo.png").resize((411, 64)),
            Image.ANTIALIAS,
        )
        self.label_logo = customtkinter.CTkLabel(self, image=self.logo)
        self.label_logo.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=15, pady=15)

        # Description label
        self.note = "The universal OSRS color bot.\n Select a game in the left-side menu to begin."
        self.label_note = customtkinter.CTkLabel(master=self, text=self.note, text_font=("Roboto", 14))
        self.label_note.bind(
            "<Configure>",
            lambda e: self.label_note.configure(wraplength=self.label_note.winfo_width() - 20),
        )
        self.label_note.grid(row=2, column=0, columnspan=3, sticky="nwes", padx=15, pady=(0, 30))

        # Buttons
        IMG_SIZE = 24
        BTN_WIDTH, BTN_HEIGHT = (96, 64)
        DEFAULT_GRAY = ("gray50", "gray30")
        # -- Github
        self.github_logo = ImageTk.PhotoImage(
            Image.open(f"{self.logo_path}/images/ui/github32_w.png").resize((IMG_SIZE, IMG_SIZE)),
            Image.LANCZOS,
        )
        self.btn_github = customtkinter.CTkButton(
            master=self,
            text="GitHub",
            image=self.github_logo,
            width=BTN_WIDTH,
            height=BTN_HEIGHT,
            corner_radius=15,
            fg_color=DEFAULT_GRAY,
            compound="top",
            command=self.btn_github_clicked,
        )
        self.btn_github.grid(row=3, column=0, padx=15, pady=(15, 0), sticky="e")

        # -- Feedback
        self.feedback_logo = ImageTk.PhotoImage(
            Image.open(f"{self.logo_path}/images/ui/feedback_w.png").resize((IMG_SIZE, IMG_SIZE)),
            Image.LANCZOS,
        )
        self.btn_feedback = customtkinter.CTkButton(
            master=self,
            text="Feedback",
            image=self.feedback_logo,
            width=BTN_WIDTH,
            height=BTN_HEIGHT,
            corner_radius=15,
            fg_color=DEFAULT_GRAY,
            compound="top",
            command=self.btn_feedback_clicked,
        )
        self.btn_feedback.grid(row=3, column=1, padx=15, pady=(15, 0))


        # -- Bug Report
        self.bug_logo = ImageTk.PhotoImage(
            Image.open(f"{self.logo_path}/images/ui/bug-report_w.png").resize((IMG_SIZE, IMG_SIZE)),
            Image.LANCZOS,
        )
        self.btn_feedback = customtkinter.CTkButton(
            master=self,
            text="Report Bug",
            image=self.bug_logo,
            width=BTN_WIDTH,
            height=BTN_HEIGHT,
            corner_radius=15,
            fg_color=DEFAULT_GRAY,
            hover_color="#b36602",
            compound="top",
            command=self.btn_bug_report_clicked,
        )
        self.btn_feedback.grid(row=3, column=2, padx=15, pady=(15, 0), sticky="w")

        # -- Sprite Scraper
        self.wiki_logo = ImageTk.PhotoImage(
            Image.open(f"{self.logo_path}/images/ui/scraper.png").resize((IMG_SIZE, IMG_SIZE)),
            Image.LANCZOS,
        )
        self.btn_sprite_scraper = customtkinter.CTkButton(
            master=self,
            text="Sprite Scraper",
            image=self.wiki_logo,
            width=BTN_WIDTH,
            height=BTN_HEIGHT,
            corner_radius=15,
            fg_color=DEFAULT_GRAY,
            compound="top",
            command=self.btn_scraper_clicked,
        )
        self.btn_sprite_scraper.grid(row=5, column=1, padx=15, pady=(15, 0))
    
    def btn_github_clicked(self):
        wb.open_new_tab("https://github.com/kelltom/OSRS-Bot-COLOR")

    def btn_feedback_clicked(self):
        wb.open_new_tab("https://github.com/kelltom/OSRS-Bot-COLOR/discussions")


    def btn_bug_report_clicked(self):
        wb.open_new_tab("https://github.com/kelltom/OSRS-Bot-COLOR/issues/new/choose")
    
    def btn_scraper_clicked(self):
        if not self.search_window:
            self.search_window = customtkinter.CTkToplevel(self)
            self.search_window.title("OSRS Wiki Sprite Search")
            self.search_window.geometry(f"400x600")

            self.search_label = customtkinter.CTkLabel(
                self.search_window, 
                text="Search OSRS wiki for Sprites.", 
                text_font=("Roboto Medium", 12))
            self.search_label.pack()

            self.search_info = customtkinter.CTkLabel(
                self.search_window, 
                text="Supports multiple searchs by adding a ',' and another query")
            self.search_info.pack()

            self.search_entry = customtkinter.CTkEntry(self.search_window)
            self.search_entry.pack(
                padx=10,
                pady=10)

            self.search_submit_button = customtkinter.CTkButton(
                self.search_window, 
                text="Submit", 
                command=self.on_submit)
            self.search_submit_button.pack()

            self.bank_image_checkbox = customtkinter.CTkCheckBox(
                self.search_window,
                text="Bank and Sprite"
            )
            self.bank_image_checkbox.pack(pady=10)

            self.bank_only_checkbox = customtkinter.CTkCheckBox(
                self.search_window,
                text="Bank Only"
            )
            self.bank_only_checkbox.pack(pady=(10, 0))

            self.bank_only_warning = customtkinter.CTkLabel(
                self.search_window,
                text="This option will delete previously downloaded sprites of the same name",
                text_color="#FF0000",
                wraplength=250
            )
            self.bank_only_warning.pack(pady=(0, 10))

            self.search_log_label = customtkinter.CTkLabel(
                self.search_window,
                text="Logs:"
            )
            self.search_log_label.pack()

            self.search_feedback_label = customtkinter.CTkLabel(
                self.search_window, 
                text="")
            self.search_feedback_label.pack(
                padx=10,
                pady=10)

            self.search_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        else:
            self.search_window.lift()

    def on_closing(self):
        self.search_window.destroy()
        self.search_window = None

    def on_submit(self):
        search_input = self.search_entry.get()
        bank_checkbox_input = self.bank_image_checkbox.get()
        bank_only_checkbox_input = self.bank_only_checkbox.get()
        scraper.search_and_download(search_input, bank_checkbox_input, bank_only_checkbox_input)
        self.search_feedback_label.set_text("\n".join(scraper.logs))