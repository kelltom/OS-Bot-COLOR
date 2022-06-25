'''
Should provide the view(s) to be returned to the main view.
Should also use the script1_controller.
'''

import customtkinter
import tkinter
from PIL import Image, ImageTk  # <- import PIL for the images
import pathlib

PATH = pathlib.Path(__file__).parent.parent.resolve()


class CerberusView(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # configure grid layout (3x7)
        self.rowconfigure((0, 1, 2, 3, 4), weight=0)  # first 5 rows will not resize
        self.rowconfigure(7, weight=10)  # big spacing for row 7 (heavier weight means it'll use more extra space than other components)
        self.columnconfigure((0, 1), weight=1)  # first 2 cols will resize
        self.columnconfigure(2, weight=0)  # last column will remain the size required to fit its contents

        # ---------- LEFT SIDE ----------
        # ------- script info box -------
        self.frame_info = customtkinter.CTkFrame(master=self)
        self.frame_info.grid(row=0, column=0, columnspan=2, rowspan=5, pady=20, padx=20, sticky="nsew")

        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.columnconfigure(0, weight=1)

        # -- script info box text contents
        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
                                                   text="This is the Cerberus script,\n" +
                                                        "choose number of iterations\n" +
                                                        "and then press play.",
                                                   height=100,
                                                   fg_color=("white", "gray38"),  # <- custom tuple-color
                                                   justify=tkinter.LEFT)
        self.label_info_1.grid(column=0, columnspan=2, row=0, rowspan=3, sticky="nwes", padx=15, pady=15)

        # -- script info box progress bar
        self.progress_label = customtkinter.CTkLabel(master=self.frame_info,
                                                     text="Progress: [ratio here]",
                                                     justify=tkinter.CENTER)
        self.progress_label.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.progressbar = customtkinter.CTkProgressBar(master=self.frame_info)
        self.progressbar.grid(row=4, column=0, columnspan=2, sticky="ew", padx=15, pady=(5, 15))

        # ------- script configuration options -------
        # -- script iterations
        self.iteration_label = customtkinter.CTkLabel(master=self,
                                                      text="Number of iterations:",
                                                      justify=tkinter.LEFT)
        self.iteration_label.grid(row=5, column=0, padx=15, pady=15)
        self.iteration_select_frame = customtkinter.CTkFrame(master=self)
        self.iteration_select_frame.columnconfigure((0, 2), weight=1)
        self.iteration_select_frame.columnconfigure(1, weight=10)
        self.iteration_select_frame.grid(row=5, column=1, padx=15, pady=15)
        # ---- iterations manual entry
        self.iterations_entry = customtkinter.CTkEntry(master=self.iteration_select_frame,
                                                       width=40,
                                                       placeholder_text="100")
        self.iterations_entry.grid(row=0, column=1, sticky="we")
        # ---- iterations increment/decrement buttons
        image_size = 20
        plus_image = ImageTk.PhotoImage(Image.open(f"{PATH}/images/plus.png").resize((image_size, image_size)))
        minus_image = ImageTk.PhotoImage(Image.open(f"{PATH}/images/minus.png").resize((image_size, image_size)))
        self.iteration_decrement_button = customtkinter.CTkButton(master=self.iteration_select_frame,
                                                                  text="",
                                                                  image=minus_image,
                                                                  width=20,
                                                                  fg_color=("gray75", "gray30"))
        self.iteration_increment_button = customtkinter.CTkButton(master=self.iteration_select_frame,
                                                                  text="",
                                                                  image=plus_image,
                                                                  width=20,
                                                                  fg_color=("gray75", "gray30"))
        self.iteration_decrement_button.grid(row=0, column=0)
        self.iteration_increment_button.grid(row=0, column=2)

        # ---------- RIGHT SIDE ----------
        self.radio_var = tkinter.IntVar(value=0)

        self.label_radio_group = customtkinter.CTkLabel(master=self,
                                                        text="CTkRadioButton Group:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, pady=20, padx=10, sticky="")

        self.radio_button_1 = customtkinter.CTkRadioButton(master=self,
                                                           variable=self.radio_var,
                                                           value=0)
        self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")

        self.radio_button_2 = customtkinter.CTkRadioButton(master=self,
                                                           variable=self.radio_var,
                                                           value=1)
        self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")

        self.radio_button_3 = customtkinter.CTkRadioButton(master=self,
                                                           variable=self.radio_var,
                                                           value=2)
        self.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")
