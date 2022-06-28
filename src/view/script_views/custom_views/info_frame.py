import customtkinter
import pathlib
from PIL import Image, ImageTk
import tkinter


class InfoFrame(customtkinter.CTkFrame):
    def __init__(self, parent, title, info):
        '''
        Creates a 5x2 frame with the following widgets:
            - script title (label)
            - script description (label)
            - script progress bar (progressbar)
            - right-side controls title (label)
            - right-side control buttons (buttons)
        '''
        super().__init__(parent)

        PATH = pathlib.Path(__file__).parent.parent.parent.resolve()

        self.rowconfigure((0, 1, 2, 3, 4), weight=0)  # rows will not resize
        self.columnconfigure(0, weight=1, minsize=200)
        self.columnconfigure(1, weight=0)

        # -- script title
        self.lbl_script_title = customtkinter.CTkLabel(master=self,
                                                       text=title,
                                                       justify=tkinter.LEFT,
                                                       text_font=("default_theme", 12))
        self.lbl_script_title.grid(column=0, row=0, sticky="wns", padx=15, pady=15)

        # -- script description
        self.lbl_script_desc = customtkinter.CTkLabel(master=self,
                                                      text=info,
                                                      justify=tkinter.CENTER)
        self.lbl_script_desc.grid(column=0, row=1, rowspan=2, sticky="nwes", padx=15)
        self.lbl_script_desc.bind('<Configure>', lambda e: self.lbl_script_desc.config(wraplength=self.lbl_script_desc.winfo_width()-10))

        # -- script progress bar
        self.lbl_progress = customtkinter.CTkLabel(master=self,
                                                   text="Progress: 50%",
                                                   justify=tkinter.CENTER)
        self.lbl_progress.grid(row=3, column=0, sticky="ew")

        self.progressbar = customtkinter.CTkProgressBar(master=self)
        self.progressbar.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 15))

        # -- right-side control buttons
        # -- images
        img_size = 20
        img_play = ImageTk.PhotoImage(Image.open(f"{PATH}/images/play.png").resize((img_size, img_size)), Image.ANTIALIAS)
        img_pause = ImageTk.PhotoImage(Image.open(f"{PATH}/images/pause.png").resize((img_size, img_size)), Image.ANTIALIAS)
        img_stop = ImageTk.PhotoImage(Image.open(f"{PATH}/images/stop.png").resize((img_size, img_size)), Image.ANTIALIAS)

        self.lbl_controls_title = customtkinter.CTkLabel(master=self,
                                                         text="Controls",
                                                         justify=tkinter.LEFT,
                                                         text_font=("default_theme", 12))
        self.lbl_controls_title.grid(row=0, column=1, sticky="wns")

        self.btn_play = customtkinter.CTkButton(master=self,
                                                text="Play [F1]",
                                                image=img_play)
        self.btn_play.grid(row=1, column=1, pady=10, padx=20, sticky="n")

        self.btn_pause = customtkinter.CTkButton(master=self,
                                                 text="Pause [F2]",
                                                 image=img_pause)
        self.btn_pause.grid(row=2, column=1, pady=10, padx=20, sticky="n")

        self.btn_abort = customtkinter.CTkButton(master=self,
                                                 text="Stop [ESC]",
                                                 image=img_stop)
        self.btn_abort.grid(row=3, column=1, pady=10, padx=20, sticky="n")
