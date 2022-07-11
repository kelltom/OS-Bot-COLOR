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
                                                   text="Progress: 0%",
                                                   justify=tkinter.CENTER)
        self.lbl_progress.grid(row=3, column=0, sticky="ew")

        self.progressbar = customtkinter.CTkProgressBar(master=self)
        self.progressbar.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.progressbar.set(0)

        # -- right-side control buttons
        # -- images
        img_size = 18
        self.img_play = ImageTk.PhotoImage(Image.open(f"{PATH}/images/play.png").resize((img_size, img_size)), Image.ANTIALIAS)
        self.img_pause = ImageTk.PhotoImage(Image.open(f"{PATH}/images/pause.png").resize((img_size, img_size)), Image.ANTIALIAS)
        self.img_stop = ImageTk.PhotoImage(Image.open(f"{PATH}/images/stop2.png").resize((img_size, img_size)), Image.ANTIALIAS)
        self.img_options = ImageTk.PhotoImage(Image.open(f"{PATH}/images/options2.png").resize((img_size, img_size)), Image.ANTIALIAS)

        self.lbl_controls_title = customtkinter.CTkLabel(master=self,
                                                         text="Controls",
                                                         justify=tkinter.LEFT,
                                                         text_font=("default_theme", 12))
        self.lbl_controls_title.grid(row=0, column=1, sticky="wns")

        self.btn_play = customtkinter.CTkButton(master=self,
                                                text="Play",
                                                text_color="white",
                                                image=self.img_play,
                                                command=self.play_btn_clicked)
        self.btn_play.grid(row=1, column=1, pady=10, padx=20, sticky="nsew")

        self.btn_abort = customtkinter.CTkButton(master=self,
                                                 text="Stop [ESC]",
                                                 text_color="white",
                                                 fg_color="#910101",
                                                 hover_color="#690101",
                                                 image=self.img_stop,
                                                 command=self.stop_btn_clicked)
        self.btn_abort.grid(row=2, column=1, pady=10, padx=20, sticky="nsew")

        self.btn_options = customtkinter.CTkButton(master=self,
                                                   text="Options",
                                                   text_color="white",
                                                   fg_color="#d97b00",
                                                   hover_color="#b36602",
                                                   image=self.img_options,
                                                   command=self.options_btn_clicked)
        self.btn_options.grid(row=3, column=1, pady=10, padx=20, sticky="nsew")

        self.lbl_status = customtkinter.CTkLabel(master=self,
                                                 text="Status: Idle",
                                                 justify=tkinter.CENTER)
        self.lbl_status.grid(row=4, column=1, sticky="we")

        self.controller = None
        self.options_class = None

    def set_controller(self, controller):
        self.controller = controller

    def setup(self, title, description, options_class):
        self.lbl_script_title.config(text=title)
        self.lbl_script_desc.config(text=description)
        self.options_class = options_class

    def play_btn_clicked(self):
        self.controller.play_pause()

    def stop_btn_clicked(self):
        self.controller.stop()

    def options_btn_clicked(self):
        self.controller.options_btn_clicked()

    def on_options_closing(self, window):
        self.controller.abort_options()
        window.destroy()

    def show_options(self):
        '''
        Creates a new TopLevel view to display bot options.
        '''
        window = customtkinter.CTkToplevel(master=self)
        window.geometry("400x200")
        window.protocol("WM_DELETE_WINDOW", lambda arg=window: self.on_options_closing(arg))

        self.options_class(parent=window, controller=self.controller).pack(side="top", fill="both", expand=True, padx=40, pady=40)

    def update_status_running(self):
        self.__toggle_buttons(True)
        self.btn_options.config(state=tkinter.DISABLED)
        self.btn_play.config(image=self.img_pause)
        self.btn_play.config(text="Pause [F1]")
        self.lbl_status.config(text="Status: Running")

    def update_status_paused(self):
        self.__toggle_buttons(True)
        self.btn_options.config(state=tkinter.DISABLED)
        self.btn_play.config(image=self.img_play)
        self.btn_play.config(text="Play")
        self.lbl_status.config(text="Status: Paused")

    def update_status_stopped(self):
        self.__toggle_buttons(True)
        self.btn_play.config(image=self.img_play)
        self.btn_play.config(text="Play")
        self.lbl_status.config(text="Status: Stopped")

    def update_status_configuring(self):
        self.__toggle_buttons(False)
        self.lbl_status.config(text="Status: Configuring")

    def __toggle_buttons(self, enabled: bool):
        if enabled:
            self.btn_play.config(state=tkinter.NORMAL)
            self.btn_abort.config(state=tkinter.NORMAL)
            self.btn_options.config(state=tkinter.NORMAL)
        else:
            self.btn_play.config(state=tkinter.DISABLED)
            self.btn_abort.config(state=tkinter.DISABLED)
            self.btn_options.config(state=tkinter.DISABLED)

    def update_progress(self, progress):
        '''
        Called from controller. Updates the progress bar and percentage.
        Parameter progress is a float between 0 and 1.
        '''
        self.progressbar.set(progress)
        self.lbl_progress.config(text=f"Progress: {progress*100:.0f}%")
