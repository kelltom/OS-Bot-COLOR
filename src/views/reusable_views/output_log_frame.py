import customtkinter
import tkinter


class OutputLogFrame(customtkinter.CTkFrame):
    def __init__(self, parent):
        '''
        Creates a 2x1 frame with a text box for outputting log messages.
        '''
        super().__init__(parent)

        # configure grid layout (1x1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)  # log row will resize
        self.columnconfigure(0, weight=1)

        # Frame title
        self.lbl_title = customtkinter.CTkLabel(master=self,
                                                text="Script Log",
                                                justify=tkinter.LEFT,
                                                text_font=("default_theme", 12))
        self.lbl_title.grid(row=0, column=0, sticky="wns", padx=15, pady=15)

        # Text Box
        self.txt_log = tkinter.Text(master=self,
                                    wrap=tkinter.WORD,
                                    font=("Roboto", 10),
                                    bg="#343638",
                                    fg="#ffffff",
                                    padx=5,
                                    pady=5,
                                    spacing1=4,  # spacing before a line
                                    spacing3=4,  # spacing after a line / wrapped line
                                    cursor="arrow")
        self.txt_log.grid(row=1, column=0, padx=(15, 0), pady=(0, 15), sticky="nsew")
        # insert text
        self.txt_log.insert(tkinter.END, "This is just me typing about the script and this text should wrap. Lonnnnng line here :).\n")
        self.txt_log.insert(tkinter.END, "Here's another line.")
        self.txt_log.configure(state=tkinter.DISABLED)

        # Scrollbar
        self.scrollbar = customtkinter.CTkScrollbar(master=self,
                                                    command=self.txt_log.yview)
        self.scrollbar.grid(row=1, column=1, padx=(0, 15), pady=(0, 15), sticky="ns")

        # Connect textbox scroll event to scrollbar
        self.txt_log.configure(yscrollcommand=self.scrollbar.set)

        self.controller = None

    def set_controller(self, controller):
        self.controller = controller
