'''
Should provide the view(s) to be returned to the main view.
Should also use the script1_controller.
'''

import customtkinter
import tkinter
# from PIL import Image, ImageTk  # <- import PIL for the images
import pathlib

PATH = pathlib.Path(__file__).parent.parent.resolve()


class CerberusView(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # configure grid layout (3x1)
        self.rowconfigure(0, weight=0)  # info row will not resize
        self.rowconfigure(1, weight=1)  # settings row will resize
        self.rowconfigure(2, weight=2)  # log row will resize but take more space
        self.columnconfigure(0, weight=1)
        # script log should resize, weight 1

        # ---------- TOP HALF (script info and control buttons) ----------
        # -- row-spanning frame
        self.frame_info = customtkinter.CTkFrame(master=self)
        self.frame_info.grid(row=0, column=0, pady=15, padx=15, sticky="nsew")

        self.frame_info.rowconfigure((0, 1, 2, 3, 4), weight=0)  # rows will not resize
        self.frame_info.columnconfigure(0, weight=1, minsize=200)
        self.frame_info.columnconfigure(1, weight=0)

        # -- script title
        self.lbl_script_title = customtkinter.CTkLabel(master=self.frame_info,
                                                       text="Cerberus Bot",
                                                       justify=tkinter.LEFT,
                                                       text_font=("default_theme", 12))
        self.lbl_script_title.grid(column=0, row=0, sticky="wns", padx=15, pady=15)

        # -- script description
        self.lbl_script_desc = customtkinter.CTkLabel(master=self.frame_info,
                                                      text="This is just me typing about the script and this text should wrap " +
                                                      "according to the length of the label. I'm just gonna keep typing to make " +
                                                      "this a really long label.",
                                                      # bg_color="gray38",
                                                      justify=tkinter.CENTER)
        self.lbl_script_desc.grid(column=0, row=1, rowspan=2, sticky="nwes", padx=15)
        self.lbl_script_desc.bind('<Configure>', lambda e: self.lbl_script_desc.config(wraplength=self.lbl_script_desc.winfo_width()-10))

        # -- script progress bar
        self.lbl_progress = customtkinter.CTkLabel(master=self.frame_info,
                                                   text="Progress: 50%",
                                                   justify=tkinter.CENTER)
        self.lbl_progress.grid(row=3, column=0, sticky="ew")

        self.progressbar = customtkinter.CTkProgressBar(master=self.frame_info)
        self.progressbar.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 15))

        # -- right-side control buttons
        self.radio_var = tkinter.IntVar(value=0)

        self.label_radio_group = customtkinter.CTkLabel(master=self.frame_info,
                                                        text="Controls",
                                                        justify=tkinter.LEFT,
                                                        text_font=("default_theme", 12))
        self.label_radio_group.grid(row=0, column=1, sticky="wns")

        self.radio_button_1 = customtkinter.CTkRadioButton(master=self.frame_info,
                                                           variable=self.radio_var,
                                                           value=0)
        self.radio_button_1.grid(row=1, column=1, pady=10, padx=20, sticky="n")

        self.radio_button_2 = customtkinter.CTkRadioButton(master=self.frame_info,
                                                           variable=self.radio_var,
                                                           value=1)
        self.radio_button_2.grid(row=2, column=1, pady=10, padx=20, sticky="n")

        self.radio_button_3 = customtkinter.CTkRadioButton(master=self.frame_info,
                                                           variable=self.radio_var,
                                                           value=1)
        self.radio_button_3.grid(row=3, column=1, pady=10, padx=20, sticky="n")

        # # ------- script configuration options -------
        # # -- script iterations
        # self.iteration_label = customtkinter.CTkLabel(master=self,
        #                                               text="Number of iterations:",
        #                                               justify=tkinter.LEFT)
        # self.iteration_label.grid(row=5, column=0, padx=15, pady=15)
        # self.iteration_select_frame = customtkinter.CTkFrame(master=self)
        # self.iteration_select_frame.columnconfigure((0, 2), weight=1)
        # self.iteration_select_frame.columnconfigure(1, weight=10)
        # self.iteration_select_frame.grid(row=5, column=1, padx=15, pady=15)
        # # ---- iterations manual entry
        # self.iterations_entry = customtkinter.CTkEntry(master=self.iteration_select_frame,
        #                                                width=40,
        #                                                placeholder_text="100")
        # self.iterations_entry.grid(row=0, column=1, sticky="we")
        # # ---- iterations increment/decrement buttons
        # image_size = 20
        # plus_image = ImageTk.PhotoImage(Image.open(f"{PATH}/images/plus.png").resize((image_size, image_size)))
        # minus_image = ImageTk.PhotoImage(Image.open(f"{PATH}/images/minus.png").resize((image_size, image_size)))
        # self.iteration_decrement_button = customtkinter.CTkButton(master=self.iteration_select_frame,
        #                                                           text="",
        #                                                           image=minus_image,
        #                                                           width=20,
        #                                                           fg_color=("gray75", "gray30"))
        # self.iteration_increment_button = customtkinter.CTkButton(master=self.iteration_select_frame,
        #                                                           text="",
        #                                                           image=plus_image,
        #                                                           width=20,
        #                                                           fg_color=("gray75", "gray30"))
        # self.iteration_decrement_button.grid(row=0, column=0)
        # self.iteration_increment_button.grid(row=0, column=2)
